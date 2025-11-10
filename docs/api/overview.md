# API Reference

Complete API documentation for all backend modules and frontend packages.

## Backend Modules

### Core Foundation

#### [Config Manager](/api/backend/config)
```python
from toolkit.config import ConfigManager

config = ConfigManager.from_file("config.yaml", env_prefix="APP_")
value = config.get("database.host", default="localhost")
config.watch(callback)
```

**Key Methods**:
- `from_file(path, env_prefix)` - Load from YAML with environment overrides
- `get(key, default)` - Get configuration value with dot notation
- `set(key, value)` - Set configuration value
- `watch(callback)` - Watch for configuration changes
- `validate(schema)` - Validate against Pydantic schema

#### [Logging](/api/backend/logging)
```python
from toolkit.logging import LogManager

logger = LogManager.get_logger(__name__)
logger.info("message", extra={"key": "value"})
```

**Key Methods**:
- `get_logger(name)` - Get named logger
- `context(**kwargs)` - Add context to all logs
- `timer(name)` - Time code execution
- `add_handler(handler)` - Add log handler
- `set_level(level)` - Set log level

#### [Error Handling](/api/backend/errors)
```python
from toolkit.errors import ToolkitError, ValidationError

raise ValidationError(
    message="Invalid email",
    field="email",
    invalid_value="not-an-email"
)
```

**Error Hierarchy**:
- `ToolkitError` - Base error
  - `ValidationError` - Input validation errors
  - `ResourceError` - Resource-related errors
    - `NotFoundError`
    - `AlreadyExistsError`
    - `PermissionError`
  - `RetryableError` - Retryable errors
    - `NetworkError`
    - `TimeoutError`
    - `ThrottledError`
  - `PerformanceError` - Performance threshold violations

### Performance Modules

#### [Cache Manager](/api/backend/cache)
```python
from toolkit.cache import CacheManager

cache = CacheManager(
    backend="redis",
    host="localhost",
    serializer="pickle",
    compress=True
)

cache.set("key", value, ttl=3600)
value = cache.get("key")
cache.delete("key")
```

**Performance**: 326K+ ops/sec (memory), 100K+ ops/sec (Redis)

**Backends**: `memory`, `redis`, `memcached`

**Key Methods**:
- `set(key, value, ttl)` - Set value with optional TTL
- `get(key, default)` - Get value or default
- `delete(key)` - Delete key
- `exists(key)` - Check if key exists
- `clear()` - Clear all keys
- `memoize(ttl, key_prefix)` - Decorator for function memoization
- `get_stats()` - Get cache statistics

#### [Rate Limiter](/api/backend/ratelimit)
```python
from toolkit.ratelimit import RateLimiter

limiter = RateLimiter(rate=100, period=60)  # 100 req/min

if limiter.is_allowed("user:123"):
    process_request()
else:
    raise RateLimitExceeded()
```

**Performance**: 100K+ checks/sec, < 10μs latency

**Key Methods**:
- `is_allowed(key)` - Check if request is allowed
- `get_remaining(key)` - Get remaining tokens
- `get_reset_time(key)` - Get time until reset
- `reset(key)` - Reset rate limit for key
- `limit(key)` - Decorator for function rate limiting

#### [Metrics Manager](/api/backend/metrics)
```python
from toolkit.metrics import MetricsManager

metrics = MetricsManager(backend="prometheus")

metrics.increment("api.requests", tags={"endpoint": "/users"})
metrics.gauge("queue.size", len(queue))
metrics.histogram("response.time", duration)

with metrics.timer("database_query"):
    results = db.execute(query)
```

**Backends**: `prometheus`, `statsd`, `datadog`

**Key Methods**:
- `increment(name, value, tags)` - Increment counter
- `decrement(name, value, tags)` - Decrement counter
- `gauge(name, value, tags)` - Set gauge value
- `histogram(name, value, tags)` - Record histogram value
- `timer(name, tags)` - Time code execution
- `profile()` - Decorator for automatic profiling

#### [HTTP Client](/api/backend/http)
```python
from toolkit.http import HTTPClient

client = HTTPClient(
    base_url="https://api.example.com",
    timeout=5.0,
    max_retries=3,
    circuit_breaker={
        "failure_threshold": 5,
        "recovery_timeout": 60,
    }
)

response = await client.get("/users/123", cache_ttl=300)
response = await client.post("/users", json=data)
```

