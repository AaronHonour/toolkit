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

### Architectural Modules
- **Dependency Injection**: Auto-wiring container with lifetime management (singleton, transient, scoped)
- **Application Lifecycle**: Startup/shutdown hooks, health checks (liveness/readiness), and graceful shutdown
- **Middleware Pipeline**: Request/response processing chain with built-in logging, metrics, and CORS middleware
- **Event Bus**: Pub/sub event system with async support and priority-based handlers
- **Repository Pattern**: Generic repository with Unit of Work for transaction management
- **Security**: JWT authentication, password hashing (bcrypt), and RBAC authorization
- **CLI Framework**: Command-line interface scaffolding with argument parsing
- **Testing Utilities**: Fixtures, mocks, and factory patterns for comprehensive testing

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

### Dependency Injection

```python
from toolkit.di import Container, Lifetime, singleton

# Create container
container = Container()

# Register services
container.register(UserService, lifetime=Lifetime.SINGLETON)
container.register(UserRepository, lifetime=Lifetime.SCOPED)

# Auto-wiring based on type hints
@singleton
class UserService:
    def __init__(self, repository: UserRepository, cache: CacheManager):
        self.repository = repository
        self.cache = cache

# Resolve dependencies
service = container.resolve(UserService)
```

### Application Lifecycle

```python
from toolkit.lifecycle import Application

# Create application
app = Application(name="my-app")

# Register startup/shutdown hooks
@app.on_startup
async def startup():
    print("Application starting...")
    await database.connect()

@app.on_shutdown
async def shutdown():
    print("Application shutting down...")
    await database.disconnect()

# Register health checks
@app.health_check(check_type="readiness")
def database_health():
    return database.is_connected()

# Start application
await app.start()
health = app.get_health_status()
await app.stop()
```

### Middleware Pipeline

```python
from toolkit.middleware import MiddlewarePipeline, LoggingMiddleware, MetricsMiddleware

# Create pipeline
pipeline = MiddlewarePipeline()

# Add middleware (order matters!)
pipeline.use(LoggingMiddleware(logger))
pipeline.use(MetricsMiddleware(metrics))

# Custom middleware
class AuthMiddleware:
    async def process(self, request, next_handler):
        # Authentication logic
        if not request.headers.get("Authorization"):
            return Response(status_code=401)
        return await next_handler(request)

pipeline.use(AuthMiddleware())

# Execute pipeline
response = await pipeline.execute(request)
```

### Event Bus

```python
from toolkit.events import EventBus, Event
from dataclasses import dataclass

# Create event bus
event_bus = EventBus()

# Define events
@dataclass
class UserCreatedEvent(Event):
    user_id: int
    email: str

# Subscribe to events
@event_bus.subscribe(UserCreatedEvent)
async def send_welcome_email(event: UserCreatedEvent):
    print(f"Sending email to {event.email}")

@event_bus.subscribe(UserCreatedEvent)
async def log_user_creation(event: UserCreatedEvent):
    logger.info(f"User {event.user_id} created")

# Publish events
await event_bus.publish(UserCreatedEvent(user_id=123, email="test@example.com"))
```

### Repository Pattern

```python
from toolkit.repository import Repository, UnitOfWork

# Define repository
class UserRepository(Repository[User]):
    async def find_by_email(self, email: str):
        return await self.find_one(email=email)

# Use with Unit of Work
async with UnitOfWork() as uow:
    user_repo = uow.get_repository(UserRepository)

    user = User(email="test@example.com", name="John")
    user = await user_repo.add(user)

    await uow.commit()  # Transaction committed
```

### Security

```python
from toolkit.security import JWT, PasswordHasher, RBAC

# JWT authentication
jwt = JWT(secret="my-secret-key")
token = jwt.encode({"user_id": 123}, expires_in=3600)
payload = jwt.decode(token)

# Password hashing
hasher = PasswordHasher()
password_hash = hasher.hash("SecurePassword123!")
is_valid = hasher.verify("SecurePassword123!", password_hash)

# RBAC authorization
rbac = RBAC()
rbac.define_role("admin", ["*"])
rbac.define_role("user", ["posts:read", "posts:create"])
rbac.assign_role("user:123", "admin")

if rbac.has_permission("user:123", "posts:delete"):
    delete_post()
```

### CLI Framework

```python
from toolkit.cli import CLI

# Create CLI application
cli = CLI(name="myapp", version="1.0.0")

@cli.command()
def hello(name: str, greeting: str = "Hello"):
    """Greet someone."""
    print(f"{greeting}, {name}!")

@cli.command()
def deploy(env: str, dry_run: bool = False):
    """Deploy application."""
    if dry_run:
        print(f"Would deploy to {env}")
    else:
        print(f"Deploying to {env}...")

# Run CLI
cli.run()
```

### Testing Utilities

```python
from toolkit.testing import TestFixtures, MockFactory, DataFactory

# Create test fixtures
fixtures = TestFixtures()

@fixtures.fixture
def database():
    db = Database.connect()
    yield db
    db.close()

# Create mocks
mocks = MockFactory()
mock_cache = mocks.create_mock(CacheManager)
mock_cache.get.return_value = {"user": "data"}

# Create test data factories
user_factory = DataFactory.create(User)
user = user_factory.build(email="test@example.com")
users = user_factory.batch(10)
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
│   ├── env/             # Environment management
│   ├── metrics/         # Metrics collection
│   ├── cache/           # Caching system
│   ├── http/            # HTTP client
│   ├── validation/      # Data validation
│   ├── ratelimit/       # Rate limiting
│   ├── resilience/      # Resilience patterns
│   ├── di/              # Dependency injection
│   ├── lifecycle/       # Application lifecycle
│   ├── middleware/      # Middleware pipeline
│   ├── events/          # Event bus
│   ├── repository/      # Repository pattern
│   ├── security/        # Security utilities
│   ├── cli/             # CLI framework
│   └── testing/         # Testing utilities
├── configs/             # Example configurations
├── tests/               # Comprehensive tests
└── examples/            # Usage examples
```

## Configuration Files

All modules are configured via YAML files in the `configs/` directory:

**Core Configuration:**
- `config.yaml` - Application configuration
- `logging.yaml` - Logging setup
- `errors.yaml` - Error handling rules
- `env.yaml` - Environment variables

**Extended Configuration:**
- `metrics.yaml` - Metrics backends and collection
- `cache.yaml` - Cache backends and TTL settings
- `http.yaml` - HTTP client timeouts and retries
- `validation.yaml` - Validation rules
- `ratelimit.yaml` - Rate limiting strategies
- `resilience.yaml` - Circuit breaker and fallback settings

**Architectural Configuration:**
- `di.yaml` - Dependency injection container setup
- `lifecycle.yaml` - Application lifecycle hooks
- `middleware.yaml` - Middleware pipeline configuration
- `events.yaml` - Event bus and handlers
- `security.yaml` - JWT, RBAC, and password policies

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
