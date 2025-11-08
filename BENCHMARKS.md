# Performance Benchmarks

Comprehensive performance benchmarking system for the Composable Toolkit, designed to validate the **100K+ requests/second** capability and track performance over time.

## Quick Start

```bash
# Run all benchmarks
python scripts/run-benchmarks.py

# Run quick benchmarks only (faster)
python scripts/run-benchmarks.py --quick

# View latest results
open benchmarks/results/latest.html
```

## Overview

The benchmark system provides:

- **Automated Performance Testing**: Comprehensive benchmarks for all 19 patterns
- **Regression Detection**: Automatically detect performance degradations
- **Historical Tracking**: Track performance trends over time
- **Public Dashboard**: View latest benchmark results online
- **Multi-Platform**: Test across Python 3.10, 3.11, and 3.12
- **CI/CD Integration**: Automated nightly runs via GitHub Actions

## Architecture

```
├── tests/
│   ├── benchmark.py                          # Core benchmark framework
│   ├── benchmarks/                           # Benchmark test suites
│   │   ├── test_algorithms_benchmarks.py     # Algorithm performance
│   │   └── test_database_benchmarks.py       # Database performance
│   └── performance/                          # Performance regression tests
│       ├── test_cache_performance.py         # Cache benchmarks
│       └── test_ratelimit_performance.py     # Rate limiter benchmarks
│
├── scripts/
│   ├── run-benchmarks.py                     # Main benchmark runner
│   └── compare-benchmarks.py                 # Regression detection
│
├── .github/workflows/
│   └── benchmarks.yml                        # Automated nightly runs
│
└── benchmarks/                               # Results directory
    ├── results/                              # Latest results
    │   ├── latest.json                       # Latest JSON data
    │   └── latest.html                       # Latest HTML report
    └── baseline/                             # Performance baseline
        ├── latest.json
        └── latest.html
```

## Benchmark Framework

### Core Framework (tests/benchmark.py)

```python
from tests.benchmark import Benchmark

# Create benchmark
benchmark = Benchmark("my_test")

# Run synchronous function
result = benchmark.run(my_function, iterations=1000)

# Run async function
result = await benchmark.run_async(my_async_function, iterations=1000)

# Compare implementations
comparison = benchmark.compare(
    old_implementation,
    new_implementation,
    iterations=1000,
    name1="baseline",
    name2="optimized"
)

print(f"Speedup: {comparison['speedup']:.2f}x")
print(f"Improvement: {comparison['improvement_percent']:.1f}%")
```

### Benchmark Results

Each benchmark provides detailed statistics:

```python
@dataclass
class BenchmarkResult:
    name: str                    # Benchmark name
    iterations: int              # Number of iterations run
    total_time: float            # Total execution time
    min_time: float              # Fastest iteration
    max_time: float              # Slowest iteration
    mean_time: float             # Average time
    median_time: float           # Median time
    p95_time: float              # 95th percentile
    p99_time: float              # 99th percentile
    stddev: float                # Standard deviation
    ops_per_second: float        # Throughput
    metadata: Dict[str, Any]     # Additional context
```

### Memory Benchmarking

```python
from tests.benchmark import MemoryBenchmark

# Measure memory usage
stats = MemoryBenchmark.measure_memory(my_function, iterations=100)

print(f"Mean memory: {stats['mean_mb']:.2f} MB")
print(f"Max memory: {stats['max_mb']:.2f} MB")
```

### Load Testing

```python
from tests.benchmark import LoadBenchmark

# Run load test
results = LoadBenchmark.run_load_test(
    func=my_endpoint,
    duration=10.0,      # 10 seconds
    concurrency=50      # 50 concurrent workers
)

print(f"RPS: {results['requests_per_second']:.0f}")
print(f"P95 latency: {results['latency_p95']:.2f}ms")
print(f"Error rate: {results['error_rate']:.2%}")
```

## Performance Targets

### Algorithm Benchmarks