**Key Features**:
- Automatic retries with exponential backoff
- Circuit breaker pattern
- Connection pooling
- Request/response caching
- Timeout handling

**Key Methods**:
- `get(url, params, cache_ttl)` - GET request
- `post(url, json, data)` - POST request
- `put(url, json, data)` - PUT request
- `delete(url)` - DELETE request
- `request(method, url, **kwargs)` - Generic request

### Architecture Patterns

#### [Dependency Injection](/api/backend/di)
```python
from toolkit.di import Container, inject

container = Container()
container.register(CacheManager, lifetime="singleton")

@inject
class UserService:
    def __init__(self, cache: CacheManager):
        self.cache = cache

service = container.resolve(UserService)
```

**Lifetimes**: `singleton`, `transient`, `scoped`

**Key Methods**:
- `register(interface, implementation, lifetime)` - Register service
- `resolve(interface)` - Resolve instance
- `create_scope()` - Create new scope
- `inject` - Decorator for auto-wiring

#### [Event Bus](/api/backend/event)
```python
from toolkit.event import EventBus

bus = EventBus()

@bus.subscribe("user.created")
async def handle_user_created(event):
    await send_welcome_email(event.data)

await bus.publish("user.created", data={"user_id": "123"})
```

**Key Methods**:
- `subscribe(event_name, handler, priority)` - Subscribe to event
- `unsubscribe(event_name, handler)` - Unsubscribe from event
- `publish(event_name, data, **kwargs)` - Publish event
- `publish_async(event_name, data)` - Async publish
- `get_subscribers(event_name)` - Get event subscribers

#### [Repository Pattern](/api/backend/repository)
```python
from toolkit.repository import Repository, UnitOfWork

class UserRepository(Repository[User]):
    async def find_by_email(self, email: str) -> User | None:
        return await self.find_one({"email": email})

async with UnitOfWork() as uow:
    user_repo = uow.get_repository(UserRepository)
    user = await user_repo.get(user_id)
    user.name = "Updated"
    await uow.commit()
```

**Key Methods**:
- `get(id)` - Get by ID
- `find(criteria)` - Find multiple
- `find_one(criteria)` - Find single
- `create(entity)` - Create entity
- `update(entity)` - Update entity
- `delete(id)` - Delete entity
- `count(criteria)` - Count entities

### Data Processing

#### [Event Sourcing](/api/backend/eventsourcing)
```python
from toolkit.eventsourcing import Aggregate, Event

class UserAggregate(Aggregate):
    def create_user(self, name: str):
        self.apply(UserCreatedEvent(name=name))

    def on_user_created(self, event: UserCreatedEvent):
        self.name = event.name

user = UserAggregate.create(user_id)
user.create_user("Alice")
event_store.save(user.uncommitted_events)
```

**Key Concepts**:
- Aggregate - Domain entity with event sourcing
- Event - Immutable domain event
- Event Store - Persistence for events
- Projection - Read model built from events

#### [Lambda Architecture](/api/backend/lambda)
```python
from toolkit.lambda_arch import BatchLayer, StreamLayer, ServingLayer

batch = BatchLayer()
stream = StreamLayer()
serving = ServingLayer()

# Batch processing
batch_result = batch.process(historical_data)

# Stream processing
stream.process_event(new_event)

# Merged view
result = serving.query(user_id)  # Batch + Stream merged
```

### Operations

#### [Security](/api/backend/security)
```python
from toolkit.security import JWTManager, RBACManager, PasswordHasher

# JWT
jwt = JWTManager(secret_key="secret")
token = jwt.encode({"user_id": "123"})
payload = jwt.decode(token)

# RBAC
rbac = RBACManager()
rbac.grant("user:123", "admin")
if rbac.has_role("user:123", "admin"):
    allow_access()

# Password hashing
hasher = PasswordHasher()
hashed = hasher.hash("password123")
if hasher.verify("password123", hashed):
    login_user()
```

**Key Features**:
- JWT token generation and validation
- Role-based access control (RBAC)
- Secure password hashing (bcrypt)
- Permission management

## Frontend Packages

### Atomic Components

#### [@composable/atoms](/api/frontend/atoms)

