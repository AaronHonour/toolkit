"""
Decorators for caching function results.

Provides convenient decorators for memoization.
"""

from functools import wraps
from typing import Any, Callable, Optional

from .manager import get_cache


def memoize(
    ttl: Optional[int] = None,
    key_prefix: str = "",
    key_func: Optional[Callable] = None,
) -> Callable:
    """
    Decorator for memoizing function results.

    Args:
        ttl: Time to live in seconds
        key_prefix: Prefix for cache keys
        key_func: Custom function to generate cache key

    Examples:
        >>> @memoize(ttl=3600, key_prefix="user")
        ... def get_user(user_id):
        ...     return db.query(user_id)
    """
    cache = get_cache()
    return cache.memoize(ttl=ttl, key_prefix=key_prefix, key_func=key_func)


def cache_result(ttl: Optional[int] = None, key: Optional[str] = None) -> Callable:
    """
    Decorator to cache function result with fixed key.

    Args:
        ttl: Time to live in seconds
        key: Cache key (uses function name if None)

    Examples:
        >>> @cache_result(ttl=300, key="latest_users")
        ... def get_latest_users():
        ...     return db.query("SELECT * FROM users ORDER BY created_at DESC LIMIT 10")
    """

    def decorator(func: Callable) -> Callable:
        cache = get_cache()
        cache_key = key or func.__name__

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Try cache first
            result = cache.get(cache_key)
            if result is not None:
                return result

            # Call function and cache
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            return result

        # Add cache control
        wrapper.cache_clear = lambda: cache.delete(cache_key)
        wrapper.cache_key = cache_key

        return wrapper

    return decorator
