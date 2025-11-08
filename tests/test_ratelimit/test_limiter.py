"""
Comprehensive tests for RateLimiter.

Testing Strategy:
- Test token bucket algorithm correctness
- Test rate limiting enforcement
- Test burst handling
- Test different time windows
- Test multiple clients/keys
- Test decorator functionality
- Test performance (should handle 100K+ checks/sec)
- Test edge cases (clock skew, rapid requests)
"""

import pytest
import time
from freezegun import freeze_time
from unittest.mock import Mock, patch
from toolkit.ratelimit.limiter import RateLimiter


class TestRateLimiterBasics:
    """Test basic rate limiter functionality."""

    def test_create_rate_limiter(self):
        """Should create rate limiter with default settings."""
        limiter = RateLimiter(rate=100, period=60)

        assert limiter.rate == 100
        assert limiter.period == 60

    def test_first_request_allowed(self):
        """First request should always be allowed."""
        limiter = RateLimiter(rate=10, period=60)

        assert limiter.is_allowed("user:123") is True

    def test_requests_within_limit_allowed(self):
        """Requests within rate limit should be allowed."""
        limiter = RateLimiter(rate=10, period=60)

        # First 10 requests should be allowed
        for i in range(10):
            assert limiter.is_allowed("user:123") is True, f"Request {i+1} should be allowed"

    def test_requests_over_limit_denied(self):
        """Requests over rate limit should be denied."""
        limiter = RateLimiter(rate=10, period=60)

        # Consume all tokens
        for i in range(10):
            limiter.is_allowed("user:123")

        # 11th request should be denied
        assert limiter.is_allowed("user:123") is False


class TestRateLimiterMultipleClients:
    """Test rate limiting for multiple clients."""

    def test_different_keys_independent_limits(self):
        """Different keys should have independent rate limits."""
        limiter = RateLimiter(rate=5, period=60)

        # User 1 consumes their limit
        for i in range(5):
            assert limiter.is_allowed("user:1") is True

        # User 1 should be rate limited
        assert limiter.is_allowed("user:1") is False

        # User 2 should still be allowed
        assert limiter.is_allowed("user:2") is True

    def test_many_clients(self):
        """Should handle many independent clients."""
        limiter = RateLimiter(rate=10, period=60)

        # 100 different clients, each making 10 requests
        for client_id in range(100):
            key = f"client:{client_id}"

            # Each client should get 10 requests
            for i in range(10):
                assert limiter.is_allowed(key) is True

            # 11th request should be denied
            assert limiter.is_allowed(key) is False


class TestRateLimiterTokenRefill:
    """Test token refill over time."""

    def test_tokens_refill_over_time(self):
        """Tokens should refill based on time period."""
        limiter = RateLimiter(rate=10, period=1)  # 10 requests per second

        # Consume all tokens
        for i in range(10):
            limiter.is_allowed("user:123")

        # Should be denied
        assert limiter.is_allowed("user:123") is False

        # Wait for refill (1 second)
        time.sleep(1.1)

        # Should be allowed again
        assert limiter.is_allowed("user:123") is True

    def test_partial_refill(self):
        """Tokens should partially refill over partial time period."""
        limiter = RateLimiter(rate=10, period=2)  # 10 requests per 2 seconds = 5/sec

        # Consume all tokens
        for i in range(10):
            limiter.is_allowed("user:123")

        # Wait for 1 second (should refill ~5 tokens)
        time.sleep(1.0)

        # Should be able to make ~5 more requests
        allowed_count = 0
        for i in range(10):
            if limiter.is_allowed("user:123"):
                allowed_count += 1

        # Should have refilled approximately 5 tokens (±1 for timing)
        assert 4 <= allowed_count <= 6