| Component | Target | Actual (Typical) |
|-----------|--------|------------------|
| RingBuffer | 200K+ ops/sec | ~350K ops/sec |
| LRUCache | 200K+ ops/sec | ~326K ops/sec |
| BloomFilter | 500K+ ops/sec | ~800K ops/sec |
| FastDict | 300K+ ops/sec | ~450K ops/sec |
| FastHash | 1M+ ops/sec | ~2M ops/sec |

### Cache Performance

| Operation | Target | Actual (Typical) |
|-----------|--------|------------------|
| Set | < 10μs | ~3-5μs |
| Get | < 10μs | ~2-4μs |
| Throughput | 100K+ ops/sec | ~200K+ ops/sec |

### Rate Limiter Performance

| Operation | Target | Actual (Typical) |
|-----------|--------|------------------|
| Check | < 100μs | ~20-50μs |
| Throughput | 50K+ ops/sec | ~100K+ ops/sec |

### Database Operations

| Operation | Target | Actual (Typical) |
|-----------|--------|------------------|
| Query | < 5ms | ~1-3ms |
| Insert | < 10ms | ~2-5ms |
| Bulk Insert | 10K+ rows/sec | ~20K+ rows/sec |

## Running Benchmarks

### Local Development

```bash
# Install dependencies
pip install -e ".[dev,all]"

# Run all benchmarks with detailed output
python scripts/run-benchmarks.py

# Run specific pattern
pytest tests/benchmarks/test_algorithms_benchmarks.py -v

# Run with pytest-benchmark
pytest tests/benchmarks/ --benchmark-only

# Run performance regression tests
pytest tests/performance/ -m performance
```

### Quick Benchmarks

```bash
# Skip full pytest suite (faster iteration)
python scripts/run-benchmarks.py --quick

# Run single test file
pytest tests/benchmarks/test_algorithms_benchmarks.py -v -s
```

### Custom Output Directory

```bash
# Specify output location
python scripts/run-benchmarks.py --output-dir /path/to/results
```

## Viewing Results

### HTML Reports

After running benchmarks, open the HTML report:

```bash
# View latest report
open benchmarks/results/latest.html

# Or with your browser
firefox benchmarks/results/latest.html
```

The HTML report includes:
- Summary statistics (total, passed, failed, success rate)
- Individual benchmark results with metrics
- Environment information (Python version, platform, etc.)
- Visual indicators for pass/fail status

### JSON Results

```bash
# View JSON results
cat benchmarks/results/latest.json | jq .

# Extract specific metrics
cat benchmarks/results/latest.json | jq '.benchmarks.algorithms.success'
```

## Detecting Regressions

### Compare Against Baseline

```bash
# Run current benchmarks
python scripts/run-benchmarks.py

# Compare with baseline
python scripts/compare-benchmarks.py \
    benchmarks/baseline/latest.json \
    benchmarks/results/latest.json \
    --threshold 10

# Fail if regressions detected
python scripts/compare-benchmarks.py \
    benchmarks/baseline/latest.json \
    benchmarks/results/latest.json \
    --threshold 10 \
    --fail-on-regression
```

### Update Baseline

When performance improves or you intentionally change performance characteristics:

```bash
# Run benchmarks
python scripts/run-benchmarks.py

# Update baseline
mkdir -p benchmarks/baseline
cp benchmarks/results/latest.json benchmarks/baseline/latest.json
cp benchmarks/results/latest.html benchmarks/baseline/latest.html

# Commit new baseline
git add benchmarks/baseline/
git commit -m "Update performance baseline"
```

## Automated Benchmarks

### GitHub Actions

Benchmarks run automatically:

- **Nightly**: Every day at 2 AM UTC
- **Pull Requests**: On benchmark-related changes
- **Manual**: Via workflow_dispatch

#### Trigger Manual Run

1. Go to Actions tab on GitHub
2. Select "Performance Benchmarks" workflow
3. Click "Run workflow"
4. Optional: Check "Run quick benchmarks only"

