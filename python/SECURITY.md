# Security Improvements & Best Practices

This document details the security improvements made to the unistax backend and provides best practices for secure usage.

## Recent Security Fixes

### 1. Password Hashing (CRITICAL FIX)

**Issue:** Previously used SHA256 for password hashing, which is vulnerable to brute-force attacks.

**Fix:** Migrated to bcrypt with configurable work factor.

**File:** `python/src/unistax/security/password.py`

**Changes:**
- ✅ Replaced SHA256 with bcrypt (industry standard)
- ✅ Added automatic salting (bcrypt built-in)
- ✅ Configurable work factor (default: 12 rounds ~300ms)
- ✅ Timing-attack resistant verification
- ✅ Secure fallback with warnings if bcrypt unavailable

**Usage:**
```python
from unistax.security.password import PasswordHasher

# Create hasher with default settings (12 rounds)
hasher = PasswordHasher()

# Hash a password
hashed = hasher.hash("user-password")
# Returns: $2b$12$xxxxx... (bcrypt format)

# Verify password
is_valid = hasher.verify("user-password", hashed)  # True

# Increase work factor for high-security scenarios
secure_hasher = PasswordHasher(rounds=14)  # ~1.2 seconds per hash
```

**Security Notes:**
- Default 12 rounds provides good security/performance balance
- Increase rounds as hardware improves (add 1 every ~18 months)
- Never use rounds < 10 in production
- bcrypt automatically handles salting and timing attacks

**Migration from SHA256:**
```python
# Old hashes will still verify correctly using fallback
# Detect old format and re-hash on next login:

if hasher.verify(password, old_hash):
    if old_hash.startswith("sha256$"):
        # Re-hash with bcrypt
        new_hash = hasher.hash(password)
        # Update database with new_hash
```

---

### 2. SQL Injection Prevention (CRITICAL FIX)

**Issue:** Query builder allowed arbitrary attribute access via `getattr()`, enabling SQL injection and code execution.

**Fix:** Comprehensive input validation and whitelisting.

**File:** `python/src/unistax/query/builder.py`

**Changes:**
- ✅ Field name validation (alphanumeric + underscore only)
- ✅ Operator whitelist (prevents SQL injection)
- ✅ Column existence validation against model
- ✅ Blocked access to private attributes (`__xxx__`)
- ✅ Pagination parameter validation
- ✅ Sort direction validation

**Security Features:**

1. **Field Name Validation:**
```python
# Blocks dangerous inputs
query.where("__class__", "eq", "value")  # ❌ ValueError
query.where("_private", "eq", "value")    # ❌ ValueError
query.where("user'; DROP TABLE--", "eq", "x")  # ❌ ValueError
query.where("user_id", "eq", 123)        # ✅ Valid
```

2. **Operator Whitelist:**
```python
# Only safe operators allowed
ALLOWED_OPERATORS = {
    "eq", "ne", "gt", "gte", "lt", "lte",
    "in", "not_in", "like", "ilike"
}

query.where("email", "DROP", "x")  # ❌ ValueError
query.where("email", "eq", "test@example.com")  # ✅ Valid
```

3. **Column Validation:**
```python
# Only actual model columns can be queried
query.where("nonexistent_field", "eq", "x")  # ❌ ValueError
# Checks against model.__table__.columns
```

**Usage:**
```python
from unistax.query.builder import QueryBuilder

# Safe query building
query = (QueryBuilder()
    .where("user_id", "eq", 123)          # ✅ Validated
    .where("status", "in", ["active"])    # ✅ Safe
    .order_by("created_at", "desc")       # ✅ Validated
    .limit(100)                           # ✅ Range checked
    .offset(0))                           # ✅ Non-negative

# Apply to SQLAlchemy query
results = query.apply_to_sqlalchemy(db_query, UserModel)
```

---

### 3. Security Headers Implementation (FEATURE ADDED)

**Feature:** Added comprehensive OWASP-recommended security headers middleware.

**File:** `python/src/unistax/middleware/builtin.py`