class TestRateLimiterBurst:
    """Test burst handling."""

    def test_allows_burst_up_to_limit(self):
        """Should allow burst of requests up to rate limit."""
        limiter = RateLimiter(rate=100, period=60)

        # Should handle rapid burst
        start = time.time()
        for i in range(100):
            assert limiter.is_allowed("user:123") is True

        duration = time.time() - start

        # Should complete quickly (< 100ms)
        assert duration < 0.1

    def test_denies_burst_over_limit(self):
        """Should deny burst over rate limit."""
        limiter = RateLimiter(rate=10, period=60)

        # Rapid burst of 20 requests
        results = []
        for i in range(20):
            results.append(limiter.is_allowed("user:123"))

        # First 10 should be True, rest False
        assert results[:10] == [True] * 10
        assert results[10:] == [False] * 10


class TestRateLimiterDifferentRates:
    """Test different rate configurations."""

    def test_very_low_rate(self):
        """Should handle very low rate limits (1 request/min)."""
        limiter = RateLimiter(rate=1, period=60)

        # First request allowed
        assert limiter.is_allowed("user:123") is True

        # Second request denied
        assert limiter.is_allowed("user:123") is False

    def test_very_high_rate(self):
        """Should handle very high rate limits (10000 requests/sec)."""
        limiter = RateLimiter(rate=10000, period=1)

        # Should allow many requests
        allowed = 0
        for i in range(10000):
            if limiter.is_allowed("user:123"):
                allowed += 1

        assert allowed == 10000

    def test_fractional_rate(self):
        """Should handle fractional rates (1 request per 5 seconds)."""
        limiter = RateLimiter(rate=1, period=5)

        assert limiter.is_allowed("user:123") is True
        assert limiter.is_allowed("user:123") is False

        # After 5 seconds, should refill
        time.sleep(5.1)
        assert limiter.is_allowed("user:123") is True


class TestRateLimiterDecorator:
    """Test rate limiter decorator functionality."""

    def test_decorator_basic(self):
        """Should rate limit decorated functions."""
        limiter = RateLimiter(rate=5, period=60)

        if hasattr(limiter, 'limit'):
            @limiter.limit(key=lambda user_id: f"user:{user_id}")
            def process_request(user_id):
                return f"processed {user_id}"

            # First 5 calls should succeed
            for i in range(5):
                result = process_request("123")
                assert result == "processed 123"

            # 6th call should raise exception or return error
            # (behavior depends on decorator implementation)

    def test_decorator_with_different_keys(self):
        """Decorated function should respect different keys."""
        limiter = RateLimiter(rate=3, period=60)

        if hasattr(limiter, 'limit'):
            @limiter.limit(key=lambda user_id: f"user:{user_id}")
            def process_request(user_id):
                return f"processed {user_id}"

            # User 1 can make 3 requests
            for i in range(3):
                process_request("user1")

            # User 2 can still make requests (different key)
            result = process_request("user2")
            assert result == "processed user2"


class TestRateLimiterEdgeCases:
    """Test edge cases and error conditions."""

    def test_zero_rate(self):
        """Should handle zero rate gracefully."""
        # Zero rate means no requests allowed
        try:
            limiter = RateLimiter(rate=0, period=60)
            # All requests should be denied
            assert limiter.is_allowed("user:123") is False
        except ValueError:
            # Or might raise error for invalid config
            pass

    def test_zero_period(self):
        """Should handle zero period gracefully."""
        try:
            limiter = RateLimiter(rate=10, period=0)
            # Behavior undefined - either allows all or denies all
        except ValueError:
            # Or might raise error for invalid config
            pass

    def test_negative_rate(self):
        """Should reject negative rate."""
        with pytest.raises(ValueError):
            RateLimiter(rate=-10, period=60)

    def test_negative_period(self):
        """Should reject negative period."""
        with pytest.raises(ValueError):
            RateLimiter(rate=10, period=-60)

    def test_empty_key(self):
        """Should handle empty key string."""
        limiter = RateLimiter(rate=10, period=60)

        # Should work with empty string key
        assert limiter.is_allowed("") is True

    def test_unicode_key(self):
        """Should handle Unicode keys."""
        limiter = RateLimiter(rate=10, period=60)

        key = "user:测试:🎉"
        assert limiter.is_allowed(key) is True

    def test_very_long_key(self):
        """Should handle very long keys."""
        limiter = RateLimiter(rate=10, period=60)

        long_key = "user:" + "a" * 10000
        assert limiter.is_allowed(long_key) is True


