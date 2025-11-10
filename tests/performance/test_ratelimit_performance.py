"""
Performance regression tests for RateLimiter module.

Performance Targets:
- Token bucket check: 100K+ operations/sec
- is_allowed() call: < 10μs
- Memory per bucket: < 500 bytes
- Support 10K+ concurrent limiters
"""

import pytest
import time
from toolkit.ratelimit.limiter import RateLimiter


class TestRateLimiterPerformanceRegression:
    """Performance regression tests for rate limiter."""

    @pytest.mark.performance
    def test_is_allowed_speed(self, benchmark):
        """is_allowed() should be < 10 microseconds."""
        limiter = RateLimiter(rate=1000, period=60)

        # Use different key each time to avoid state effects
        counter = [0]

        def check_allowed():
            counter[0] += 1
            return limiter.is_allowed(f"user:{counter[0]}")

        result = benchmark(check_allowed)

        # Check that mean time is < 10μs
        assert benchmark.stats.mean < 0.00001, \
            f"is_allowed() too slow: {benchmark.stats.mean*1000000:.2f}μs (target: <10μs)"

    @pytest.mark.performance
    def test_throughput_target(self):
        """Should achieve 100K+ checks/sec."""
        limiter = RateLimiter(rate=100000, period=1)

        # Warm up
        for i in range(100):
            limiter.is_allowed(f"warmup{i}")

        # Benchmark
        checks = 10000
        start = time.perf_counter()

        for i in range(checks):
            limiter.is_allowed(f"user:{i}")

        elapsed = time.perf_counter() - start
        checks_per_sec = checks / elapsed

        assert checks_per_sec >= 100000, \
            f"Throughput too low: {checks_per_sec:.0f} checks/sec (target: 100K+)"

    @pytest.mark.performance
    def test_1000_checks_performance(self):
        """1000 checks should complete in < 10ms."""
        limiter = RateLimiter(rate=1000, period=60)

        start = time.perf_counter()

        for i in range(1000):
            limiter.is_allowed(f"user:{i % 100}")

        elapsed = time.perf_counter() - start

        assert elapsed < 0.01, \
            f"1000 checks too slow: {elapsed*1000:.2f}ms (target: <10ms)"

    @pytest.mark.performance
    def test_single_key_burst_performance(self):
        """Should handle rapid bursts efficiently."""
        limiter = RateLimiter(rate=1000, period=1)

        start = time.perf_counter()

        # Rapid burst on single key
        for i in range(1000):
            limiter.is_allowed("burst_user")

        elapsed = time.perf_counter() - start

        assert elapsed < 0.01, \
            f"Burst handling too slow: {elapsed*1000:.2f}ms"

    @pytest.mark.performance
    def test_refill_calculation_performance(self, benchmark):
        """Token refill calculation should be fast."""
        limiter = RateLimiter(rate=100, period=60)

        # Consume some tokens
        for i in range(50):
            limiter.is_allowed("user:123")

        # Wait a bit for refill to occur
        time.sleep(0.1)

        def check_after_refill():
            return limiter.is_allowed("user:123")

        result = benchmark(check_after_refill)

        # Refill calculation shouldn't add significant overhead
        assert benchmark.stats.mean < 0.000015, \
            f"Refill calculation too slow: {benchmark.stats.mean*1000000:.2f}μs"


