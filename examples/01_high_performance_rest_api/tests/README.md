# Test Suite for High-Performance REST API

Comprehensive test suite validating functionality and performance.

## Test Structure

```
tests/
├── unit/                    # Unit tests (fast, isolated)
│   ├── test_product_model.py
│   └── test_inventory_model.py
├── integration/             # Integration tests (API endpoints)
│   ├── test_product_api.py
│   └── test_inventory_api.py
├── benchmarks/              # Performance benchmarks
│   ├── test_api_performance.py
│   └── locustfile.py
└── conftest.py             # Shared fixtures
```

## Running Tests

### Install Test Dependencies

```bash
pip install -r requirements-test.txt
```

### Run All Tests

```bash
pytest
```

### Run Specific Test Types

```bash
# Unit tests only (fast)
pytest -m unit

# Integration tests
pytest -m integration

# Performance benchmarks
pytest -m benchmark

# Exclude slow tests
pytest -m "not slow"
```

### Run with Coverage

```bash
pytest --cov=src --cov-report=html
# Open htmlcov/index.html to view coverage report
```

## Test Categories

### Unit Tests

Fast, isolated tests for domain models and business logic.

**Coverage:**
- Product model (creation, validation, updates, margin calculation)
- Inventory model (stock operations, reservations, status updates)
- Business rules and constraints
- `__slots__` memory optimization verification

**Run:**
```bash
pytest tests/unit/ -v
```

### Integration Tests

End-to-end tests for API endpoints with real database.

**Coverage:**
- Product CRUD operations
- Inventory management
- Stock operations (reserve, release, fulfill)
- Search and filtering
- Pagination
- Error handling
- Complete order workflows

**Run:**
```bash
pytest tests/integration/ -v
```

### Performance Benchmarks

Validates 100K+ RPS capability and performance targets.

**Coverage:**
- Product read performance
- Concurrent operations
- Cache effectiveness
- Atomic stock operations
- Bulk operations
- End-to-end order flow
- Repository-level performance

**Run:**
```bash
pytest tests/benchmarks/ -v --benchmark-only
```

## Load Testing with Locust

### Quick Load Test

```bash
# Start API server (terminal 1)
python src/main.py

# Run load test (terminal 2)
cd tests/benchmarks
locust -f locustfile.py --host=http://localhost:8000
```

Then open http://localhost:8089 for the Locust web UI.

### Headless Load Test

Validate 100K+ RPS capability:

```bash
locust -f tests/benchmarks/locustfile.py \
    --host=http://localhost:8000 \
    --users=1000 \
    --spawn-rate=100 \
    --run-time=60s \
    --headless \
    --print-stats
```

### Load Test Scenarios

**1. Read-Heavy Workload** (Validates caching effectiveness)
```bash
locust -f tests/benchmarks/locustfile.py \
    --host=http://localhost:8000 \
    --user-classes ReadHeavyUser \
    --users=2000 \
    --spawn-rate=200 \
    --run-time=60s
```

**2. Mixed Workload** (Realistic production traffic)
```bash
locust -f tests/benchmarks/locustfile.py \
    --host=http://localhost:8000 \
    --user-classes InventoryAPIUser \
    --users=1000 \
    --spawn-rate=100 \
    --run-time=300s
```

**3. Stress Test** (Find breaking point)
```bash
locust -f tests/benchmarks/locustfile.py \
    --host=http://localhost:8000 \
    --users=5000 \
    --spawn-rate=500 \
    --run-time=120s
```

## Performance Targets

Tests validate these performance targets:

| Metric | Target | Test |
|--------|--------|------|
| Throughput | 100K+ RPS | Load test |
| P99 Latency | < 100ms | Benchmarks |
| Cache Hit Rate | 70%+ | Cache tests |
| Concurrent Ops | 1000+ | Concurrency tests |
| Memory | 40-50% reduction | __slots__ tests |

## Expected Results

### Unit Tests
- **~40 tests** covering domain models
- **100% coverage** of business logic
- **< 1 second** total runtime

### Integration Tests
- **~30 tests** covering all API endpoints
- **End-to-end workflows** validated
- **< 10 seconds** total runtime (with in-memory DB)

### Performance Benchmarks
- **Product read:** > 10K ops/sec (cached)
- **Concurrent reads:** 100 reads in < 1s
- **Atomic operations:** > 100 ops/sec
- **Search queries:** < 200ms
- **Cache speedup:** 1.5x+ improvement
- **Bulk operations:** 50+ products/sec

### Load Test Results (Expected)
With single FastAPI instance (uvicorn):
- **Read-heavy:** 50K-100K RPS
- **Mixed workload:** 20K-50K RPS
- **P99 latency:** < 50ms (cached reads)
- **P99 latency:** < 100ms (mixed operations)

With multiple workers (4 cores):
- **Read-heavy:** 100K-200K RPS
- **Mixed workload:** 50K-100K RPS

## Continuous Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-test.txt

      - name: Run unit tests
        run: pytest tests/unit/ -v

      - name: Run integration tests
        run: pytest tests/integration/ -v

      - name: Run benchmarks
        run: pytest tests/benchmarks/ -v

      - name: Generate coverage
        run: pytest --cov=src --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

## Troubleshooting

### Tests Fail with Database Errors

Ensure SQLAlchemy and aiosqlite are installed:
```bash
pip install sqlalchemy[asyncio] aiosqlite
```

### Load Tests Show Low RPS

Possible causes:
1. **Single worker:** Use `--workers 4` with uvicorn
2. **Debug mode:** Ensure `reload=False` in production
3. **System resources:** Check CPU/memory usage
4. **Network latency:** Run load test from same machine

### Benchmarks Too Slow

1. Use in-memory SQLite for tests (already configured)
2. Ensure no other processes consuming resources
3. Check if pytest-benchmark is installed

## Best Practices

1. **Run unit tests frequently** during development
2. **Run integration tests** before committing
3. **Run benchmarks** before releases
4. **Profile slow tests** with `pytest --durations=10`
5. **Monitor coverage** to ensure code quality
6. **Use load tests** to validate production readiness

## Additional Resources

- [pytest documentation](https://docs.pytest.org/)
- [Locust documentation](https://docs.locust.io/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [Performance Testing Best Practices](https://www.nginx.com/blog/testing/)
