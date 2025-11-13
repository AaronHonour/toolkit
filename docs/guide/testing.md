# Testing Guide

Complete guide to running and writing tests for the Unistax.

---

## Quick Start

```bash
# Install dependencies
pip install -e ".[dev]"
cd frontend && npm install && cd ..

# Run all backend tests
pytest

# Run all frontend tests
cd frontend && npm test

# Run E2E tests
cd frontend && npm run test:e2e
```

---

## Backend Testing

### Running Tests

```bash
# All tests with coverage
pytest --cov=src/toolkit --cov-report=html

# Specific test file
pytest tests/test_cache/test_cache_manager.py

# Specific test
pytest tests/test_cache/test_cache_manager.py::TestCacheManagerBasics::test_set_and_get_simple_value

# By marker
pytest -m unit                    # Only unit tests
pytest -m integration             # Only integration tests
pytest -m performance             # Only performance tests
pytest -m "not slow"              # Exclude slow tests

# Parallel execution (faster)
pytest -n auto                    # Use all CPU cores
pytest -n 4                       # Use 4 workers

# Verbose output
pytest -v

# Stop on first failure
pytest -x

# Show local variables on failure
pytest -l

# Detailed output for failed tests
pytest --tb=long
```

### Test Markers

Available markers (defined in `pytest.ini`):

- `unit`: Fast, isolated unit tests
- `integration`: Integration tests (may need external services)
- `performance`: Performance benchmark tests
- `property`: Property-based tests with Hypothesis
- `slow`: Slow tests (> 1 second)
- `requires_redis`: Tests that need Redis
- `requires_memcached`: Tests that need Memcached

### Coverage Reports

```bash
# HTML report (opens in browser)
pytest --cov=src/toolkit --cov-report=html
open htmlcov/index.html

# Terminal report
pytest --cov=src/toolkit --cov-report=term-missing

# XML report (for CI)
pytest --cov=src/toolkit --cov-report=xml

# Fail if coverage below 90%
pytest --cov=src/toolkit --cov-fail-under=90
```

### Performance Tests

```bash
# Run only performance tests
pytest tests/performance/ --benchmark-only

# Save benchmark results
pytest tests/performance/ --benchmark-only --benchmark-save=baseline

# Compare against baseline
pytest tests/performance/ --benchmark-compare=baseline

# Fail if performance degrades > 10%
pytest tests/performance/ --benchmark-compare=baseline --benchmark-compare-fail=mean:10%

# Generate benchmark histogram
pytest tests/performance/ --benchmark-histogram
```

---

## Frontend Testing

### Running Tests

```bash
cd frontend

# All tests
npm test

# Watch mode (re-run on file changes)
npm test:watch

# Coverage report
npm test:coverage

# UI mode (visual test runner)
npm test:ui

# Specific test file
npm test Button.test.tsx

# Update snapshots
npm test -- -u
```

### E2E Tests

```bash
cd frontend

# Run E2E tests (headless)
npm run test:e2e

# Run with UI (see browser)
npm run test:e2e:ui

# Run specific test
npm run test:e2e -- app01-inventory

# Run on specific browser
npm run test:e2e -- --project=chromium
npm run test:e2e -- --project=firefox
npm run test:e2e -- --project=webkit

# Debug mode
npm run test:e2e -- --debug

# Generate HTML report
npm run test:e2e -- --reporter=html
```

### Coverage Thresholds

Frontend coverage requirements (configured in `vitest.config.ts`):

- Lines: 90%
- Functions: 90%
- Branches: 85%
- Statements: 90%

```bash
# Check coverage
npm test:coverage

# View HTML report
open frontend/coverage/index.html
```

---

## CI/CD Testing

### GitHub Actions Workflows

**On Pull Request**:
- Backend tests (Python 3.10, 3.11, 3.12)
- Frontend tests
- Integration tests
- E2E tests
- Security scanning
- Code quality checks

**On Push to Main**:
- All PR checks
- Performance benchmarks
- Docker image builds

**Nightly**:
- Full test suite (including slow tests)
- Property-based tests (1000 examples)
- Performance regression detection
- Memory profiling
- Dependency security audit

### Running CI Locally

```bash
# Install act (GitHub Actions local runner)
brew install act  # macOS
# or: curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash

# Run CI workflow
act pull_request

# Run specific job
act -j backend-tests
```

---

## Writing Tests

### Backend Test Structure

```python
"""
Module description.

Testing Strategy:
- What aspects are tested
- Coverage targets
- Performance targets
"""

import pytest
from unistax.module import MyClass


class TestMyClass:
    """Test basic functionality."""

    def test_basic_operation(self):
        """Should perform basic operation correctly."""
        # Arrange
        obj = MyClass()

        # Act
        result = obj.operation()

        # Assert
        assert result == expected


    @pytest.mark.performance
    def test_operation_performance(self, benchmark):
        """Operation should be fast (< 10μs)."""
        obj = MyClass()

        result = benchmark(obj.operation)

        assert benchmark.stats.mean < 0.00001
```