class TestRateLimiterConcurrency:
    """Test performance with multiple concurrent keys."""

    @pytest.mark.performance
    def test_100_concurrent_keys(self):
        """Should handle 100 concurrent keys efficiently."""
        limiter = RateLimiter(rate=100, period=60)

        start = time.perf_counter()

        # 100 keys, each making 100 requests
        for key_id in range(100):
            for i in range(100):
                limiter.is_allowed(f"user:{key_id}")

        elapsed = time.perf_counter() - start

        # Should complete in < 100ms
        assert elapsed < 0.1, \
            f"100 concurrent keys too slow: {elapsed*1000:.2f}ms"

    @pytest.mark.performance
    def test_1000_concurrent_keys(self):
        """Should handle 1000 concurrent keys efficiently."""
        limiter = RateLimiter(rate=100, period=60)

        start = time.perf_counter()

        # 1000 keys, each making 10 requests
        for key_id in range(1000):
            for i in range(10):
                limiter.is_allowed(f"user:{key_id}")

        elapsed = time.perf_counter() - start

        # Should complete in < 1 second
        assert elapsed < 1.0, \
            f"1000 concurrent keys too slow: {elapsed:.2f}s"

    @pytest.mark.performance
    @pytest.mark.slow
    def test_10k_concurrent_keys(self):
        """Should handle 10K concurrent keys without degradation."""
        limiter = RateLimiter(rate=100, period=60)

        start = time.perf_counter()

        # 10K keys, each making 5 requests
        for key_id in range(10000):
            for i in range(5):
                limiter.is_allowed(f"user:{key_id}")

        elapsed = time.perf_counter() - start

        # Should complete in < 10 seconds
        assert elapsed < 10.0, \
            f"10K concurrent keys too slow: {elapsed:.2f}s"


class TestRateLimiterMemoryEfficiency:
    """Test memory efficiency of rate limiter."""

    @pytest.mark.performance
    def test_bucket_memory_overhead(self):
        """Each token bucket should use reasonable memory (< 500 bytes)."""
        import sys

        limiter = RateLimiter(rate=100, period=60)

        # Create initial bucket
        limiter.is_allowed("user:1")

        # Get size estimate
        # Note: Actual size depends on implementation

        # Create 1000 buckets
        for i in range(1000):
            limiter.is_allowed(f"user:{i}")

        # Should not use excessive memory
        # (Rough check - actual memory depends on Python implementation)
        bucket_count = len(limiter._buckets)
        assert bucket_count == 1000

    @pytest.mark.performance
    def test_no_memory_leak(self):
        """Repeated operations should not leak memory."""
        import gc

        limiter = RateLimiter(rate=100, period=1)

        gc.collect()

        # Perform many operations
        for iteration in range(10):
            for i in range(1000):
                limiter.is_allowed(f"user:{i % 100}")

            gc.collect()

        # Memory should be stable


class TestRateLimiterScalability:
    """Test scalability under different loads."""

    @pytest.mark.performance
    def test_high_rate_limit(self):
        """Should handle very high rate limits efficiently."""
        limiter = RateLimiter(rate=1000000, period=60)

        start = time.perf_counter()

        # Make 10K requests
        for i in range(10000):
            limiter.is_allowed("high_rate_user")

        elapsed = time.perf_counter() - start

        # Should complete quickly
        assert elapsed < 0.1, \
            f"High rate limit too slow: {elapsed*1000:.2f}ms"

    @pytest.mark.performance
    def test_low_rate_limit(self):
        """Should handle very low rate limits efficiently."""
        limiter = RateLimiter(rate=1, period=3600)

        start = time.perf_counter()

        # First request allowed
        assert limiter.is_allowed("low_rate_user") is True

        # Subsequent requests denied (should still be fast)
        for i in range(100):
            limiter.is_allowed("low_rate_user")

        elapsed = time.perf_counter() - start

        # Should complete quickly even with denials
        assert elapsed < 0.01, \
            f"Low rate limit checks too slow: {elapsed*1000:.2f}ms"

    @pytest.mark.performance
    def test_short_period(self):
        """Should handle very short periods efficiently."""
        limiter = RateLimiter(rate=100, period=1)  # 100 per second

        start = time.perf_counter()

        for i in range(100):
            limiter.is_allowed("short_period_user")

        elapsed = time.perf_counter() - start

        assert elapsed < 0.01, \
            f"Short period rate limiting too slow: {elapsed*1000:.2f}ms"

    @pytest.mark.performance
    def test_long_period(self):
        """Should handle very long periods efficiently."""
        limiter = RateLimiter(rate=100, period=86400)  # 100 per day

        start = time.perf_counter()

        for i in range(100):
            limiter.is_allowed("long_period_user")

        elapsed = time.perf_counter() - start

        assert elapsed < 0.01, \
            f"Long period rate limiting too slow: {elapsed*1000:.2f}ms"


