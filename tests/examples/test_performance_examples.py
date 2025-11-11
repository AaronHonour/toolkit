"""Example performance tests demonstrating the framework."""

import pytest
import time
from tests.benchmark import Benchmark, MemoryBenchmark
from tests.factories import StringFactory, NumberFactory
from tests.utils import assert_time_limit, PerformanceAssertion
from unistax.performance import MultiLevelCache, BatchProcessor


class TestCachePerformance:
    """Example cache performance tests."""

    def test_cache_latency_benchmark(self):
        """Benchmark cache get/set operations."""
        cache = MultiLevelCache(l1_max_size=1000)

        benchmark = Benchmark("cache_operations")

        # Benchmark cache set
        def cache_set():
            cache.set("test_key", "test_value", ttl=300)

        result = benchmark.run(cache_set, iterations=1000, name="cache_set")
        print(result)

        # Assert p95 latency is under 1ms
        assert result.p95_time < 0.001, f"Cache set p95 too slow: {result.p95_time*1000:.2f}ms"

        # Benchmark cache get
        def cache_get():
            cache.get("test_key")

        result = benchmark.run(cache_get, iterations=10000, name="cache_get")
        print(result)

        # Assert throughput is high enough
        assert result.ops_per_second > 10000, f"Cache throughput too low: {result.ops_per_second:.0f} ops/sec"

    def test_multilevel_cache_comparison(self):
        """Compare single-level vs multi-level cache."""
        benchmark = Benchmark("cache_comparison")

        # Single-level cache
        single_cache = {}
        def single_level_get():
            return single_cache.get("key1")

        # Multi-level cache
        multi_cache = MultiLevelCache(l1_max_size=100)
        multi_cache.set("key1", "value1")

        def multi_level_get():
            return multi_cache.get("key1")

        # Compare
        comparison = benchmark.compare(
            single_level_get,
            multi_level_get,
            iterations=10000,
            name1="single_level",
            name2="multi_level"
        )

        print(f"\nCache Comparison:")
        print(f"Speedup: {comparison['speedup']:.2f}x")
        print(f"Faster: {comparison['faster']}")

    def test_cache_memory_usage(self):
        """Test cache memory consumption."""
        cache = MultiLevelCache(l1_max_size=1000)

        def fill_cache():
            for i in range(1000):
                cache.set(f"key_{i}", f"value_{i}" * 100)

        memory_stats = MemoryBenchmark.measure_memory(fill_cache, iterations=10)
        print(f"\nCache Memory Usage: {memory_stats['mean_mb']:.2f}MB")

        # Assert memory usage is reasonable
        assert memory_stats['max_mb'] < 50, "Cache uses too much memory"


class TestBatchProcessingPerformance:
    """Example batch processing performance tests."""

    def test_batch_vs_individual_operations(self):
        """Compare batch vs individual database operations."""
        benchmark = Benchmark("batch_vs_individual")

        items = [{"id": i, "value": i * 2} for i in range(100)]

        # Simulate individual inserts
        def individual_operations():
            for item in items:
                time.sleep(0.001)  # Simulated DB operation

        # Simulate batch insert
        def batch_operation():
            # Process all at once
            time.sleep(0.001 * len(items) * 0.1)  # 10x faster

        result1 = benchmark.run(individual_operations, iterations=10, name="individual")
        result2 = benchmark.run(batch_operation, iterations=10, name="batch")

        speedup = result1.mean_time / result2.mean_time
        print(f"\nBatch Processing Speedup: {speedup:.2f}x")

        assert speedup > 5, "Batch processing should be significantly faster"

    def test_batch_processor_throughput(self):
        """Test batch processor throughput."""
        processed = []

        def process_batch(items):
            # Simulate batch processing
            processed.extend(items)
            return items

        processor = BatchProcessor(process_batch)
        processor.start()

        benchmark = Benchmark("batch_processor")

        def add_item():
            processor.add({"data": "test"}, timeout=1.0)

        result = benchmark.run(add_item, iterations=100, warmup=0)  # No warmup to get exact count

        processor.stop()

        print(f"\nBatch Processor Throughput: {result.ops_per_second:.0f} ops/sec")
        # Verify all items were processed (should be exactly 100 with warmup=0)
        assert len(processed) == 100, f"Expected 100 items, got {len(processed)}"


class TestPerformanceAssertions:
    """Example performance assertion tests."""

    def test_function_latency_assertion(self):
        """Test latency assertion helper."""
        def fast_function():
            time.sleep(0.001)

        # Assert p95 latency is under 5ms
        PerformanceAssertion.assert_latency_p95(fast_function, max_latency=0.005)

    def test_throughput_assertion(self):
        """Test throughput assertion helper."""
        counter = {"value": 0}

        def increment():
            counter["value"] += 1

        # Assert at least 1000 ops/sec
        PerformanceAssertion.assert_throughput(increment, min_rps=1000, duration=0.5)

    def test_time_limit_assertion(self):
        """Test time limit context manager."""
        with assert_time_limit(0.1, "fast operation"):
            time.sleep(0.05)  # Should pass

        # This would fail:
        # with assert_time_limit(0.01, "slow operation"):
        #     time.sleep(0.1)


@pytest.mark.benchmark
class TestBenchmarkExamples:
    """Benchmark test examples."""

    def test_string_operations_benchmark(self):
        """Benchmark string operations."""
        benchmark = Benchmark("string_operations")

        test_string = StringFactory.random_string(1000)

        # Benchmark different string operations
        benchmark.run(lambda: test_string.upper(), iterations=10000, name="upper")
        benchmark.run(lambda: test_string.lower(), iterations=10000, name="lower")
        benchmark.run(lambda: test_string.replace("a", "b"), iterations=10000, name="replace")
        benchmark.run(lambda: test_string.split(" "), iterations=10000, name="split")

        benchmark.print_summary()

    def test_list_operations_benchmark(self):
        """Benchmark list operations."""
        benchmark = Benchmark("list_operations")

        items = list(range(1000))

        # Benchmark different list operations
        benchmark.run(lambda: items.copy(), iterations=10000, name="copy")
        benchmark.run(lambda: sorted(items), iterations=1000, name="sort")
        benchmark.run(lambda: [x * 2 for x in items], iterations=1000, name="comprehension")
        benchmark.run(lambda: list(map(lambda x: x * 2, items)), iterations=1000, name="map")

        benchmark.print_summary()


if __name__ == "__main__":
    # Run benchmarks directly
    pytest.main([__file__, "-v", "-s"])
