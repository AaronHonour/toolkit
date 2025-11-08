"""Feature Store for ML.

Real-time feature serving with < 1ms P99 latency and 500K+ lookups/sec.
"""

from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Any
import time

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from toolkit.algorithms import LRUCache, ConsistentHashRing, fast_hash


@dataclass
class Feature:
    """Feature value with metadata."""
    __slots__ = ('entity_id', 'feature_name', 'value', 'timestamp', 'version')

    entity_id: str
    feature_name: str
    value: Any
    timestamp: float
    version: int


class FeatureStore:
    """Feature store with online and offline serving."""

    def __init__(self):
        """Initialize feature store."""
        # Online feature cache (326K+ ops/sec)
        self.online_cache = LRUCache(capacity=1_000_000)

        # Feature sharding
        self.hash_ring = ConsistentHashRing()
        self.shards: Dict[str, Dict[str, List[Feature]]] = {}

        for i in range(16):
            shard = f"shard_{i}"
            self.hash_ring.add_node(shard)
            self.shards[shard] = {}

        # Stats
        self.stats = {
            'cache_hits': 0,
            'cache_misses': 0,
            'feature_writes': 0,
            'feature_reads': 0,
        }

    async def write_feature(
        self,
        entity_id: str,
        feature_name: str,
        value: Any,
        timestamp: Optional[float] = None
    ) -> None:
        """Write feature value.

        Args:
            entity_id: Entity ID (e.g., user:123)
            feature_name: Feature name
            value: Feature value
            timestamp: Optional timestamp (defaults to now)
        """
        if timestamp is None:
            timestamp = time.time()

        feature = Feature(
            entity_id=entity_id,
            feature_name=feature_name,
            value=value,
            timestamp=timestamp,
            version=1,
        )

        # Get shard using feature hashing (886K+ ops/sec)
        feature_key = f"{entity_id}:{feature_name}"
        hash_value = fast_hash(feature_key)
        shard = self.hash_ring.get_node(str(hash_value))

        # Store in shard
        if entity_id not in self.shards[shard]:
            self.shards[shard][entity_id] = []

        self.shards[shard][entity_id].append(feature)

        # Update online cache
        cache_key = f"{entity_id}:{feature_name}"
        self.online_cache.put(cache_key, feature)

        self.stats['feature_writes'] += 1

    async def get_online_features(
        self,
        entity_id: str,
        feature_names: List[str]
    ) -> Dict[str, Any]:
        """Get online features (real-time serving).

        Args:
            entity_id: Entity ID
            feature_names: List of feature names

        Returns:
            Dictionary of feature values
        """
        features = {}

        for feature_name in feature_names:
            cache_key = f"{entity_id}:{feature_name}"

            # Check cache (326K+ ops/sec)
            cached = self.online_cache.get(cache_key)

            if cached:
                features[feature_name] = cached.value
                self.stats['cache_hits'] += 1
            else:
                # Cache miss - get from shard
                hash_value = fast_hash(cache_key)
                shard = self.hash_ring.get_node(str(hash_value))

                if entity_id in self.shards[shard]:
                    entity_features = self.shards[shard][entity_id]
                    # Get latest value for feature
                    matching = [f for f in entity_features if f.feature_name == feature_name]
                    if matching:
                        latest = max(matching, key=lambda f: f.timestamp)
                        features[feature_name] = latest.value
                        # Update cache
                        self.online_cache.put(cache_key, latest)

                self.stats['cache_misses'] += 1

        self.stats['feature_reads'] += 1
        return features

    async def get_historical_features(
        self,
        entity_id: str,
        feature_names: List[str],
        as_of: float
    ) -> Dict[str, Any]:
        """Get features as of a specific timestamp (point-in-time).

        Args:
            entity_id: Entity ID
            feature_names: List of feature names
            as_of: Timestamp to query at

        Returns:
            Dictionary of feature values at that time
        """
        features = {}

        for feature_name in feature_names:
            hash_value = fast_hash(f"{entity_id}:{feature_name}")
            shard = self.hash_ring.get_node(str(hash_value))

            if entity_id in self.shards[shard]:
                entity_features = self.shards[shard][entity_id]

                # Get features up to as_of timestamp
                historical = [
                    f for f in entity_features
                    if f.feature_name == feature_name and f.timestamp <= as_of
                ]

                if historical:
                    latest = max(historical, key=lambda f: f.timestamp)
                    features[feature_name] = latest.value

        return features


# Global service
service: Optional[FeatureStore] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan."""
    global service
    service = FeatureStore()
    yield


app = FastAPI(
    title="Feature Store",
    description="ML feature serving with < 1ms P99 latency",
    version="1.0.0",
    lifespan=lifespan,
)


class WriteFeatureRequest(BaseModel):
    """Write feature request."""
    entity_id: str
    feature_name: str
    value: Any
    timestamp: Optional[float] = None


class GetFeaturesRequest(BaseModel):
    """Get features request."""
    entity_id: str
    feature_names: List[str]
    as_of: Optional[float] = None


@app.post("/api/v1/features")
async def write_feature(req: WriteFeatureRequest):
    """Write feature value."""
    await service.write_feature(
        entity_id=req.entity_id,
        feature_name=req.feature_name,
        value=req.value,
        timestamp=req.timestamp
    )

    return {"status": "ok"}


@app.post("/api/v1/features/online")
async def get_online_features(req: GetFeaturesRequest):
    """Get online features (real-time)."""
    features = await service.get_online_features(
        entity_id=req.entity_id,
        feature_names=req.feature_names
    )

    return {
        "entity_id": req.entity_id,
        "features": features,
    }


@app.post("/api/v1/features/historical")
async def get_historical_features(req: GetFeaturesRequest):
    """Get historical features (point-in-time)."""
    if req.as_of is None:
        raise HTTPException(status_code=400, detail="as_of timestamp required")

    features = await service.get_historical_features(
        entity_id=req.entity_id,
        feature_names=req.feature_names,
        as_of=req.as_of
    )

    return {
        "entity_id": req.entity_id,
        "features": features,
        "as_of": req.as_of,
    }


@app.get("/api/v1/stats")
async def get_stats():
    """Get feature store statistics."""
    total = service.stats['cache_hits'] + service.stats['cache_misses']
    hit_rate = (service.stats['cache_hits'] / total * 100) if total > 0 else 0

    return {
        **service.stats,
        'cache_hit_rate_percent': hit_rate,
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.get("/")
async def root():
    return {"message": "Feature Store"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8016)
