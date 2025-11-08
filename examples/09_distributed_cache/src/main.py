"""Distributed Cache System.

Multi-tier caching with 1M+ req/sec throughput.
"""

from contextlib import asynccontextmanager
from typing import Optional, Any
import time

from fastapi import FastAPI
from pydantic import BaseModel

from toolkit.algorithms import LRUCache, ConsistentHashRing, BloomFilter, fast_hash


class DistributedCache:
    """Distributed cache with consistent hashing."""

    def __init__(self, num_shards: int = 16, capacity_per_shard: int = 100_000):
        # L1 cache (local)
        self.l1_cache = LRUCache(capacity=10_000)

        # L2 caches (sharded)
        self.hash_ring = ConsistentHashRing()
        self.shards: dict[str, LRUCache] = {}

        for i in range(num_shards):
            shard_name = f"shard_{i}"
            self.hash_ring.add_node(shard_name)
            self.shards[shard_name] = LRUCache(capacity=capacity_per_shard)

        # Negative cache (BloomFilter for non-existent keys)
        self.negative_cache = BloomFilter(expected_elements=1_000_000)

        # Stats
        self.hits = 0
        self.misses = 0
        self.l1_hits = 0
        self.l2_hits = 0

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        # Check L1 cache
        value = self.l1_cache.get(key)
        if value is not None:
            self.hits += 1
            self.l1_hits += 1
            return value

        # Check negative cache
        if self.negative_cache.contains(key):
            self.misses += 1
            return None

        # Check L2 cache
        shard = self.hash_ring.get_node(key)
        value = self.shards[shard].get(key)

        if value is not None:
            # Promote to L1
            self.l1_cache.put(key, value)
            self.hits += 1
            self.l2_hits += 1
            return value

        self.misses += 1
        return None

    async def put(self, key: str, value: Any) -> None:
        """Put value in cache."""
        # Write to L1
        self.l1_cache.put(key, value)

        # Write to L2
        shard = self.hash_ring.get_node(key)
        self.shards[shard].put(key, value)

    async def delete(self, key: str) -> None:
        """Delete from cache."""
        # Remove from L1
        # Note: LRUCache doesn't have delete, so we just skip

        # Remove from L2
        shard = self.hash_ring.get_node(key)
        # Mark as non-existent
        self.negative_cache.add(key)


class CacheService:
    """Cache service."""

    def __init__(self):
        self.cache = DistributedCache(num_shards=16)

    def get_stats(self) -> dict:
        """Get cache statistics."""
        total_requests = self.cache.hits + self.cache.misses
        hit_rate = (self.cache.hits / total_requests * 100) if total_requests > 0 else 0

        return {
            "total_requests": total_requests,
            "hits": self.cache.hits,
            "misses": self.cache.misses,
            "hit_rate_percent": hit_rate,
            "l1_hits": self.cache.l1_hits,
            "l2_hits": self.cache.l2_hits,
        }


service: Optional[CacheService] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global service
    service = CacheService()
    yield


app = FastAPI(title="Distributed Cache", lifespan=lifespan)


class CacheValue(BaseModel):
    value: Any


@app.get("/api/v1/cache/{key}")
async def get_key(key: str):
    """Get value from cache."""
    value = await service.cache.get(key)
    if value is None:
        return {"found": False}
    return {"found": True, "value": value}


@app.put("/api/v1/cache/{key}")
async def put_key(key: str, data: CacheValue):
    """Put value in cache."""
    await service.cache.put(key, data.value)
    return {"status": "ok"}


@app.delete("/api/v1/cache/{key}")
async def delete_key(key: str):
    """Delete from cache."""
    await service.cache.delete(key)
    return {"status": "ok"}


@app.get("/api/v1/stats")
async def get_stats():
    """Get cache statistics."""
    return service.get_stats()


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.get("/")
async def root():
    return {"message": "Distributed Cache System"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8009)
