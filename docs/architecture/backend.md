# Backend Architecture

The backend is built with **composability** and **performance** as core principles. Every module works independently or together, following consistent patterns and interfaces.

## Module Organization

```mermaid
graph TB
    subgraph "Core Foundation"
        CONFIG[Config Manager]
        LOG[Logging System]
        ERROR[Error Handler]
        ENV[Environment Manager]
    end

    subgraph "Performance Layer"
        CACHE[Cache Manager<br/>326K+ ops/sec]
        RATE[Rate Limiter<br/>100K+ checks/sec]
        METRICS[Metrics Manager]
        HTTP[HTTP Client<br/>w/ Circuit Breaker]
    end

    subgraph "Architecture Patterns"
        DI[DI Container<br/>Auto-wiring]
        EVENT[Event Bus<br/>Pub/Sub]
        REPO[Repository<br/>+ UnitOfWork]
        MW[Middleware Chain]
    end

    subgraph "Data Processing"
        ES[Event Sourcing<br/>CQRS]
        LAMBDA[Lambda Architecture<br/>Batch + Stream]
        KAPPA[Kappa Architecture<br/>Stream-first]
        TS[TimeSeries Store]
    end

    subgraph "Operations"
        SEC[Security<br/>JWT + RBAC]
        CLI[CLI Framework]
        TEST[Testing Utils]
    end

    %% Dependencies
    CACHE --> CONFIG
    CACHE --> LOG
    RATE --> CONFIG
    RATE --> LOG
    METRICS --> CONFIG
    HTTP --> CONFIG
    HTTP --> CACHE

    DI --> CONFIG
    EVENT --> LOG
    REPO --> LOG
    MW --> LOG

    ES --> EVENT
    ES --> REPO
    LAMBDA --> EVENT
    KAPPA --> EVENT

    SEC --> CONFIG
    CLI --> CONFIG
```

## Core Foundation

### Configuration System

The configuration system provides centralized, type-safe configuration management.

```mermaid
sequenceDiagram
    participant App
    participant ConfigManager
    participant FileLoader
    participant EnvOverride
    participant Validator

    App->>ConfigManager: from_file("config.yaml")
    ConfigManager->>FileLoader: load_yaml()
    FileLoader-->>ConfigManager: raw_config
    ConfigManager->>EnvOverride: apply_env_overrides()
    EnvOverride-->>ConfigManager: merged_config
    ConfigManager->>Validator: validate_schema()
    Validator-->>ConfigManager: validated_config
    ConfigManager-->>App: ConfigManager instance

    App->>ConfigManager: get("database.host")
    ConfigManager-->>App: "localhost"
```

**Key Features**:
- YAML-based configuration with environment overrides
- Type validation with Pydantic
- Nested key access with dot notation
- Hot-reload support for configuration changes
- Environment-specific profiles (dev, staging, prod)

**Example**:
```python
from toolkit.config import ConfigManager

# Load with environment overrides
config = ConfigManager.from_file(
    "config.yaml",
    env_prefix="APP_",  # APP_DATABASE_HOST overrides database.host
)

# Type-safe access
db_config = config.get("database", default={})
host = config.get("database.host", default="localhost")

# Watch for changes
config.watch(lambda changes: reload_services(changes))
```

### Logging System

Structured logging with multiple handlers and context propagation.

```mermaid
graph LR
    A[Application] --> B[LogManager]
    B --> C[Formatter<br/>JSON/Text]
    C --> D1[Console Handler]
    C --> D2[File Handler]
    C --> D3[Syslog Handler]
    C --> D4[HTTP Handler]

    B --> E[Context Manager]
    E --> F1[Request ID]
    E --> F2[User ID]
    E --> F3[Trace ID]

    B --> G[Filter Chain]
    G --> H1[Level Filter]
    G --> H2[Rate Limiter]
    G --> H3[PII Masker]
```

**Key Features**:
- Structured JSON logging for machine parsing
- Context propagation (request_id, user_id, trace_id)
- Multiple handlers (console, file, syslog, HTTP)
- Performance timers and metrics
- PII masking for sensitive data
- Log sampling for high-traffic endpoints

