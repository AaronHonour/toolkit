# Testing Strategy

**Goal**: Achieve 90%+ test coverage across backend and frontend with comprehensive test suites that ensure quality, performance, and reliability.

---

## Testing Principles

1. **High Coverage**: 90%+ coverage for all modules
2. **Fast Feedback**: Tests run in < 2 minutes locally
3. **Deterministic**: No flaky tests, reproducible results
4. **Isolated**: Each test runs independently
5. **Documented**: Every test has clear purpose and assertions

---

## Backend Testing (Python)

### Test Categories

#### 1. Unit Tests (80% of tests)
**Coverage Target**: 95%+ line coverage

**Focus**: Individual functions, classes, methods
- Test all public APIs
- Test edge cases and error conditions
- Test type validation
- Mock external dependencies

**Tools**:
- `pytest`: Test framework
- `pytest-cov`: Coverage reporting
- `pytest-mock`: Mocking
- `pytest-asyncio`: Async tests
- `hypothesis`: Property-based testing

**Example Modules to Test**:
```python
# Cache module tests
tests/test_cache/
  test_lru_cache.py       # LRU algorithm correctness
  test_cache_manager.py   # Cache backends (Redis, Memcached, in-memory)
  test_decorators.py      # @memoize decorator

# Rate limiter tests
tests/test_ratelimit/
  test_token_bucket.py    # Token bucket algorithm
  test_sliding_window.py  # Sliding window algorithm
  test_distributed.py     # Redis-backed rate limiting
```

#### 2. Integration Tests (15% of tests)
**Coverage Target**: 80%+ integration paths

**Focus**: Module interactions, configuration loading
- Test YAML config loading
- Test dependency injection wiring
- Test event bus pub/sub
- Test repository + UnitOfWork transactions

**Example**:
```python
def test_cache_with_metrics_integration():
    """Test cache operations emit metrics."""
    cache = CacheManager(backend="memory")
    metrics = MetricsManager(backend="memory")

    cache.set("key", "value")
    assert metrics.counter("cache.sets") == 1
```

#### 3. Performance Tests (3% of tests)
**Coverage Target**: All critical algorithms

**Focus**: Performance regression detection
- Benchmark LRU cache operations (target: 326K+ ops/sec)
- Benchmark rate limiter (target: 100K+ ops/sec)
- Benchmark serialization/deserialization
- Memory usage profiling

**Tools**:
- `pytest-benchmark`: Performance testing
- `memory_profiler`: Memory profiling

**Example**:
```python
def test_lru_cache_performance(benchmark):
    """LRU cache should handle 300K+ ops/sec."""
    cache = LRUCache(capacity=1000)

    def run():
        for i in range(1000):
            cache.set(f"key{i}", f"value{i}")
            cache.get(f"key{i}")

    result = benchmark(run)
    assert result.stats.mean < 0.01  # 10ms for 2000 ops = 200K ops/sec
```

#### 4. Property-Based Tests (2% of tests)
**Coverage Target**: Critical algorithms

**Focus**: Find edge cases through generative testing
- Test invariants (e.g., LRU cache never exceeds capacity)
- Test commutative operations
- Test serialization round-trips

**Tools**: `hypothesis`

**Example**:
```python
from hypothesis import given, strategies as st

@given(st.lists(st.integers(), min_size=1, max_size=100))
def test_lru_cache_never_exceeds_capacity(items):
    """LRU cache should never exceed capacity."""
    cache = LRUCache(capacity=10)

    for item in items:
        cache.set(f"key{item}", item)

    assert len(cache) <= 10
```

---

## Frontend Testing (TypeScript/React)

### Test Categories

#### 1. Unit Tests (70% of tests)
**Coverage Target**: 90%+ line coverage

**Focus**: Hooks, utilities, pure functions
- Test performance hooks (useLRUMemo, useDebounce, etc.)
- Test utility functions
- Test design token calculations

