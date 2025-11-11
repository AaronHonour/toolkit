"""
Cache Module.

Provides unified caching interface with:
- Multiple backends (Redis, Memcached, in-memory)
- Decorator-based caching
- TTL management
- Cache invalidation patterns
- Compression support
"""

from .manager import CacheManager, Cache
from .backends import RedisBackend, MemcachedBackend, InMemoryCache
from .decorators import memoize, cache_result

__all__ = [
    "CacheManager",
    "Cache",
    "RedisBackend",
    "MemcachedBackend",
    "InMemoryCache",
    "memoize",
    "cache_result",
]