**Example**:
```python
from toolkit.logging import LogManager

logger = LogManager.get_logger(__name__)

# Contextual logging
with logger.context(user_id="123", request_id="abc"):
    logger.info("Processing request")
    # Output: {"level": "INFO", "user_id": "123", "request_id": "abc", ...}

# Performance timing
with logger.timer("database_query"):
    results = db.execute(query)
# Output: {"message": "database_query completed", "duration_ms": 45.2}

# Exception logging with context
try:
    process_payment()
except Exception as e:
    logger.error("Payment failed", exc_info=True, extra={
        "payment_id": payment_id,
        "amount": amount,
    })
```

### Error Handling

Comprehensive error hierarchy with context and recovery strategies.

```mermaid
classDiagram
    class ToolkitError {
        +message: str
        +code: str
        +context: dict
        +is_retryable: bool
        +to_dict()
    }

    class ValidationError {
        +field: str
        +invalid_value: any
        +constraints: dict
    }

    class ResourceError {
        +resource_type: str
        +resource_id: str
    }

    class PerformanceError {
        +threshold: float
        +actual: float
        +metric: str
    }

    class RetryableError {
        +max_retries: int
        +backoff_strategy: str
    }

    ToolkitError <|-- ValidationError
    ToolkitError <|-- ResourceError
    ToolkitError <|-- PerformanceError
    ToolkitError <|-- RetryableError

    ResourceError <|-- NotFoundError
    ResourceError <|-- AlreadyExistsError
    ResourceError <|-- PermissionError

    RetryableError <|-- NetworkError
    RetryableError <|-- TimeoutError
    RetryableError <|-- ThrottledError
```

**Key Features**:
- Hierarchical error types with semantic meaning
- Error context for debugging
- Retryability indicators for automatic retry logic
- Error serialization for API responses
- Error aggregation and metrics

## Performance Layer

### Cache Manager

High-performance caching with multiple backends.

```mermaid
graph TB
    subgraph "Cache Manager"
        API[Cache API]
        SER[Serializer<br/>JSON/Pickle]
        COMP[Compressor<br/>gzip/lz4]
    end

    subgraph "Backends"
        MEM[Memory<br/>LRU Dict]
        REDIS[Redis<br/>Distributed]
        MEMCACHED[Memcached<br/>Distributed]
    end

    subgraph "Features"
        TTL[TTL Expiration]
        STATS[Statistics]
        WARM[Cache Warming]
        EVICT[Eviction Policy]
    end

    API --> SER
    SER --> COMP
    COMP --> MEM
    COMP --> REDIS
    COMP --> MEMCACHED

    MEM --> TTL
    REDIS --> TTL
    MEMCACHED --> TTL

    TTL --> STATS
    TTL --> EVICT
```

**Performance Characteristics**:
- **Memory Backend**: 326K+ ops/sec, < 10μs latency
- **Redis Backend**: 100K+ ops/sec (network dependent)
- **Memory Overhead**: < 100 bytes per entry

**Example**:
```python
from toolkit.cache import CacheManager

# High-performance memory cache
cache = CacheManager(
    backend="memory",
    max_size=10000,
    eviction_policy="lru",
)

# Distributed Redis cache
cache = CacheManager(
    backend="redis",
    host="localhost",
    serializer="pickle",  # For Python objects
    compress=True,  # Enable compression for large values
)

# Decorator for function memoization
@cache.memoize(ttl=3600, key_prefix="user_stats")
def get_user_statistics(user_id: str):
    # Expensive computation
    return compute_statistics(user_id)
```

### Rate Limiter

Token bucket algorithm with high throughput.

```mermaid
sequenceDiagram
    participant Client
    participant RateLimiter
    participant TokenBucket
    participant Storage

    Client->>RateLimiter: is_allowed("user:123")
    RateLimiter->>Storage: get_bucket("user:123")

    alt Bucket exists
        Storage-->>RateLimiter: TokenBucket(tokens=50, last_update=T1)
        RateLimiter->>TokenBucket: calculate_refill(T_now - T1)
        TokenBucket-->>RateLimiter: refilled_tokens=10
        RateLimiter->>TokenBucket: try_consume(1)

        alt Tokens available
            TokenBucket-->>RateLimiter: success(tokens_remaining=59)
            RateLimiter->>Storage: update_bucket(59, T_now)
            RateLimiter-->>Client: True
        else No tokens
            TokenBucket-->>RateLimiter: denied(tokens_remaining=0)
            RateLimiter-->>Client: False
        end
    else New bucket
        RateLimiter->>Storage: create_bucket(tokens=100, last_update=T_now)
        RateLimiter-->>Client: True
    end
```

