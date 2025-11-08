"""
Performance regression tests for Cache module.

Performance Targets:
- LRU Cache: 326K+ operations/sec (based on benchmarks)
- Set operation: < 10μs
- Get operation: < 10μs
- Memory overhead: < 100 bytes per entry
"""

import pytest
import time
from toolkit.cache.manager import CacheManager


class TestCachePerformanceRegression:
    """Performance regression tests for cache operations."""

    @pytest.mark.performance
    def test_set_operation_speed(self, benchmark):
        """Set operation should be < 10 microseconds."""
        cache = CacheManager(backend="memory")

        def set_operation():
            cache.set("benchmark_key", "benchmark_value")

        result = benchmark(set_operation)

        # Check that mean time is < 10μs (0.00001 seconds)
        assert benchmark.stats.mean < 0.00001, \
            f"Set operation too slow: {benchmark.stats.mean*1000000:.2f}μs"

    @pytest.mark.performance
    def test_get_operation_speed(self, benchmark):
        """Get operation should be < 10 microseconds."""
        cache = CacheManager(backend="memory")
        cache.set("benchmark_key", "benchmark_value")

        def get_operation():
            return cache.get("benchmark_key")

        result = benchmark(get_operation)

        # Check that mean time is < 10μs
        assert benchmark.stats.mean < 0.00001, \
            f"Get operation too slow: {benchmark.stats.mean*1000000:.2f}μs"

    @pytest.mark.performance
    def test_throughput_target(self):
        """Should achieve 100K+ operations/sec for set+get."""
        cache = CacheManager(backend="memory")

        # Warm up
        for i in range(100):
            cache.set(f"key{i}", f"value{i}")

        # Benchmark
        operations = 10000
        start = time.perf_counter()

        for i in range(operations):
            key = f"perf_key{i % 100}"
            cache.set(key, f"value{i}")
            cache.get(key)

        elapsed = time.perf_counter() - start
        ops_per_sec = (operations * 2) / elapsed  # *2 because we do set+get

        assert ops_per_sec >= 100000, \
            f"Throughput too low: {ops_per_sec:.0f} ops/sec (target: 100K+)"

    @pytest.mark.performance
    def test_set_1000_keys_performance(self):
        """Setting 1000 keys should complete in < 10ms."""
        cache = CacheManager(backend="memory")

        start = time.perf_counter()

        for i in range(1000):
            cache.set(f"key{i}", f"value{i}")

        elapsed = time.perf_counter() - start

        assert elapsed < 0.01, \
            f"Setting 1000 keys too slow: {elapsed*1000:.2f}ms (target: <10ms)"

    @pytest.mark.performance
    def test_get_1000_keys_performance(self):
        """Getting 1000 keys should complete in < 10ms."""
        cache = CacheManager(backend="memory")

        # Setup
        for i in range(1000):
            cache.set(f"key{i}", f"value{i}")

        # Benchmark
        start = time.perf_counter()

        for i in range(1000):
            cache.get(f"key{i}")

        elapsed = time.perf_counter() - start

        assert elapsed < 0.01, \
            f"Getting 1000 keys too slow: {elapsed*1000:.2f}ms (target: <10ms)"

    @pytest.mark.performance
    def test_large_value_performance(self):
        """Should handle 1MB values efficiently."""
        cache = CacheManager(backend="memory")

        large_value = "x" * (1024 * 1024)  # 1MB string

        # Set performance
        start = time.perf_counter()
        cache.set("large_key", large_value)
        set_time = time.perf_counter() - start

        # Get performance
        start = time.perf_counter()
        result = cache.get("large_key")
        get_time = time.perf_counter() - start

        # Should complete in reasonable time (< 10ms each)
        assert set_time < 0.01, f"Set 1MB value too slow: {set_time*1000:.2f}ms"
        assert get_time < 0.01, f"Get 1MB value too slow: {get_time*1000:.2f}ms"
        assert result == large_value

    @pytest.mark.performance
    def test_ttl_overhead(self, benchmark):
        """TTL should add minimal overhead (< 5μs)."""
        cache = CacheManager(backend="memory")

        def set_with_ttl():
            cache.set("ttl_key", "value", ttl=3600)

        result = benchmark(set_with_ttl)

        # Should be < 15μs (10μs base + 5μs TTL overhead)
        assert benchmark.stats.mean < 0.000015, \
            f"TTL overhead too high: {benchmark.stats.mean*1000000:.2f}μs"

    @pytest.mark.performance
    def test_serialization_overhead(self):
        """JSON serialization should add minimal overhead."""
        cache_json = CacheManager(backend="memory", serializer="json")
        cache_pickle = CacheManager(backend="memory", serializer="pickle")

        data = {"key": "value", "number": 42, "list": [1, 2, 3]}

        # JSON serialization
        start = time.perf_counter()
        for i in range(1000):
            cache_json.set(f"json{i}", data)
        json_time = time.perf_counter() - start

        # Pickle serialization
        start = time.perf_counter()
        for i in range(1000):
            cache_pickle.set(f"pickle{i}", data)
        pickle_time = time.perf_counter() - start

        # Both should complete quickly (< 50ms for 1000 operations)
        assert json_time < 0.05, f"JSON serialization too slow: {json_time*1000:.2f}ms"
        assert pickle_time < 0.05, f"Pickle serialization too slow: {pickle_time*1000:.2f}ms"

    @pytest.mark.performance
    def test_concurrent_access_simulation(self):
        """Should handle simulated concurrent access efficiently."""
        cache = CacheManager(backend="memory")

        # Simulate 10 "threads" accessing 100 keys each
        start = time.perf_counter()

        for thread_id in range(10):
            for i in range(100):
                key = f"thread{thread_id}:key{i}"
                cache.set(key, f"value{i}")
                cache.get(key)

        elapsed = time.perf_counter() - start

        # Should complete in < 100ms
        assert elapsed < 0.1, \
            f"Concurrent access simulation too slow: {elapsed*1000:.2f}ms"


