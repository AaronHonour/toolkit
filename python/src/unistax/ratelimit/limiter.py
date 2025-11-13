"""Rate limiter implementation."""

from collections.abc import Callable
from functools import wraps
from typing import Any

from .algorithms import TokenBucket


class RateLimiter:
    """Rate limiter with configurable algorithms.

    Examples:
        >>> limiter = RateLimiter(rate=100, period=60)  # 100 requests per minute
        >>> if limiter.is_allowed("user:123"):
        ...     process_request()
    """

    def __init__(self, rate: int = 100, period: int = 60) -> None:
        """Initialize rate limiter.

        Args:
            rate: Number of allowed requests
            period: Time period in seconds
        """
        self.rate = rate
        self.period = period
        self._buckets: dict[str, TokenBucket] = {}

    def _get_bucket(self, key: str) -> TokenBucket:
        """Get or create token bucket for key."""
        if key not in self._buckets:
            self._buckets[key] = TokenBucket(self.rate, self.period)
        return self._buckets[key]

    def is_allowed(self, key: str) -> bool:
        """Check if request is allowed.

        Args:
            key: Identifier (e.g., user ID, IP address)

        Returns:
            True if allowed
        """
        bucket = self._get_bucket(key)
        return bucket.consume()

    def limit(self, key_func: Callable[..., Any]| None = None) -> Callable[..., Any]:
        """Decorator for rate limiting functions.

        Args:
            key_func: Function to extract key from arguments

        Examples:
            >>> @limiter.limit(key_func=lambda user_id: f"user:{user_id}")
            ... def api_endpoint(user_id):
            ...     pass
        """

        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            @wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                # Extract key
                if key_func:
                    key = key_func(*args, **kwargs)
                else:
                    key = func.__name__

                if not self.is_allowed(key):
                    raise Exception(f"Rate limit exceeded for {key}")

                return func(*args, **kwargs)

            return wrapper

        return decorator


# Convenience alias
RateLimit = RateLimiter