**Changes:**
- ✅ Added SecurityHeadersMiddleware with configurable headers
- ✅ Content-Security-Policy (CSP) with restrictive defaults
- ✅ HTTP Strict Transport Security (HSTS)
- ✅ X-Frame-Options (clickjacking protection)
- ✅ X-Content-Type-Options (MIME sniffing protection)
- ✅ Referrer-Policy
- ✅ Permissions-Policy (feature policy)
- ✅ X-XSS-Protection (legacy browser support)

**Security Headers Included:**

1. **Content-Security-Policy (CSP)**
   - Prevents XSS, data injection, and code execution attacks
   - Default: Restrictive policy allowing only same-origin resources
   - Customizable per application needs

2. **Strict-Transport-Security (HSTS)**
   - Forces HTTPS connections
   - Default: 1 year max-age with includeSubDomains
   - Prevents man-in-the-middle attacks

3. **X-Frame-Options**
   - Prevents clickjacking attacks
   - Default: DENY (no framing allowed)
   - Can be set to SAMEORIGIN if needed

4. **X-Content-Type-Options**
   - Prevents MIME type sniffing
   - Default: nosniff

5. **Referrer-Policy**
   - Controls referrer information leakage
   - Default: strict-origin-when-cross-origin

6. **Permissions-Policy**
   - Disables sensitive browser features
   - Default: Disables geolocation, camera, microphone, etc.

**Usage:**

```python
from unistax.middleware import SecurityHeadersMiddleware, MiddlewarePipeline

# Production configuration with custom CSP
security = SecurityHeadersMiddleware(
    content_security_policy=(
        "default-src 'self'; "
        "script-src 'self' https://cdn.example.com; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:; "
        "font-src 'self' data:; "
        "connect-src 'self' https://api.example.com; "
        "frame-ancestors 'none'; "
        "base-uri 'self'; "
        "form-action 'self'"
    ),
    strict_transport_security="max-age=63072000; includeSubDomains; preload",
    x_frame_options="DENY",
)

# Add to middleware pipeline
pipeline = MiddlewarePipeline()
pipeline.use(security)
```

**Development Configuration:**

```python
# More permissive for local development
security = SecurityHeadersMiddleware(
    content_security_policy=(
        "default-src 'self' 'unsafe-inline' 'unsafe-eval'; "
        "img-src 'self' data: https:; "
        "connect-src 'self' ws: wss:"  # Allow WebSocket for hot reload
    ),
    strict_transport_security=None,  # Disable HSTS for HTTP dev server
)
```

**Testing Your Security Headers:**

