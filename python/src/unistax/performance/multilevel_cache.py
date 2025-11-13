"""Multi-level caching for optimal performance."""

import threading
import time
from collections import OrderedDict
from dataclasses import dataclass
from enum import Enum
from typing import Any


class CacheLevel(Enum):
    """Cache level enumeration."""

    L1_MEMORY = "l1_memory"  # In-process memory
    L2_REDIS = "l2_redis"  # Distributed Redis
    L3_DATABASE = "l3_database"  # Database query cache


@dataclass
class CacheEntry:
    """Cache entry with metadata."""

    value: Any
    timestamp: float
    ttl: int
    hits: int = 0


class LRUCache:
    """Thread-safe LRU cache implementation."""

    def __init__(self, max_size: int = 1000):
        """Initialize LRU cache.

        Args:
            max_size: Maximum cache size
        """
        self.max_size = max_size
        self.cache: OrderedDict = OrderedDict()
        self.lock = threading.RLock()

    def get(self, key: str) -> Any | None:
        """Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None
        """
        with self.lock:
            if key not in self.cache:
                return None

            # Move to end (most recently used)
            self.cache.move_to_end(key)
            entry = self.cache[key]

            # Check TTL
            if time.time() - entry.timestamp > entry.ttl:
                del self.cache[key]
                return None

            entry.hits += 1
            return entry.value

    def set(self, key: str, value: Any, ttl: int = 300):
        """Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
        """
        with self.lock:
            if key in self.cache:
                del self.cache[key]
            elif len(self.cache) >= self.max_size:
                # Remove least recently used
                self.cache.popitem(last=False)

            self.cache[key] = CacheEntry(value=value, timestamp=time.time(), ttl=ttl)

    def delete(self, key: str):
        """Delete key from cache.

        Args:
            key: Cache key
        """
        with self.lock:
            if key in self.cache:
                del self.cache[key]

    def clear(self):
        """Clear all cache entries."""
        with self.lock:
            self.cache.clear()

    def size(self) -> int:
        """Get cache size.

        Returns:
            Number of entries
        """
        with self.lock:
            return len(self.cache)

    def stats(self) -> dict:
        """Get cache statistics.

        Returns:
            Statistics dictionary
        """
        with self.lock:
            total_hits = sum(entry.hits for entry in self.cache.values())
            return {
                "size": len(self.cache),
                "max_size": self.max_size,
                "total_hits": total_hits,
                "fill_rate": len(self.cache) / self.max_size,
            }


class MultiLevelCache:
    """Multi-level cache with L1 (memory) and L2 (Redis) support."""

    def __init__(
        self, l1_max_size: int = 1000, l2_client: Any | None = None, enable_stats: bool = True
    ):
        """Initialize multi-level cache.

        Args:
            l1_max_size: L1 cache max size
            l2_client: Redis client for L2 cache
            enable_stats: Enable statistics tracking
        """
        self.l1 = LRUCache(max_size=l1_max_size)
        self.l2_client = l2_client
        self.enable_stats = enable_stats

        if enable_stats:
            self.stats = {
                "l1_hits": 0,
                "l1_misses": 0,
                "l2_hits": 0,
                "l2_misses": 0,
                "sets": 0,
            }
            self.stats_lock = threading.Lock()

    def get(self, key: str) -> Any | None:
        """Get value from cache (L1 then L2).

        Args:
            key: Cache key

        Returns:
            Cached value or None
        """
        # Try L1 first
        value = self.l1.get(key)
        if value is not None:
            if self.enable_stats:
                with self.stats_lock:
                    self.stats["l1_hits"] += 1
            return value

        if self.enable_stats:
            with self.stats_lock:
                self.stats["l1_misses"] += 1

        # Try L2 (Redis)
        if self.l2_client:
            try:
                value = self.l2_client.get(key)
                if value is not None:
                    # Promote to L1
                    self.l1.set(key, value)
                    if self.enable_stats:
                        with self.stats_lock:
                            self.stats["l2_hits"] += 1
                    return value
            except Exception:
                pass  # L2 unavailable

        if self.enable_stats:
            with self.stats_lock:
                self.stats["l2_misses"] += 1

        return None

    def set(self, key: str, value: Any, ttl: int = 300):
        """Set value in both cache levels.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
        """
        # Set in L1
        self.l1.set(key, value, ttl)

        # Set in L2 (Redis)
        if self.l2_client:
            try:
                self.l2_client.setex(key, ttl, value)
            except Exception:
                pass  # L2 unavailable

        if self.enable_stats:
            with self.stats_lock:
                self.stats["sets"] += 1

    def delete(self, key: str):
        """Delete from all cache levels.

        Args:
            key: Cache key
        """
        self.l1.delete(key)

        if self.l2_client:
            try:
                self.l2_client.delete(key)
            except Exception:
                pass

    def clear(self):
        """Clear all cache levels."""
        self.l1.clear()

        if self.l2_client:
            try:
                self.l2_client.flushdb()
            except Exception:
                pass

    def get_stats(self) -> dict:
        """Get cache statistics.

        Returns:
            Statistics dictionary
        """
        if not self.enable_stats:
            return {}

        with self.stats_lock:
            stats = self.stats.copy()

        l1_stats = self.l1.stats()

        total_requests = stats["l1_hits"] + stats["l1_misses"]
        l1_hit_rate = stats["l1_hits"] / total_requests if total_requests > 0 else 0
        l2_hit_rate = stats["l2_hits"] / stats["l1_misses"] if stats["l1_misses"] > 0 else 0

        return {
            "l1": {
                "hits": stats["l1_hits"],
                "misses": stats["l1_misses"],
                "hit_rate": l1_hit_rate,
                **l1_stats,
            },
            "l2": {
                "hits": stats["l2_hits"],
                "misses": stats["l2_misses"],
                "hit_rate": l2_hit_rate,
            },
            "total": {
                "requests": total_requests,
                "sets": stats["sets"],
            },
        }

    def warm_cache(self, key_value_pairs: list[tuple[str, Any]], ttl: int = 300):
        """Warm cache with initial data.

        Args:
            key_value_pairs: List of (key, value) tuples
            ttl: Time to live in seconds
        """
        for key, value in key_value_pairs:
            self.set(key, value, ttl)
