"""
Cache Module.

Provides unified caching interface with:
- Multiple backends (Redis, Memcached, in-memory)
- Decorator-based caching
- TTL management
- Cache invalidation patterns
- Compression support
"""

from .backends import InMemoryCache, MemcachedBackend, RedisBackend
from .decorators import cache_result, memoize
from .manager import Cache, CacheManager

__all__ = [
    "CacheManager",
    "Cache",
    "RedisBackend",
    "MemcachedBackend",
    "InMemoryCache",
    "memoize",
    "cache_result",
]