Use these tools to validate your configuration:
- [https://securityheaders.com/](https://securityheaders.com/)
- [https://observatory.mozilla.org/](https://observatory.mozilla.org/)

**CSP Testing:**

Start with CSP in report-only mode to test without blocking:
```python
security = SecurityHeadersMiddleware(
    custom_headers={
        "Content-Security-Policy-Report-Only": "default-src 'self'; report-uri /csp-report"
    }
)
```

**Security Notes:**
- Customize CSP based on your application's resource loading needs
- Only enable HSTS over HTTPS (causes errors on HTTP)
- Test thoroughly before deploying to production
- Use security scanners to validate configuration
- Consider adding CSP reporting endpoint for violations

---

## Remaining Security Concerns

### HIGH PRIORITY (Requires Immediate Action)

#### 1. Custom JWT Implementation ✅ FIXED

**Status:** IMPLEMENTED - Using industry-standard PyJWT library.

**File:** `python/src/unistax/security/jwt.py`

The JWT implementation has been completely rewritten to use PyJWT, addressing all security concerns:

**Security Improvements:**
- ✅ Industry-standard PyJWT library (battle-tested, actively maintained)
- ✅ Support for multiple algorithms (HS256/384/512, RS256/384/512, ES256/384/512)
- ✅ Algorithm verification (prevents algorithm confusion attacks)
- ✅ Expiration (exp) claim validation
- ✅ Not-before (nbf) claim validation
- ✅ Issued-at (iat) claim validation
- ✅ Audience (aud) claim validation
- ✅ Issuer (iss) claim validation
- ✅ Proper error handling with specific exception types
- ✅ Secret strength validation (warns if too weak)
- ✅ Clock skew handling (configurable leeway)
- ✅ Comprehensive logging for security events

**New Exception Types:**
- `JWTError` - Base exception
- `JWTDecodeError` - Invalid token format
- `JWTExpiredError` - Token expired
- `JWTInvalidSignatureError` - Signature verification failed
- `JWTInvalidAudienceError` - Audience validation failed
- `JWTInvalidIssuerError` - Issuer validation failed

**Usage:**
```python
from unistax.security import JWT, JWTExpiredError, JWTInvalidSignatureError

# Basic usage with HS256
jwt_manager = JWT(
    secret="your-strong-256-bit-secret-key-here",
    algorithm="HS256",
    expiration=3600  # 1 hour
)

# Encode token
token = jwt_manager.encode({"user_id": 123, "role": "admin"})

# Decode and verify token
try:
    claims = jwt_manager.decode(token)
    user_id = claims["user_id"]
except JWTExpiredError:
    # Handle expired token - require re-authentication
    pass
except JWTInvalidSignatureError:
    # Handle forged token - log security incident!
    pass

# With audience and issuer validation (recommended)
jwt_manager = JWT(
    secret="your-secret",
    algorithm="HS256",
    audience="myapp",
    issuer="auth-service",
    expiration=1800  # 30 minutes
)
token = jwt_manager.encode({"user_id": 123})
claims = jwt_manager.decode(token)  # Validates aud and iss

# Using RS256 with public/private keys (recommended for distributed systems)
with open("private_key.pem") as f:
    private_key = f.read()
with open("public_key.pem") as f:
    public_key = f.read()

jwt_manager = JWT(
    secret=private_key,
    public_key=public_key,
    algorithm="RS256"
)
token = jwt_manager.encode({"user_id": 123})
claims = jwt_manager.decode(token)
```

**Security Best Practices:**
- Use secrets of at least 256 bits (32 characters) for HS256
- Use RS256 or ES256 for public/private key scenarios
- Set expiration times as short as practical (15-60 minutes)
- Always validate audience and issuer in production
- Never disable signature verification
- Implement token refresh mechanism for long-lived sessions
- Consider token revocation for sensitive operations (use Redis/database)

See documentation in `python/src/unistax/security/jwt.py` for more details.

#### 2. Authorization Bypass ✅ FIXED

**Status:** FIXED - See "Recent Security Fixes" section above.

RBAC authorization is now properly enforced. See commit "security: implement RBAC, fix CORS, and improve error handling" for details.

#### 3. Insecure CORS Configuration ✅ FIXED

**Status:** FIXED - See "Recent Security Fixes" section above.

CORS now requires explicit origin configuration. See commit "security: implement RBAC, fix CORS, and improve error handling" for details.

#### 4. No Rate Limiting on Auth Endpoints
**Impact:** Brute force attacks possible

**Fix:**
```python
from unistax.ratelimit.limiter import RateLimiter

limiter = RateLimiter(max_requests=5, window_seconds=300)  # 5 per 5 minutes

@app.post("/login")
@limiter.limit(key_func=lambda req: req.client.host)
async def login(credentials: LoginRequest):
    # Limit login attempts per IP
    pass
```

---

### MEDIUM PRIORITY

#### 1. No CSRF Protection
Add CSRF tokens for state-changing operations:
```python
from fastapi_csrf_protect import CsrfProtect

@app.post("/api/update")
async def update(csrf_protect: CsrfProtect = Depends()):
    await csrf_protect.validate_csrf(request)
    # Process update
```

#### 2. Missing Security Headers ✅ FIXED

**Status:** IMPLEMENTED - See "Recent Security Fixes" section #3 above.

The SecurityHeadersMiddleware is now available with comprehensive OWASP-recommended headers:
- Content-Security-Policy (CSP)
- Strict-Transport-Security (HSTS)
- X-Frame-Options
- X-Content-Type-Options
- Referrer-Policy
- Permissions-Policy
- X-XSS-Protection

Usage:
```python
from unistax.middleware import SecurityHeadersMiddleware

security = SecurityHeadersMiddleware()  # Uses secure defaults
# Add to your middleware pipeline
```

See documentation above for complete usage examples and configuration options.

#### 3. Secrets Management
Never store secrets in code or config files:

```python
# BAD
database_url = "postgresql://user:password@localhost/db"

# GOOD
import os
database_url = os.environ["DATABASE_URL"]

# BETTER - Use secrets manager
from cloud_secrets import get_secret
database_url = get_secret("production/database/url")
```

---

## Security Best Practices

### 1. Input Validation

Always validate user input:
```python
from unistax.validation.validators import Validator

validator = Validator()
validator.add_rule("email", "email")
validator.add_rule("age", "min", 18)
validator.add_rule("age", "max", 120)

if not validator.validate(user_data):
    raise ValueError(validator.errors)
```

### 2. Parameterized Queries

Never concatenate SQL:
```python
# BAD
query = f"SELECT * FROM users WHERE id = {user_id}"

# GOOD
query = "SELECT * FROM users WHERE id = :id"
result = session.execute(text(query), {"id": user_id})
```

### 3. Error Handling

Don't leak sensitive information in errors:
```python
# BAD
except Exception as e:
    return {"error": str(e)}  # Leaks stack trace!

# GOOD
except Exception as e:
    logger.error(f"Database error: {e}", exc_info=True)
    return {"error": "An error occurred. Please try again."}
```

### 4. Authentication Best Practices

```python
# Use secure session management
from unistax.security.sessions import SecureSessionManager

session_manager = SecureSessionManager(
    secret_key=os.environ["SESSION_SECRET"],
    secure=True,  # HTTPS only
    httponly=True,  # No JavaScript access
    samesite="strict"  # CSRF protection
)
```

### 5. Audit Logging

Log security events:
```python
from unistax.audit.logger import AuditLogger

audit = AuditLogger()

# Log authentication events
audit.log_event("user.login", user_id=user.id, ip=request.client.host)
audit.log_event("user.login.failed", username=username, ip=request.client.host)

# Log data access
audit.log_event("data.access", resource="user", action="read", user_id=user.id)
```

---

## Security Checklist for Production

- [ ] Enable bcrypt for password hashing (`pip install bcrypt`)
- [ ] Replace custom JWT with PyJWT library
- [ ] Implement RBAC decorator properly
- [ ] Configure CORS with specific origins
- [ ] Add rate limiting to authentication endpoints
- [ ] Enable CSRF protection
- [ ] Add security headers
- [ ] Move secrets to environment variables or secrets manager
- [ ] Enable HTTPS/TLS
- [ ] Set up audit logging
- [ ] Configure session security (httponly, secure, samesite)
- [ ] Implement input validation on all endpoints
- [ ] Use parameterized queries everywhere
- [ ] Set up monitoring and alerting for security events
- [ ] Regular dependency updates (`pip-audit`)
- [ ] Penetration testing
- [ ] Code review for security issues

---

## Incident Response

If you discover a security vulnerability:

1. **Don't** disclose publicly until patched
2. Email security concerns to: [security contact]
3. Include:
   - Description of vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

---

## Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/)
- [CWE Top 25](https://cwe.mitre.org/top25/)
- [Python Security Best Practices](https://python.readthedocs.io/en/latest/library/security_warnings.html)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)

---

## Changelog

### 2024-11-13
- ✅ Migrated password hashing from SHA256 to bcrypt
- ✅ Added comprehensive SQL injection prevention
- ✅ Added input validation to query builder
- ✅ Implemented RBAC authorization (fixed bypass vulnerability)
- ✅ Added security context management (thread-safe user context)
- ✅ Fixed CORS configuration security (removed wildcard default)
- ✅ Improved error handling with proper logging
- ✅ Implemented SecurityHeadersMiddleware with OWASP headers
- ✅ Added CSP, HSTS, X-Frame-Options, and other security headers
- ✅ Replaced custom JWT with industry-standard PyJWT library
- ✅ Added comprehensive JWT claim validation (exp, nbf, iat, aud, iss)
- ✅ Added algorithm verification (prevents algorithm confusion attacks)
- ✅ Added support for RS256, ES256, and other secure algorithms
- ✅ Added specific JWT exception types for better error handling
- ✅ Added secret strength validation
- ✅ Documented remaining security concerns
- ✅ Created security best practices guide