**Button**:
```tsx
import { Button } from '@composable/atoms'

<Button
  variant="primary" | "secondary" | "success" | "danger" | "ghost"
  size="xs" | "sm" | "md" | "lg" | "xl"
  loading={boolean}
  disabled={boolean}
  leftIcon={ReactNode}
  rightIcon={ReactNode}
  onClick={handler}
>
  Button Text
</Button>
```

**Input**:
```tsx
import { Input } from '@composable/atoms'

<Input
  type="text" | "email" | "password" | "number"
  size="sm" | "md" | "lg"
  error={string}
  helperText={string}
  leftAddon={ReactNode}
  rightAddon={ReactNode}
  onChange={handler}
/>
```

**Badge**:
```tsx
import { Badge } from '@composable/atoms'

<Badge
  variant="primary" | "secondary" | "success" | "warning" | "danger" | "info"
  size="sm" | "md" | "lg"
  dot={boolean}
>
  Badge Text
</Badge>
```

**Spinner**:
```tsx
import { Spinner } from '@composable/atoms'

<Spinner
  size="xs" | "sm" | "md" | "lg" | "xl"
  color="primary" | "secondary" | "white"
/>
```

**Icon**:
```tsx
import { Icon } from '@composable/atoms'

<Icon
  name="check" | "x" | "chevron-right" | "search" | ...
  size={number}
  color={string}
/>
```

### Performance Hooks

#### [@composable/performance](/api/frontend/performance)

**useLRUMemo**:
```tsx
import { useLRUMemo } from '@composable/performance'

const result = useLRUMemo(
  () => expensiveComputation(data),
  [data],
  { maxSize: 100 }
)
```
**Performance**: 300K+ cache lookups/sec

**useDebounce**:
```tsx
import { useDebounce } from '@composable/performance'

const [value, setValue] = useState('')
const debouncedValue = useDebounce(value, 300)
```
**Performance**: ±10ms accuracy

**useThrottle**:
```tsx
import { useThrottle } from '@composable/performance'

const [value, setValue] = useState(0)
const throttledValue = useThrottle(value, 1000)
```

**useVirtualScroll**:
```tsx
import { useVirtualScroll } from '@composable/performance'

const { virtualItems, totalHeight, containerRef } = useVirtualScroll({
  items,
  itemHeight: 50,
  overscan: 5,
})
```
**Performance**: 60fps with 1M+ items

**useWorkerPool**:
```tsx
import { useWorkerPool } from '@composable/performance'

const { execute, isProcessing } = useWorkerPool({
  workerCount: 4,
  workerScript: '/workers/processor.js',
})

const result = await execute({ type: 'process', data })
```

**usePerformanceMonitor**:
```tsx
import { usePerformanceMonitor } from '@composable/performance'

const { fps, memory, renderTime } = usePerformanceMonitor({
  enabled: isDevelopment,
  sampleInterval: 1000,
})
```

### Design Tokens

#### [@composable/design-tokens](/api/frontend/design-tokens)

```tsx
import { colors, spacing, typography } from '@composable/design-tokens'

// Colors
const primaryColor = colors.primary[500]
const successColor = colors.success.default

// Spacing
const padding = spacing[4]  // 1rem / 16px

// Typography
const fontSize = typography.fontSize.lg
const fontFamily = typography.fontFamily.sans
```

## OpenAPI Specifications

Each backend service provides OpenAPI 3.0 specification:

- [App 01 - Inventory API](/api/openapi/app01-inventory)
- [App 02 - Analytics API](/api/openapi/app02-analytics)
- [App 03 - File Processor API](/api/openapi/app03-file-processor)
- ... (all 19 apps)

## Type Definitions

Full TypeScript type definitions available:

```bash
# Install types
npm install @composable/atoms @composable/performance

# Types are automatically included
import type { ButtonProps } from '@composable/atoms'
import type { UseLRUMemoOptions } from '@composable/performance'
```

## Response Formats

### Success Response
```json
{
  "success": true,
  "data": { ... },
  "metadata": {
    "timestamp": "2024-01-01T12:00:00Z",
    "request_id": "abc123"
  }
}
```

### Error Response
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input",
    "details": {
      "field": "email",
      "constraint": "format"
    }
  },
  "metadata": {
    "timestamp": "2024-01-01T12:00:00Z",
    "request_id": "abc123"
  }
}
```

---

Next: [Pattern Library](/patterns/overview) | [Testing Guide](/guide/testing)