### Frontend Test Structure

```typescript
/**
 * Component/Hook description.
 *
 * Testing Strategy:
 * - What scenarios are tested
 * - User interactions
 * - Edge cases
 */

import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MyComponent } from './MyComponent'

describe('MyComponent', () => {
  it('should render correctly', () => {
    // Arrange & Act
    render(<MyComponent />)

    // Assert
    expect(screen.getByRole('button')).toBeInTheDocument()
  })

  it('should handle user interaction', async () => {
    const user = userEvent.setup()
    render(<MyComponent />)

    await user.click(screen.getByRole('button'))

    expect(screen.getByText('Clicked')).toBeVisible()
  })
})
```

### Test Best Practices

**DO**:
- ✅ Use descriptive test names: `test_cache_evicts_lru_item_when_full`
- ✅ Follow AAA pattern (Arrange, Act, Assert)
- ✅ Test one thing per test
- ✅ Use fixtures for setup/teardown
- ✅ Mock external dependencies
- ✅ Test edge cases (empty, null, max values)
- ✅ Add docstrings explaining test purpose

**DON'T**:
- ❌ Test implementation details
- ❌ Write tests that depend on other tests
- ❌ Use `sleep()` (use proper async/await or fake timers)
- ❌ Ignore flaky tests
- ❌ Skip writing tests for "simple" code
- ❌ Test framework internals

---

## Debugging Tests

### Backend Debugging

```bash
# Print output
pytest -s

# Drop into debugger on failure
pytest --pdb

# Drop into debugger at start
pytest --pdb --trace

# Increase verbosity
pytest -vv

# Show full diff for assertions
pytest -vv --tb=long
```

### Frontend Debugging

```bash
# Debug specific test
npm test -- Button.test.tsx --no-coverage

# Debug in browser
npm test:ui

# E2E debugging
npm run test:e2e:ui  # Visual mode
npm run test:e2e -- --debug  # Step-by-step
```

---

## Performance Benchmarking

### Backend Benchmarks

```bash
# Run benchmarks
pytest tests/performance/ --benchmark-only

# Save baseline
pytest tests/performance/ --benchmark-save=v1.0.0

# Compare versions
pytest tests/performance/ --benchmark-compare=v1.0.0

# Generate reports
pytest tests/performance/ --benchmark-histogram
pytest tests/performance/ --benchmark-json=output.json
```

### Frontend Benchmarks

Performance is tested via:
- Render time assertions (< 5ms target)
- Large list rendering (60fps with 1M items)
- Debounce accuracy (±10ms)

---

## Continuous Monitoring

### Coverage Tracking

Coverage is automatically tracked on every PR via Codecov:
- Backend: `codecov.io/gh/toolkit/backend`
- Frontend: `codecov.io/gh/toolkit/frontend`

### Performance Tracking

Performance benchmarks are tracked via GitHub Actions:
- Baseline stored in repository
- Alerts on > 10% regression
- Historical trends visible in Actions tab

---

## Troubleshooting

### Common Issues

**Tests fail with "fixture not found"**:
```bash
# Ensure conftest.py is in place
ls tests/conftest.py
```

**Coverage too low**:
```bash
# Find uncovered lines
pytest --cov=src/toolkit --cov-report=term-missing

# Check specific module
pytest --cov=src/toolkit/cache --cov-report=term-missing tests/test_cache/
```

**E2E tests timeout**:
```bash
# Increase timeout in playwright.config.ts
# Or run with more time:
npm run test:e2e -- --timeout=60000
```

**Performance tests fail**:
```bash
# May need to close other applications
# Or adjust thresholds in test files
```

**Frontend tests fail with module not found**:
```bash
# Reinstall dependencies
cd frontend
rm -rf node_modules
npm install
```

---

## Test Maintenance

### Weekly

- Review and fix flaky tests
- Update snapshots if needed
- Review coverage reports
- Check for slow tests

### Monthly

- Review and update performance benchmarks
- Audit test suite for redundant tests
- Update test dependencies
- Review test execution times

### Quarterly

- Review testing strategy effectiveness
- Analyze test coverage gaps
- Optimize slow test suites
- Update testing documentation

---

## Resources

- **pytest docs**: https://docs.pytest.org
- **Vitest docs**: https://vitest.dev
- **Playwright docs**: https://playwright.dev
- **Testing Library**: https://testing-library.com
- **Hypothesis**: https://hypothesis.readthedocs.io

---

## Support

For testing questions:
- Check [TESTING_STRATEGY.md](TESTING_STRATEGY.md) for philosophy
- Open an issue with `testing` label
- Ask in Discord #testing channel
