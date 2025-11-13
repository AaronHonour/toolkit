# Quick Start

Get up and running with Unistax in 5 minutes.

## Prerequisites

- **Backend**: Python 3.10+, pip
- **Frontend**: Node.js 18+, npm
- **Docker** (optional): For running all apps together

## Installation

### Backend Only

```bash
# Install from PyPI (when published)
pip install unistax

# Or install from source
git clone https://github.com/AaronHonour/unistax
cd unistax/python
pip install -e ".[dev]"
```

### Frontend Only

```bash
# Install packages
npm install @unistax/atoms @unistax/performance @unistax/design-tokens

# Or clone and build from source
git clone https://github.com/AaronHonour/unistax
cd unistax/frontend
npm install
npm run build
```

### Full Stack (All 20 Apps)

```bash
# Clone repository
git clone https://github.com/AaronHonour/unistax
cd unistax

# Start everything with Docker
docker-compose up
```

Access the applications:
- **Backend APIs**: http://localhost:8000-8020
- **Frontend Apps**: http://localhost:3001-3020

## Your First Backend Module

### 1. Simple Cache Usage

```python
from unistax.cache import CacheManager

# Create cache instance
cache = CacheManager(backend="memory")

# Set a value with TTL
cache.set("user:123", {"name": "Alice", "email": "alice@example.com"}, ttl=3600)

# Get a value
user = cache.get("user:123")
print(user)  # {'name': 'Alice', 'email': 'alice@example.com'}

# Check if key exists
if cache.exists("user:123"):
    print("User is cached!")

# Delete a key
cache.delete("user:123")
```

### 2. Rate Limiting

```python
from unistax.ratelimit import RateLimiter

# 100 requests per minute per user
limiter = RateLimiter(rate=100, period=60)

# Check if request is allowed
user_id = "user:123"

if limiter.is_allowed(user_id):
    # Process request
    process_api_request()
else:
    # Reject request
    raise RateLimitExceeded("Too many requests")
```

### 3. Configuration Management

```python
from unistax.config import ConfigManager

# Load configuration from YAML
config = ConfigManager.from_file("config.yaml")

# Access nested configuration
db_host = config.get("database.host", default="localhost")
db_port = config.get("database.port", default=5432)

# Environment-specific config
if config.get("environment") == "production":
    enable_debug = False
```

### 4. Structured Logging

```python
from unistax.logging import LogManager

# Create logger
logger = LogManager.get_logger(__name__)

# Log with context
logger.info("User login", extra={
    "user_id": "123",
    "ip_address": "192.168.1.1",
    "user_agent": "Mozilla/5.0"
})

# Log with performance metrics
with logger.timer("database_query"):
    results = execute_query()

# Output: {"level": "INFO", "message": "database_query completed", "duration_ms": 45.2}
```

## Your First Frontend Component

### 1. Using Atomic Components

```tsx
import { Button } from '@unistax/atoms'
import { useState } from 'react'

function MyComponent() {
  const [loading, setLoading] = useState(false)

  const handleClick = async () => {
    setLoading(true)
    await performAction()
    setLoading(false)
  }

  return (
    <div>
      <Button
        variant="primary"
        size="lg"
        loading={loading}
        onClick={handleClick}
      >
        Click Me
      </Button>
    </div>
  )
}
```

### 2. Using Performance Hooks

```tsx
import { useDebounce } from '@unistax/performance'
import { useState, useEffect } from 'react'

function SearchComponent() {
  const [search, setSearch] = useState('')
  const debouncedSearch = useDebounce(search, 300)

  useEffect(() => {
    if (debouncedSearch) {
      // Only called 300ms after user stops typing
      performSearch(debouncedSearch)
    }
  }, [debouncedSearch])

  return (
    <input
      value={search}
      onChange={(e) => setSearch(e.target.value)}
      placeholder="Search..."
    />
  )
}
```

### 3. Using Virtual Scroll for Large Lists

```tsx
import { useVirtualScroll } from '@unistax/performance'

function LargeList({ items }) {
  const {
    virtualItems,
    totalHeight,
    containerRef,
  } = useVirtualScroll({
    items,
    itemHeight: 50,
    overscan: 5,
  })

  return (
    <div
      ref={containerRef}
      style={{ height: '500px', overflow: 'auto' }}
    >
      <div style={{ height: totalHeight }}>
        {virtualItems.map(({ item, style }) => (
          <div key={item.id} style={style}>
            {item.name}
          </div>
        ))}
      </div>
    </div>
  )
}
```

### 4. Using LRU Memoization

```tsx
import { useLRUMemo } from '@unistax/performance'

function ExpensiveComponent({ data }) {
  // Cache last 100 computation results
  const result = useLRUMemo(
    () => expensiveComputation(data),
    [data],
    { maxSize: 100 }
  )

  return <div>{result}</div>
}
```

## Building a Full-Stack Feature

Let's build a simple user profile cache with rate limiting:

### Backend API (FastAPI)