#### View Results

1. Go to Actions tab
2. Click on benchmark run
3. Download artifacts:
   - `benchmark-results-py3.XX`: Raw JSON/HTML results
   - `benchmark-report-py3.XX`: HTML report

#### PR Comments

On pull requests, the workflow automatically comments with:
- Summary of benchmark results
- Pass/fail status for each category
- Link to full report

### Benchmark Dashboard

Live dashboard available at: `https://yourusername.github.io/toolkit/`

Features:
- Latest results for Python 3.10, 3.11, 3.12
- Historical trend tracking
- Updated nightly
- 90-day result retention

## Writing Custom Benchmarks

### Basic Benchmark

```python
# tests/benchmarks/test_my_feature.py
from tests.benchmark import Benchmark

def test_my_feature_performance():
    """Benchmark my feature."""
    benchmark = Benchmark("my_feature")

    def operation():
        # Your code here
        my_feature.do_something()

    result = benchmark.run(operation, iterations=10000)

    # Assert performance targets
    assert result.ops_per_second > 50000, \
        f"Too slow: {result.ops_per_second:,.0f} ops/sec"

    print(result)  # Print detailed results
```

### Async Benchmark

```python
import pytest
from tests.benchmark import Benchmark

@pytest.mark.asyncio
async def test_async_feature_performance():
    """Benchmark async feature."""
    benchmark = Benchmark("async_feature")

    async def operation():
        await my_async_feature.do_something()

    result = await benchmark.run_async(operation, iterations=5000)

    assert result.mean_time < 0.001, \
        f"Too slow: {result.mean_time*1000:.2f}ms"
```

### Comparison Benchmark

```python
def test_optimization_comparison():
    """Compare old vs new implementation."""
    benchmark = Benchmark("optimization")

    comparison = benchmark.compare(
        old_implementation,
        new_implementation,
        iterations=10000,
        name1="v1_baseline",
        name2="v2_optimized"
    )

    # Ensure new version is faster
    assert comparison['speedup'] > 1.5, \
        f"Insufficient improvement: {comparison['speedup']:.2f}x"

    print(f"Speedup: {comparison['speedup']:.2f}x")
    print(f"Improvement: {comparison['improvement_percent']:.1f}%")
```

### Memory Benchmark

```python
from tests.benchmark import MemoryBenchmark

def test_memory_usage():
    """Benchmark memory usage."""
    def operation():
        data = create_large_dataset()
        process_data(data)

    stats = MemoryBenchmark.measure_memory(operation, iterations=100)

    # Assert memory constraints
    assert stats['mean_mb'] < 100, \
        f"Too much memory: {stats['mean_mb']:.2f} MB"

    print(f"Memory usage: {stats['mean_mb']:.2f} MB")
```

### Using pytest-benchmark

```python
import pytest

def test_with_pytest_benchmark(benchmark):
    """Use pytest-benchmark fixture."""
    result = benchmark(my_function, arg1, arg2)

    # pytest-benchmark automatically handles iterations,
    # warmup, and statistics

    assert result == expected_value
```

## Best Practices

### 1. **Consistent Environment**

```bash
# Disable CPU frequency scaling (Linux)
sudo cpupower frequency-set --governor performance

# Close unnecessary applications
# Run on dedicated hardware for accurate results
```

### 2. **Warmup Iterations**

```python
# Always include warmup to avoid cold start bias
result = benchmark.run(
    func,
    iterations=10000,
    warmup=100  # Warmup iterations
)
```

### 3. **Multiple Iterations**

```python
# Use enough iterations for statistical significance
# Minimum: 1000 iterations
# Recommended: 10,000+ iterations
result = benchmark.run(func, iterations=10000)
```

### 4. **Garbage Collection**

```python
import gc

# Force GC before benchmarking
gc.collect()

result = benchmark.run(func, iterations=10000)
```

