# Backend Toolkit

Enterprise-grade Python toolkit for backend development with a focus on composability, performance, and configuration-driven architecture.

## Features

### Core Modules
- **Configuration Management**: YAML-driven configuration with validation, environment variable interpolation, and hot-reloading
- **Advanced Logging**: Structured logging with multiple handlers, formatters, and filters
- **Error Handling**: Comprehensive error system with custom exceptions, error codes, and handlers
- **Environment Management**: Multi-environment support with validation and type-safe access

### Extended Modules
- **Metrics Collection**: Prometheus, StatsD, and in-memory backends with decorators and auto-instrumentation
- **Caching**: Redis, Memcached, and in-memory caching with TTL, compression, and memoization decorators
- **HTTP Client**: Enterprise HTTP client with retries, circuit breaker, and connection pooling
- **Validation**: Data validation with pre-built rules and custom validators
- **Rate Limiting**: Token bucket and sliding window algorithms with Redis support
- **Resilience**: Circuit breaker, fallback, and bulkhead patterns for fault tolerance

## Installation

```bash
pip install -e .
```

For development:
```bash
pip install -e ".[dev]"
```

With optional features:
```bash
pip install -e ".[http]"      # HTTP client support
pip install -e ".[cache]"     # Redis/Memcached support
pip install -e ".[metrics]"   # Prometheus/StatsD support
pip install -e ".[all]"       # All optional features
```

## Quick Start

### Configuration Management

```python
from toolkit.config import ConfigManager

# Load from YAML
config = ConfigManager.from_yaml("configs/config.yaml")

# Access nested values
db_host = config.get("database.host", default="localhost")

# Type-safe access
db_port = config.get_int("database.port", default=5432)
```

### Logging

```python
from toolkit.logging import LoggerFactory

# Create logger from config
logger = LoggerFactory.from_yaml("configs/logging.yaml")

# Use structured logging
logger.info("User login", extra={"user_id": 123, "ip": "192.168.1.1"})
```

### Error Handling

```python
from toolkit.errors import ApplicationError, ErrorCode

# Define custom errors
class DatabaseError(ApplicationError):
    code = ErrorCode.DATABASE_ERROR

# Use in code
try:
    # ... database operation
    raise DatabaseError("Connection failed", details={"host": "localhost"})
except ApplicationError as e:
    logger.error(f"Error: {e.code} - {e.message}", extra=e.details)
```

### Environment Management

```python
from toolkit.env import EnvManager

# Load environment configuration
env = EnvManager.from_yaml("configs/env.yaml")

# Access with validation
api_key = env.require("API_KEY")  # Raises if missing
debug_mode = env.get_bool("DEBUG", default=False)
```

### Metrics Collection

```python
from toolkit.metrics import MetricsManager

# Create metrics manager
metrics = MetricsManager(backend="prometheus")

# Track metrics
metrics.counter("requests.total", labels={"endpoint": "/api/users"})
metrics.gauge("queue.size", 42)

# Time operations
with metrics.timer("db.query.duration"):
    # Timed operation
    pass
```

### Caching

```python
from toolkit.cache import CacheManager

# Create cache manager
cache = CacheManager(backend="redis")

# Cache operations
cache.set("user:123", user_data, ttl=3600)
user = cache.get("user:123")

# Memoization decorator
@cache.memoize(ttl=3600, key_prefix="user")
def get_user(user_id):
    return db.query(user_id)
```

### HTTP Client

```python
from toolkit.http import HTTPClient

# Create HTTP client
client = HTTPClient(base_url="https://api.example.com")

# Make requests with auto-retry
response = client.get("/users")
response = client.post("/users", json_data={"name": "John"})
```

### Validation

```python
from toolkit.validation import Validator, ValidationRules

# Create validator
validator = Validator()
validator.add_rule("email", ValidationRules.email)
validator.add_rule("username", lambda x: len(x) >= 3)

# Validate data
is_valid = validator.validate({"email": "test@example.com", "username": "john"})
```

### Rate Limiting

```python
from toolkit.ratelimit import RateLimiter

# Create rate limiter
limiter = RateLimiter(rate=100, period=60)  # 100 requests per minute

# Check if allowed
if limiter.is_allowed("user:123"):
    process_request()

# Decorator
@limiter.limit(key_func=lambda user_id: f"user:{user_id}")
def api_endpoint(user_id):
    pass
```

### Resilience

```python
from toolkit.resilience import CircuitBreaker, Fallback

# Circuit breaker
breaker = CircuitBreaker(failure_threshold=5, timeout=60)

@breaker.protected(fallback=lambda: {"status": "unavailable"})
def call_external_service():
    return requests.get("https://api.example.com")

# Fallback
fallback = Fallback(default_value=[])

@fallback.with_fallback()
def get_recommendations(user_id):
    return ml_service.get_recommendations(user_id)
```

## Architecture

The toolkit follows SOLID principles and emphasizes:

- **Composability**: Each module works independently or together
- **Configuration-driven**: Everything configurable via YAML
- **Performance**: Lazy loading, caching, minimal overhead
- **Type Safety**: Full type hints and runtime validation
- **Enterprise-ready**: Thread-safe, production-tested patterns

## Project Structure

```
toolkit/
├── src/toolkit/          # Main package
│   ├── config/          # Configuration management
│   ├── logging/         # Logging system
│   ├── errors/          # Error handling
│   └── env/             # Environment management
├── configs/             # Example configurations
├── tests/               # Comprehensive tests
└── examples/            # Usage examples
```

## Configuration Files

All modules are configured via YAML files in the `configs/` directory:

- `config.yaml` - Application configuration
- `logging.yaml` - Logging setup
- `errors.yaml` - Error handling rules
- `env.yaml` - Environment variables

## Development

Run tests:
```bash
pytest
```

Format code:
```bash
black src/ tests/
ruff check src/ tests/
```

Type checking:
```bash
mypy src/
```

## License

MIT
