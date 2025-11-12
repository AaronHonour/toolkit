"""
Cache backends for different storage systems.

Provides backends for Redis, Memcached, and in-memory storage.
"""

import threading
import time
from abc import ABC, abstractmethod


class CacheBackend(ABC):
    """Abstract base class for cache backends."""

    @abstractmethod
    def get(self, key: str) -> bytes | None:
        """Get value from cache."""
        pass

    @abstractmethod
    def set(self, key: str, value: bytes, ttl: int | None = None) -> bool:
        """Set value in cache."""
        pass

    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete value from cache."""
        pass

    @abstractmethod
    def exists(self, key: str) -> bool:
        """Check if key exists."""
        pass

    @abstractmethod
    def clear(self) -> bool:
        """Clear all cache entries."""
        pass


class InMemoryCache(CacheBackend):
    """
    In-memory cache backend for testing and development.

    Thread-safe with TTL support.
    """

    def __init__(self, max_size: int = 1000) -> None:
        """
        Initialize in-memory cache.

        Args:
            max_size: Maximum number of entries (LRU eviction)
        """
        self._lock = threading.RLock()
        self._cache: dict[str, tuple[bytes, float | None]] = {}
        self._max_size = max_size

    def _is_expired(self, expiry: float | None) -> bool:
        """Check if entry is expired."""
        if expiry is None:
            return False
        return time.time() > expiry

    def _evict_expired(self) -> None:
        """Remove expired entries."""
        current_time = time.time()
        expired_keys = [
            key
            for key, (_, expiry) in self._cache.items()
            if expiry is not None and current_time > expiry
        ]
        for key in expired_keys:
            del self._cache[key]

    def _evict_lru(self) -> None:
        """Evict oldest entry if cache is full."""
        if len(self._cache) >= self._max_size:
            # Simple FIFO eviction
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]

    def get(self, key: str) -> bytes | None:
        """Get value from cache."""
        with self._lock:
            if key not in self._cache:
                return None

            value, expiry = self._cache[key]

            if self._is_expired(expiry):
                del self._cache[key]
                return None

            return value

    def set(self, key: str, value: bytes, ttl: int | None = None) -> bool:
        """Set value in cache."""
        with self._lock:
            self._evict_expired()
            self._evict_lru()

            expiry = time.time() + ttl if ttl else None
            self._cache[key] = (value, expiry)
            return True

    def delete(self, key: str) -> bool:
        """Delete value from cache."""
        with self._lock:
            # Support pattern matching with *
            if "*" in key:
                pattern = key.replace("*", "")
                keys_to_delete = [k for k in self._cache if k.startswith(pattern)]
                for k in keys_to_delete:
                    del self._cache[k]
                return len(keys_to_delete) > 0

            if key in self._cache:
                del self._cache[key]
                return True
            return False

    def exists(self, key: str) -> bool:
        """Check if key exists."""
        return self.get(key) is not None

    def clear(self) -> bool:
        """Clear all cache entries."""
        with self._lock:
            self._cache.clear()
            return True


class RedisBackend(CacheBackend):
    """
    Redis cache backend.

    Uses redis-py library if available, falls back to in-memory.
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: str | None = None,
    ) -> None:
        """
        Initialize Redis backend.

        Args:
            host: Redis server host
            port: Redis server port
            db: Redis database number
            password: Redis password
        """
        self._host = host
        self._port = port
        self._db = db
        self._password = password
        self._fallback = InMemoryCache()

        try:
            import redis

            self._client = redis.Redis(
                host=host, port=port, db=db, password=password, decode_responses=False
            )
            # Test connection
            self._client.ping()
            self._redis_available = True
        except (ImportError, Exception):
            self._redis_available = False

    def get(self, key: str) -> bytes | None:
        """Get value from cache."""
        if not self._redis_available:
            return self._fallback.get(key)

        try:
            return self._client.get(key)
        except Exception:
            return None

    def set(self, key: str, value: bytes, ttl: int | None = None) -> bool:
        """Set value in cache."""
        if not self._redis_available:
            return self._fallback.set(key, value, ttl)

        try:
            if ttl:
                return bool(self._client.setex(key, ttl, value))
            else:
                return bool(self._client.set(key, value))
        except Exception:
            return False

    def delete(self, key: str) -> bool:
        """Delete value from cache."""
        if not self._redis_available:
            return self._fallback.delete(key)

        try:
            # Support pattern matching
            if "*" in key:
                keys = self._client.keys(key)
                if keys:
                    return bool(self._client.delete(*keys))
                return False
            return bool(self._client.delete(key))
        except Exception:
            return False

    def exists(self, key: str) -> bool:
        """Check if key exists."""
        if not self._redis_available:
            return self._fallback.exists(key)

        try:
            return bool(self._client.exists(key))
        except Exception:
            return False

    def clear(self) -> bool:
        """Clear all cache entries."""
        if not self._redis_available:
            return self._fallback.clear()

        try:
            return bool(self._client.flushdb())
        except Exception:
            return False


class MemcachedBackend(CacheBackend):
    """
    Memcached cache backend.

    Uses pymemcache library if available, falls back to in-memory.
    """

    def __init__(self, host: str = "localhost", port: int = 11211) -> None:
        """
        Initialize Memcached backend.

        Args:
            host: Memcached server host
            port: Memcached server port
        """
        self._host = host
        self._port = port
        self._fallback = InMemoryCache()

        try:
            from pymemcache.client import base

            self._client = base.Client((host, port))
            self._memcached_available = True
        except ImportError:
            self._memcached_available = False

    def get(self, key: str) -> bytes | None:
        """Get value from cache."""
        if not self._memcached_available:
            return self._fallback.get(key)

        try:
            return self._client.get(key)
        except Exception:
            return None

    def set(self, key: str, value: bytes, ttl: int | None = None) -> bool:
        """Set value in cache."""
        if not self._memcached_available:
            return self._fallback.set(key, value, ttl)

        try:
            expire = ttl if ttl else 0
            return bool(self._client.set(key, value, expire=expire))
        except Exception:
            return False

    def delete(self, key: str) -> bool:
        """Delete value from cache."""
        if not self._memcached_available:
            return self._fallback.delete(key)

        try:
            # Memcached doesn't support pattern matching
            if "*" in key:
                # Fall back to in-memory for pattern matching
                return self._fallback.delete(key)
            return bool(self._client.delete(key))
        except Exception:
            return False

    def exists(self, key: str) -> bool:
        """Check if key exists."""
        return self.get(key) is not None

    def clear(self) -> bool:
        """Clear all cache entries."""
        if not self._memcached_available:
            return self._fallback.clear()

        try:
            return bool(self._client.flush_all())
        except Exception:
            return False