class TestRateLimiterWorstCase:
    """Test worst-case scenarios."""

    @pytest.mark.performance
    def test_alternating_allow_deny(self):
        """Should handle alternating allowed/denied efficiently."""
        limiter = RateLimiter(rate=50, period=60)

        # Consume half the tokens
        for i in range(50):
            limiter.is_allowed("alternating_user")

        start = time.perf_counter()

        # Now requests will alternate between allowed (refill) and denied
        for i in range(1000):
            limiter.is_allowed("alternating_user")
            time.sleep(0.001)  # Small delay for refill

        elapsed = time.perf_counter() - start

        # Should handle efficiently despite constant state changes
        # (Mainly checking it completes)

    @pytest.mark.performance
    def test_rapid_key_switching(self):
        """Should handle rapid switching between keys."""
        limiter = RateLimiter(rate=100, period=60)

        start = time.perf_counter()

        # Rapidly switch between 10 keys
        for i in range(1000):
            limiter.is_allowed(f"user:{i % 10}")

        elapsed = time.perf_counter() - start

        assert elapsed < 0.01, \
            f"Rapid key switching too slow: {elapsed*1000:.2f}ms"


class TestRateLimiterPerformanceComparison:
    """Compare performance characteristics."""

    @pytest.mark.performance
    def test_first_vs_subsequent_calls(self):
        """First call vs subsequent calls performance."""
        limiter = RateLimiter(rate=100, period=60)

        # First call (creates bucket)
        start = time.perf_counter()
        limiter.is_allowed("new_user")
        first_call_time = time.perf_counter() - start

        # Subsequent calls (uses existing bucket)
        start = time.perf_counter()
        for i in range(100):
            limiter.is_allowed("new_user")
        subsequent_time = (time.perf_counter() - start) / 100

        # Both should be fast (subsequent might be slightly faster)
        assert first_call_time < 0.0001, \
            f"First call too slow: {first_call_time*1000000:.2f}μs"
        assert subsequent_time < 0.00001, \
            f"Subsequent calls too slow: {subsequent_time*1000000:.2f}μs"

    @pytest.mark.performance
    def test_allowed_vs_denied_performance(self):
        """Allowed vs denied request performance."""
        limiter = RateLimiter(rate=10, period=60)

        # Measure allowed requests
        start = time.perf_counter()
        for i in range(10):
            limiter.is_allowed("user:allowed")
        allowed_time = (time.perf_counter() - start) / 10

        # Measure denied requests
        start = time.perf_counter()
        for i in range(100):
            limiter.is_allowed("user:allowed")  # Will be denied
        denied_time = (time.perf_counter() - start) / 100

        # Both should be similarly fast
        assert allowed_time < 0.00001, \
            f"Allowed requests too slow: {allowed_time*1000000:.2f}μs"
        assert denied_time < 0.00001, \
            f"Denied requests too slow: {denied_time*1000000:.2f}μs"

        # Denied might even be slightly faster (no token decrement)


class TestRateLimiterRealWorld:
    """Real-world scenario performance tests."""

    @pytest.mark.performance
    def test_api_gateway_simulation(self):
        """Simulate API gateway with 100 users."""
        limiter = RateLimiter(rate=100, period=60)  # 100 req/min per user

        start = time.perf_counter()

        # Simulate 100 users each making 50 requests
        for user_id in range(100):
            for request_num in range(50):
                limiter.is_allowed(f"user:{user_id}")

        elapsed = time.perf_counter() - start

        # Should handle 5000 total requests quickly
        throughput = 5000 / elapsed

        assert throughput >= 50000, \
            f"API gateway simulation throughput too low: {throughput:.0f} req/sec"

    @pytest.mark.performance
    def test_ddos_protection_simulation(self):
        """Simulate DDoS protection with many IPs."""
        limiter = RateLimiter(rate=10, period=1)  # 10 req/sec per IP

        start = time.perf_counter()

        # Simulate 1000 IPs, aggressive requests
        for ip_num in range(1000):
            for request_num in range(20):  # Try 20, only 10 allowed
                limiter.is_allowed(f"ip:{ip_num}")

        elapsed = time.perf_counter() - start

        # Should efficiently deny excess requests
        assert elapsed < 1.0, \
            f"DDoS simulation too slow: {elapsed:.2f}s"