**Performance Characteristics**:
- **Check Speed**: < 10μs per check
- **Throughput**: 100K+ checks/sec
- **Memory**: < 500 bytes per bucket
- **Scalability**: 10K+ concurrent limiters

**Example**:
```python
from toolkit.ratelimit import RateLimiter

# API rate limiting: 100 req/min per user
api_limiter = RateLimiter(rate=100, period=60)

# DDoS protection: 10 req/sec per IP
ddos_limiter = RateLimiter(rate=10, period=1)

# Decorator for route protection
@api_limiter.limit(key=lambda request: f"user:{request.user.id}")
async def api_endpoint(request):
    return {"data": "response"}

# Manual checking
if api_limiter.is_allowed(f"user:{user_id}"):
    process_request()
else:
    raise RateLimitExceeded()
```

### HTTP Client

Resilient HTTP client with retries and circuit breaker.

```mermaid
stateDiagram-v2
    [*] --> Closed: Circuit Closed

    Closed --> Open: Failures > Threshold
    Open --> HalfOpen: Timeout Elapsed
    HalfOpen --> Closed: Success
    HalfOpen --> Open: Failure

    state Closed {
        [*] --> Attempt
        Attempt --> Success: Response OK
        Attempt --> Retry: Failure (Retryable)
        Retry --> Attempt: Backoff Complete
        Retry --> Failed: Max Retries
        Attempt --> Failed: Non-Retryable
    }

    state Open {
        [*] --> Reject
        Reject --> [*]: Fast Fail
    }

    state HalfOpen {
        [*] --> Test
        Test --> [*]
    }
```

**Key Features**:
- Exponential backoff with jitter
- Circuit breaker pattern
- Connection pooling
- Request/response caching
- Automatic retries for transient failures

**Example**:
```python
from toolkit.http import HTTPClient

client = HTTPClient(
    base_url="https://api.example.com",
    timeout=5.0,
    max_retries=3,
    backoff_factor=0.5,
    circuit_breaker={
        "failure_threshold": 5,
        "recovery_timeout": 60,
    },
)

# Automatic retries and circuit breaker
response = await client.get("/users/123")

# With caching
response = await client.get(
    "/users/123",
    cache_ttl=300,  # Cache for 5 minutes
)
```

## Architecture Patterns

### Dependency Injection

Auto-wiring container with lifetime management.

```mermaid
graph TB
    subgraph "DI Container"
        REG[Registry]
        RES[Resolver]
        LIFE[Lifecycle Manager]
    end

    subgraph "Lifetimes"
        SING[Singleton<br/>Single instance]
        TRANS[Transient<br/>New per request]
        SCOPE[Scoped<br/>Per scope]
    end

    subgraph "Injection Types"
        CONS[Constructor]
        PROP[Property]
        METHOD[Method]
    end

    REG --> RES
    RES --> LIFE
    LIFE --> SING
    LIFE --> TRANS
    LIFE --> SCOPE

    RES --> CONS
    RES --> PROP
    RES --> METHOD
```

**Example**:
```python
from toolkit.di import Container, inject

container = Container()

# Register services
container.register(CacheManager, lifetime="singleton")
container.register(RateLimiter, lifetime="scoped")
container.register(UserRepository, lifetime="transient")

# Auto-wiring
@inject
class UserService:
    def __init__(
        self,
        cache: CacheManager,  # Injected
        limiter: RateLimiter,  # Injected
        repo: UserRepository,  # Injected
    ):
        self.cache = cache
        self.limiter = limiter
        self.repo = repo

# Resolve with dependencies
service = container.resolve(UserService)
```

### Event Bus

Pub/sub with async support and event sourcing.

```mermaid
sequenceDiagram
    participant Publisher
    participant EventBus
    participant Handler1
    participant Handler2
    participant ErrorHandler

    Publisher->>EventBus: publish("user.created", data)
    EventBus->>EventBus: serialize_event()
    EventBus->>EventBus: store_to_event_log()

    par Concurrent Dispatch
        EventBus->>Handler1: handle_async(event)
        EventBus->>Handler2: handle_async(event)
    end

    Handler1-->>EventBus: Success
    Handler2--xErrorHandler: Exception
    ErrorHandler->>ErrorHandler: log_error()
    ErrorHandler->>EventBus: retry_event()
```

