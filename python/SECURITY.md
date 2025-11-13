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

## Remaining Security Concerns

### HIGH PRIORITY (Requires Immediate Action)

#### 1. Custom JWT Implementation
**File:** `python/src/unistax/security/jwt.py`

**Issues:**
- No algorithm verification
- Timing attack vulnerabilities
- Missing "nbf", "iss", "aud" validation
- No token revocation support

**Recommendation:**
```bash
# Use PyJWT library (already in dependencies)
pip install pyjwt

# Replace custom implementation
import jwt

# Encode
token = jwt.encode({"user_id": 123}, "secret", algorithm="HS256")

# Decode with validation
try:
    payload = jwt.decode(token, "secret", algorithms=["HS256"])
except jwt.InvalidTokenError:
    # Handle invalid token
    pass
```

#### 2. Authorization Bypass
**File:** `python/src/unistax/security/rbac.py:85-91`

**Issue:** RBAC decorator is commented out - ALL requests pass through!

```python
# CURRENT CODE (INSECURE!)
async def wrapper(*args: Any, **kwargs: Any) -> Any:
    # In production, get user role from context/request
    # user_role = get_current_user_role()
    # if not self.has_permission(user_role, permission):
    #     raise PermissionDenied()

    return await func(*args, **kwargs)  # Always allows!
```

**Fix Required:**
```python
async def wrapper(*args: Any, **kwargs: Any) -> Any:
    user_role = get_current_user_role()  # Implement this!
    if not self.has_permission(user_role, permission):
        raise PermissionDenied(f"Role {user_role} lacks permission {permission}")
    return await func(*args, **kwargs)
```

#### 3. Insecure CORS Configuration
**Files:**
- `python/src/unistax/api/app.py:118`
- `python/src/unistax/middleware/builtin.py:184`

**Issue:** Default CORS allows all origins (`["*"]`)

**Fix:**
```python
# In production, specify exact origins
app = create_app(
    cors_origins=[
        "https://yourdomain.com",
        "https://app.yourdomain.com"
    ],
    cors_allow_credentials=True
)
```

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

#### 2. Missing Security Headers
Add to FastAPI app:
```python
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.cors import CORSMiddleware

app.add_middleware(TrustedHostMiddleware, allowed_hosts=["yourdomain.com"])

# Add security headers
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response
```

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
- ✅ Documented remaining security concerns
- ✅ Created security best practices guide