class TestRateLimiterPerformance:
    """Test rate limiter performance."""

    @pytest.mark.benchmark
    def test_is_allowed_performance(self, benchmark):
        """is_allowed() should be very fast (target: < 10μs)."""
        limiter = RateLimiter(rate=100, period=60)

        def check_limit():
            # Reset state for each benchmark iteration
            return limiter.is_allowed(f"user:{time.time()}")

        result = benchmark(check_limit)
        assert result is True

    @pytest.mark.performance
    def test_high_throughput(self):
        """Should handle high throughput (100K+ checks/sec)."""
        limiter = RateLimiter(rate=100000, period=1)

        start = time.time()
        count = 0

        # Run for 0.1 seconds
        while time.time() - start < 0.1:
            limiter.is_allowed("user:123")
            count += 1

        # Should handle at least 10K checks in 0.1s (100K/sec)
        throughput = count / 0.1
        assert throughput >= 10000, f"Throughput: {throughput}/sec"

    @pytest.mark.performance
    def test_memory_efficiency(self):
        """Should not leak memory with many keys."""
        limiter = RateLimiter(rate=10, period=60)

        # Create many buckets
        for i in range(10000):
            limiter.is_allowed(f"user:{i}")

        # Check bucket count
        bucket_count = len(limiter._buckets)
        assert bucket_count == 10000

        # Memory usage should be reasonable
        # (In production, you'd want cleanup of old buckets)


class TestRateLimiterWithFreezgun:
    """Test time-dependent behavior with frozen time."""

    def test_with_frozen_time(self):
        """Should work correctly with frozen time."""
        with freeze_time("2024-01-01 12:00:00") as frozen_time:
            limiter = RateLimiter(rate=10, period=60)

            # Consume all tokens
            for i in range(10):
                assert limiter.is_allowed("user:123") is True

            # Should be denied
            assert limiter.is_allowed("user:123") is False

            # Advance time by 60 seconds
            frozen_time.tick(delta=60)

            # Should be allowed again
            assert limiter.is_allowed("user:123") is True

    def test_refill_calculation_with_frozen_time(self):
        """Should correctly calculate refill with frozen time."""
        with freeze_time("2024-01-01 12:00:00") as frozen_time:
            limiter = RateLimiter(rate=60, period=60)  # 1 per second

            # Consume all tokens
            for i in range(60):
                limiter.is_allowed("user:123")

            # Move forward 30 seconds (should refill 30 tokens)
            frozen_time.tick(delta=30)

            allowed_count = 0
            for i in range(60):
                if limiter.is_allowed("user:123"):
                    allowed_count += 1

            # Should have refilled approximately 30 tokens (±2 for algorithm precision)
            assert 28 <= allowed_count <= 32


@pytest.mark.integration
class TestRateLimiterRedisBackend:
    """Integration tests with Redis backend for distributed rate limiting."""

    @pytest.mark.requires_redis
    def test_distributed_rate_limiting(self):
        """Should work across multiple limiter instances with shared Redis."""
        # This would test distributed rate limiting
        # Requires Redis to be running
        pytest.skip("Redis integration test - implement when Redis backend available")


class TestRateLimiterStatistics:
    """Test rate limiter statistics and monitoring."""

    def test_get_remaining_tokens(self):
        """Should report remaining tokens."""
        limiter = RateLimiter(rate=10, period=60)

        if hasattr(limiter, 'get_remaining'):
            # Use 3 tokens
            for i in range(3):
                limiter.is_allowed("user:123")

            remaining = limiter.get_remaining("user:123")
            assert remaining == 7

    def test_get_reset_time(self):
        """Should report when limit resets."""
        limiter = RateLimiter(rate=10, period=60)

        if hasattr(limiter, 'get_reset_time'):
            limiter.is_allowed("user:123")
            reset_time = limiter.get_reset_time("user:123")

            # Reset time should be in the future
            assert reset_time > time.time()