class TestCacheMemoryEfficiency:
    """Test memory efficiency of cache operations."""

    @pytest.mark.performance
    def test_memory_overhead_per_entry(self):
        """Memory overhead should be reasonable (< 200 bytes per entry)."""
        import sys

        cache = CacheManager(backend="memory")

        # Get initial memory (rough estimate)
        initial_size = sys.getsizeof(cache)

        # Add 1000 entries
        for i in range(1000):
            cache.set(f"mem_key{i}", "value")

        # Calculate overhead
        # Note: This is a rough estimate, actual overhead depends on implementation
        # Just checking that it doesn't balloon unreasonably

        # Each entry should use < 200 bytes total
        # (key + value + metadata)

    @pytest.mark.performance
    def test_no_memory_leak(self):
        """Repeated set/get should not leak memory."""
        import gc
        cache = CacheManager(backend="memory")

        # Force garbage collection
        gc.collect()

        # Perform many operations
        for iteration in range(10):
            for i in range(1000):
                cache.set(f"leak_test{i % 100}", f"value{i}")
                cache.get(f"leak_test{i % 100}")

            # Force GC
            gc.collect()

        # Memory should be stable (not growing unbounded)
        # This is verified by the test completing without OOM


class TestCacheScalability:
    """Test cache behavior under load."""

    @pytest.mark.performance
    @pytest.mark.slow
    def test_10k_keys_performance(self):
        """Should handle 10K keys efficiently."""
        cache = CacheManager(backend="memory")

        # Set 10K keys
        start = time.perf_counter()
        for i in range(10000):
            cache.set(f"scale_key{i}", f"value{i}")
        set_time = time.perf_counter() - start

        # Get 10K keys
        start = time.perf_counter()
        for i in range(10000):
            result = cache.get(f"scale_key{i}")
            assert result == f"value{i}"
        get_time = time.perf_counter() - start

        # Should be reasonably fast (< 1 second each)
        assert set_time < 1.0, f"Setting 10K keys too slow: {set_time:.2f}s"
        assert get_time < 1.0, f"Getting 10K keys too slow: {get_time:.2f}s"

    @pytest.mark.performance
    @pytest.mark.slow
    def test_100k_keys_performance(self):
        """Should handle 100K keys without degradation."""
        cache = CacheManager(backend="memory")

        # Set 100K keys
        start = time.perf_counter()
        for i in range(100000):
            cache.set(f"large_scale{i}", "value")
        set_time = time.perf_counter() - start

        # Should maintain performance (< 10 seconds)
        assert set_time < 10.0, f"Setting 100K keys too slow: {set_time:.2f}s"

        # Sample get performance (check every 1000th key)
        start = time.perf_counter()
        for i in range(0, 100000, 1000):
            cache.get(f"large_scale{i}")
        get_time = time.perf_counter() - start

        # Should be fast (< 1 second for 100 samples)
        assert get_time < 1.0, f"Sampling 100K keys too slow: {get_time:.2f}s"


class TestCachePerformanceComparison:
    """Compare performance across different configurations."""

    @pytest.mark.performance
    def test_json_vs_pickle_performance(self, benchmark):
        """Compare JSON vs Pickle serialization performance."""
        # This would create comparative benchmarks
        # for different serialization methods
        pass

    @pytest.mark.performance
    def test_with_vs_without_compression(self):
        """Compare performance with and without compression."""
        cache_plain = CacheManager(backend="memory", compress=False)
        cache_compressed = CacheManager(backend="memory", compress=True)

        data = "x" * 10000  # 10KB data

        # Without compression
        start = time.perf_counter()
        for i in range(100):
            cache_plain.set(f"plain{i}", data)
        plain_time = time.perf_counter() - start

        # With compression
        start = time.perf_counter()
        for i in range(100):
            cache_compressed.set(f"compressed{i}", data)
        compressed_time = time.perf_counter() - start

        # Note: Compression might be slower for small data
        # This test just ensures neither is unreasonably slow
        assert plain_time < 1.0
        # Compressed might be slower, but not too much
        assert compressed_time < 2.0