```python
# backend/api.py
from fastapi import FastAPI, HTTPException, Request
from unistax.cache import CacheManager
from unistax.ratelimit import RateLimiter

app = FastAPI()
cache = CacheManager(backend="redis", host="localhost")
limiter = RateLimiter(rate=100, period=60)

@app.get("/users/{user_id}")
async def get_user(user_id: str, request: Request):
    # Rate limiting
    client_ip = request.client.host
    if not limiter.is_allowed(f"ip:{client_ip}"):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    # Check cache first
    cached_user = cache.get(f"user:{user_id}")
    if cached_user:
        return cached_user

    # Fetch from database
    user = fetch_user_from_db(user_id)

    # Cache for 1 hour
    cache.set(f"user:{user_id}", user, ttl=3600)

    return user
```

### Frontend Component

```tsx
// frontend/UserProfile.tsx
import { useState, useEffect } from 'react'
import { Button, Spinner, Badge } from '@unistax/atoms'
import { useDebounce } from '@unistax/performance'

interface User {
  id: string
  name: string
  email: string
  status: 'active' | 'inactive'
}

export function UserProfile({ userId }: { userId: string }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const debouncedUserId = useDebounce(userId, 300)

  useEffect(() => {
    const fetchUser = async () => {
      setLoading(true)
      setError(null)

      try {
        const response = await fetch(`/api/users/${debouncedUserId}`)

        if (response.status === 429) {
          throw new Error('Rate limit exceeded. Please try again later.')
        }

        if (!response.ok) {
          throw new Error('Failed to fetch user')
        }

        const data = await response.json()
        setUser(data)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error')
      } finally {
        setLoading(false)
      }
    }

    if (debouncedUserId) {
      fetchUser()
    }
  }, [debouncedUserId])

  if (loading) {
    return <Spinner size="lg" />
  }

  if (error) {
    return <div className="text-red-500">{error}</div>
  }

  if (!user) {
    return null
  }

  return (
    <div className="p-4 border rounded-lg">
      <h2 className="text-xl font-bold">{user.name}</h2>
      <p className="text-gray-600">{user.email}</p>
      <Badge variant={user.status === 'active' ? 'success' : 'secondary'}>
        {user.status}
      </Badge>
      <Button variant="primary" className="mt-4">
        Edit Profile
      </Button>
    </div>
  )
}
```

## Running the Example Apps

### Option 1: Docker (Recommended)

```bash
# Start all 20 apps
docker-compose up

# Start specific app
docker-compose up app01-inventory

# View logs
docker-compose logs -f app01-inventory
```

### Option 2: Manual

```bash
# Backend (in separate terminals)
cd examples/backends/01_inventory
python main.py

# Frontend
cd examples/frontends/01-inventory
npm run dev
```

## Development Workflow

### Backend Development

```bash
# Install dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=unistax --cov-report=html

# Run linting
ruff check src/unistax tests
black --check src/unistax tests

# Run type checking
mypy src/unistax
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Run dev server
npm run dev

# Run tests
npm test

# Run tests with coverage
npm run test:coverage

# Run E2E tests
npm run test:e2e

# Build
npm run build
```

## Performance Verification

### Backend Performance

```bash
# Run performance benchmarks
pytest tests/performance/ --benchmark-only

# Expected output:
# Cache operations: 326K+ ops/sec
# Rate limiter checks: 100K+ checks/sec
# Token bucket latency: < 10μs
```

### Frontend Performance

```bash
# Run performance tests
npm test -- --run tests/performance/

# Expected output:
# Button render: < 1ms
# Debounce accuracy: ±10ms
# Virtual scroll: 60fps with 1M+ items
```

## Configuration

### Backend Configuration (config.yaml)

```yaml
environment: development

cache:
  backend: redis
  host: localhost
  port: 6379
  ttl: 3600

ratelimit:
  rate: 100
  period: 60

logging:
  level: INFO
  format: json
  handlers:
    - type: console
    - type: file
      filename: app.log
```

### Frontend Configuration (.env)

```bash
VITE_API_BASE_URL=http://localhost:8000
VITE_ENABLE_PERFORMANCE_MONITOR=true
VITE_CACHE_SIZE=1000
```

## Next Steps

Now that you have the basics:

1. **Explore the 20 Example Apps** - See real-world implementations
2. **Read the Architecture Guide** - Understand design patterns
3. **Check API Documentation** - Detailed module references
4. **Read Pattern Deep-Dives** - Learn when and how to use each pattern

## Common Issues

### "Module not found" errors

```bash
# Backend
pip install -e ".[dev]"

# Frontend
npm install
```

### Port already in use

```bash
# Change port in docker-compose.yml or .env files
# Backend: PORT=8001
# Frontend: VITE_PORT=3002
```

### Performance below targets

- Ensure running in production mode
- Check system resources
- Disable debug logging
- Use Redis instead of memory cache for production

## Getting Help

- **Documentation**: [Read the full docs](/guide/introduction)
- **Issues**: [GitHub Issues](https://github.com/AaronHonour/unistax/issues)
- **Discussions**: [GitHub Discussions](https://github.com/AaronHonour/unistax/discussions)

---

Ready to dive deeper? Continue to the [Architecture Overview](/architecture/overview)