**Tools**:
- `Vitest`: Test framework (faster than Jest)
- `@testing-library/react`: Component testing
- `@testing-library/react-hooks`: Hook testing

**Example**:
```typescript
// tests/hooks/useDebounce.test.ts
describe('useDebounce', () => {
  it('should debounce value changes', async () => {
    const { result, rerender } = renderHook(
      ({ value }) => useDebounce(value, 300),
      { initialProps: { value: 'initial' } }
    );

    expect(result.current).toBe('initial');

    rerender({ value: 'updated' });
    expect(result.current).toBe('initial'); // Still old value

    await waitFor(() => expect(result.current).toBe('updated'), { timeout: 400 });
  });
});
```

#### 2. Component Tests (20% of tests)
**Coverage Target**: 85%+ component coverage

**Focus**: Atomic components, interactions
- Test Button variants and states
- Test Input validation and errors
- Test Badge rendering
- Test user interactions (click, type, etc.)

**Example**:
```typescript
// tests/components/Button.test.tsx
describe('Button', () => {
  it('should render with primary variant', () => {
    render(<Button variant="primary">Click me</Button>);

    const button = screen.getByRole('button', { name: /click me/i });
    expect(button).toHaveClass('bg-primary-500');
  });

  it('should call onClick when clicked', () => {
    const handleClick = vi.fn();
    render(<Button onClick={handleClick}>Click</Button>);

    fireEvent.click(screen.getByRole('button'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });
});
```

#### 3. E2E Tests (10% of tests)
**Coverage Target**: Critical user flows

**Focus**: Full application workflows
- Test App 01: Product search and detail modal
- Test App 03: File upload flow
- Test App 05: Export job creation
- Test App 09: Cache CRUD operations

**Tools**: `Playwright`

**Example**:
```typescript
// tests/e2e/app01-inventory.spec.ts
test('should search products and view details', async ({ page }) => {
  await page.goto('http://localhost:3001');

  // Search for product
  await page.fill('input[placeholder*="search"]', 'laptop');
  await page.waitForTimeout(400); // Wait for debounce

  // Should show filtered results
  const products = await page.locator('.product-card').count();
  expect(products).toBeGreaterThan(0);

  // Click first product
  await page.click('.product-card:first-child');

  // Modal should open
  await expect(page.locator('[role="dialog"]')).toBeVisible();
});
```

---

## Test Organization

### Backend Structure
```
tests/
├── conftest.py                 # Shared fixtures
├── test_config/
│   ├── test_config_manager.py
│   └── test_yaml_loading.py
├── test_cache/
│   ├── test_lru_cache.py
│   ├── test_cache_backends.py
│   └── test_decorators.py
├── test_ratelimit/
│   ├── test_token_bucket.py
│   └── test_sliding_window.py
├── test_resilience/
│   ├── test_circuit_breaker.py
│   └── test_fallback.py
├── integration/
│   ├── test_di_container.py
│   └── test_event_bus.py
├── performance/
│   ├── test_cache_perf.py
│   └── test_ratelimit_perf.py
└── property/
    └── test_lru_invariants.py
```

### Frontend Structure
```
frontend/
├── packages/
│   ├── atoms/
│   │   └── src/
│   │       └── __tests__/
│   │           ├── Button.test.tsx
│   │           ├── Input.test.tsx
│   │           └── Badge.test.tsx
│   ├── performance/
│   │   └── src/
│   │       └── __tests__/
│   │           ├── useLRUMemo.test.ts
│   │           ├── useDebounce.test.ts
│   │           └── useVirtualScroll.test.ts
│   └── design-tokens/
│       └── src/
│           └── __tests__/
│               └── tokens.test.ts
├── tests/
│   └── e2e/
│       ├── app01-inventory.spec.ts
│       ├── app03-file-upload.spec.ts
│       └── app09-cache.spec.ts
└── vitest.config.ts
```