**Example**:
```python
from toolkit.event import EventBus

bus = EventBus()

# Subscribe to events
@bus.subscribe("user.created")
async def send_welcome_email(event):
    user = event.data
    await email_service.send(user.email, "Welcome!")

@bus.subscribe("user.created")
async def create_user_profile(event):
    user = event.data
    await profile_service.create(user.id)

# Publish event (both handlers called concurrently)
await bus.publish("user.created", data={"id": "123", "email": "user@example.com"})
```

### Repository Pattern

Generic repository with Unit of Work.

```mermaid
graph TB
    subgraph "Repository Layer"
        REPO[Generic Repository<br/>CRUD Operations]
        SPEC[Specification Pattern]
        UOW[Unit of Work]
    end

    subgraph "Implementations"
        SQL[SQL Repository]
        NOSQL[NoSQL Repository]
        MEMORY[In-Memory Repository]
    end

    subgraph "Features"
        TRANS[Transactions]
        CACHE2[Caching]
        EVENTS[Domain Events]
    end

    REPO --> SPEC
    REPO --> UOW

    REPO -.implements.-> SQL
    REPO -.implements.-> NOSQL
    REPO -.implements.-> MEMORY

    UOW --> TRANS
    UOW --> CACHE2
    UOW --> EVENTS
```

**Example**:
```python
from toolkit.repository import Repository, UnitOfWork

# Generic repository
class UserRepository(Repository[User]):
    pass

# Unit of Work for transactions
async with UnitOfWork() as uow:
    user_repo = uow.get_repository(UserRepository)
    order_repo = uow.get_repository(OrderRepository)

    # Multiple operations in transaction
    user = await user_repo.get(user_id)
    user.credit -= order.total

    order = await order_repo.create(order_data)

    # Commit all or rollback
    await uow.commit()
```

## Data Processing

### Event Sourcing

CQRS pattern with event store.

```mermaid
graph LR
    subgraph "Write Side (Command)"
        CMD[Command] --> AGG[Aggregate]
        AGG --> EVT[Events]
        EVT --> STORE[Event Store]
    end

    subgraph "Read Side (Query)"
        STORE --> PROJ[Projections]
        PROJ --> VIEW1[Read Model 1]
        PROJ --> VIEW2[Read Model 2]
    end

    CMD -.validates.-> BIZ[Business Logic]
    QUERY[Query] --> VIEW1
    QUERY --> VIEW2
```

**Example**:
```python
from toolkit.eventsourcing import Aggregate, Event

class UserAggregate(Aggregate):
    def create_user(self, name: str, email: str):
        self.apply(UserCreatedEvent(name=name, email=email))

    def update_email(self, new_email: str):
        self.apply(EmailUpdatedEvent(email=new_email))

    # Event handlers
    def on_user_created(self, event: UserCreatedEvent):
        self.name = event.name
        self.email = event.email

    def on_email_updated(self, event: EmailUpdatedEvent):
        self.email = event.email

# Usage
user = UserAggregate.create(user_id)
user.create_user("Alice", "alice@example.com")
user.update_email("newemail@example.com")

# Persist events
event_store.save(user.uncommitted_events)

# Rebuild from events
user = UserAggregate.rebuild(user_id, event_store.get_events(user_id))
```

## Performance Optimization

### Profiling and Benchmarking

```python
from toolkit.metrics import MetricsManager

metrics = MetricsManager(backend="prometheus")

# Automatic profiling decorator
@metrics.profile()
def expensive_operation():
    # Code is profiled automatically
    pass

# Custom metrics
with metrics.timer("database_query"):
    results = db.execute(query)

# Counter metrics
metrics.increment("api.requests", tags={"endpoint": "/users", "method": "GET"})

# Gauge metrics
metrics.gauge("queue.size", len(queue))
```

## Testing Strategy

All backend modules have:
- **Unit Tests**: 80% of test suite
- **Integration Tests**: 15% of test suite
- **Performance Tests**: 3% of test suite
- **Property Tests**: 2% of test suite

See [Testing Guide](/guide/testing) for details.

---

Next: [Frontend Architecture](/architecture/frontend) | [Pattern Library](/patterns/overview)