### 5. **Realistic Scenarios**

```python
# Benchmark with real-world data
def test_realistic_cache_usage():
    cache = LRUCache(capacity=10000)

    # Pre-populate with realistic data
    for i in range(1000):
        cache.put(f"key_{i}", generate_realistic_value())

    # Benchmark realistic access pattern
    def operation():
        # 80% reads, 20% writes (typical ratio)
        if random.random() < 0.8:
            cache.get(f"key_{random.randint(0, 999)}")
        else:
            cache.put(f"key_new_{random.randint(0, 999)}", "value")

    result = benchmark.run(operation, iterations=100000)
```

### 6. **Statistical Significance**

```python
# Check standard deviation
result = benchmark.run(func, iterations=10000)

# High stddev indicates unstable performance
if result.stddev / result.mean_time > 0.1:  # >10% variance
    print(f"⚠ Warning: High variance ({result.stddev/result.mean_time:.1%})")
```

## Interpreting Results

### Understanding Metrics

```
Benchmark: cache_operations
Iterations: 10000
Total Time: 0.0301s
Min: 2.10μs | Max: 45.30μs     # Range shows best/worst case
Mean: 3.01μs | Median: 2.80μs  # Central tendency
P95: 4.50μs | P99: 7.20μs      # Tail latency (important!)
Stddev: 1.23μs                 # Consistency (lower is better)
Throughput: 332,226 ops/sec    # Overall capacity
```

**Key insights:**
- **Mean vs Median**: If mean >> median, you have outliers
- **P95/P99**: Critical for user experience (99% of requests are faster than this)
- **Stddev**: Lower means more consistent performance
- **Min/Max range**: Large range indicates variability

### Comparing Results

```python
# Example comparison output
Baseline:     10,000 ops/sec
Optimized:    15,000 ops/sec
Speedup:      1.5x
Improvement:  50%
```

**Decision criteria:**
- < 10% change: Likely noise/measurement error
- 10-20% change: Noticeable but may not be significant
- 20-50% change: Significant improvement/regression
- > 50% change: Major performance change

## Troubleshooting

### Benchmarks Are Slow

```bash
# Use quick mode
python scripts/run-benchmarks.py --quick

# Run specific test
pytest tests/benchmarks/test_algorithms_benchmarks.py::test_lrucache_performance
```

### Inconsistent Results

```bash
# Close other applications
# Disable CPU frequency scaling
# Increase iterations
python scripts/run-benchmarks.py --iterations 50000

# Check system load
top
```

### Memory Errors

```bash
# Reduce iterations for memory benchmarks
pytest tests/benchmarks/ -k "not memory"

# Or increase available memory
```

### CI Failures

```bash
# Benchmarks may fail in CI due to shared runners
# Review --threshold setting in .github/workflows/benchmarks.yml

# Consider adjusting targets for CI environment
if os.getenv("CI"):
    target_rps = 50000  # Lower target for CI
else:
    target_rps = 100000  # Higher target for local
```

## Future Enhancements

Planned improvements for Phase 2:

- [ ] **Continuous Benchmarking**: Real-time performance tracking
- [ ] **Comparative Analysis**: Compare across versions/commits
- [ ] **Flamegraphs**: CPU profiling visualization
- [ ] **Memory Profiling**: Detailed memory allocation tracking
- [ ] **Network Benchmarks**: HTTP endpoint load testing with Locust
- [ ] **Database Benchmarks**: Query performance with real PostgreSQL/Redis
- [ ] **Distributed Benchmarks**: Multi-node performance testing

## Resources

- **pytest-benchmark**: https://pytest-benchmark.readthedocs.io/
- **Locust**: https://locust.io/ (load testing)
- **memory_profiler**: https://pypi.org/project/memory-profiler/
- **py-spy**: https://github.com/benfred/py-spy (profiling)

---

**Phase 2.1: Performance Benchmarks** ✓ Complete

Next: Phase 2.2 - Scalability Guides