---

## CI/CD Integration

### GitHub Actions Workflow

**On every PR**:
1. Run all unit tests (backend + frontend)
2. Run integration tests
3. Generate coverage report
4. Run linting and type checking
5. Run security scanning

**On merge to main**:
1. All PR checks
2. Run E2E tests
3. Run performance benchmarks
4. Publish coverage to Codecov
5. Build Docker images

**Nightly**:
1. Full test suite including property tests
2. Performance regression tests
3. Dependency security audit

---

## Coverage Targets

### Backend
- **Overall**: 90%+
- **Core modules** (config, logging, errors): 95%+
- **Cache module**: 95%+
- **Rate limiter**: 95%+
- **Resilience patterns**: 90%+
- **DI container**: 90%+
- **Event bus**: 90%+
- **Repository pattern**: 85%+

### Frontend
- **Overall**: 90%+
- **Performance hooks**: 95%+
- **Atomic components**: 90%+
- **Design tokens**: 85%+
- **Apps**: 70%+ (E2E coverage)

---

## Performance Benchmarks

### Backend Targets
| Module | Metric | Target |
|--------|--------|--------|
| LRU Cache | ops/sec | 326K+ |
| Token Bucket | ops/sec | 100K+ |
| Sliding Window | ops/sec | 50K+ |
| Event Bus (sync) | events/sec | 500K+ |
| Event Bus (async) | events/sec | 100K+ |
| Repository.find() | queries/sec | 10K+ |

### Frontend Targets
| Component | Metric | Target |
|-----------|--------|--------|
| Button render | ms | < 1ms |
| Input render | ms | < 2ms |
| Virtual scroll | FPS | 60fps with 100K items |
| useLRUMemo | ops/sec | 300K+ |
| useDebounce | accuracy | ±10ms |

---

## Test Writing Guidelines

### DO
- ✅ Write descriptive test names: `test_cache_evicts_lru_item_when_full`
- ✅ Use AAA pattern (Arrange, Act, Assert)
- ✅ Test one thing per test
- ✅ Use fixtures for setup/teardown
- ✅ Mock external dependencies
- ✅ Test edge cases (empty, null, max values)
- ✅ Add docstrings explaining test purpose

### DON'T
- ❌ Test implementation details
- ❌ Write tests that depend on other tests
- ❌ Use sleep/wait (use proper async/await)
- ❌ Ignore flaky tests
- ❌ Skip writing tests for "simple" code
- ❌ Test framework internals

---

## Running Tests

### Backend
```bash
# All tests
pytest

# With coverage
pytest --cov=src/toolkit --cov-report=html --cov-report=term

# Specific module
pytest tests/test_cache/

# Performance tests
pytest tests/performance/ --benchmark-only

# Property tests (slower)
pytest tests/property/ --hypothesis-profile=ci
```

### Frontend
```bash
# Unit tests
npm test

# Watch mode
npm test -- --watch

# Coverage
npm test -- --coverage

# E2E tests
npm run test:e2e

# E2E headed mode (see browser)
npm run test:e2e -- --headed
```

### CI
```bash
# Run full test suite (what CI runs)
make test-all
```

---

## Maintenance

### Weekly
- Review flaky tests and fix
- Update snapshots if needed
- Review coverage reports

### Monthly
- Review and update performance benchmarks
- Audit test suite for redundant tests
- Update test dependencies

### Quarterly
- Review testing strategy effectiveness
- Analyze test execution times
- Optimize slow tests

---

## Success Metrics

**Phase 1.1 Complete When**:
- ✅ Backend coverage ≥ 90%
- ✅ Frontend coverage ≥ 90%
- ✅ All tests pass in CI
- ✅ Performance benchmarks established
- ✅ E2E tests for critical flows
- ✅ Documentation updated with testing guidelines
- ✅ Coverage badge on README

**Target Date**: End of Week 4
