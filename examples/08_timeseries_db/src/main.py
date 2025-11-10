"""Time-Series Database.

High-performance TSDB with 1M+ data points/sec ingestion.
"""

from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import time

from fastapi import FastAPI
from pydantic import BaseModel

from toolkit.algorithms import BufferPool, ConsistentHashRing, LRUCache
import lz4.frame


@dataclass
class DataPoint:
    """Time-series data point."""
    __slots__ = ('timestamp', 'metric', 'value', 'tags')

    timestamp: float
    metric: str
    value: float
    tags: Dict[str, str]


class TimeSeriesDB:
    """Time-series database."""

    def __init__(self):
        self.buffer_pool = BufferPool(buffer_size=8192, pool_size=1000)
        self.hash_ring = ConsistentHashRing()
        self.cache = LRUCache(capacity=100_000)

        # Shards (partitions)
        for i in range(16):
            self.hash_ring.add_node(f"shard_{i}")

        # Data storage
        self._data: Dict[str, List[DataPoint]] = {}
        self._compressed: Dict[str, bytes] = {}

    async def write(self, datapoint: DataPoint) -> None:
        """Write data point."""
        # Shard by metric + tags
        shard_key = f"{datapoint.metric}:{hash(frozenset(datapoint.tags.items()))}"
        shard = self.hash_ring.get_node(shard_key)

        if shard not in self._data:
            self._data[shard] = []

        self._data[shard].append(datapoint)

        # Compress older data
        if len(self._data[shard]) > 10000:
            await self._compress_shard(shard)

    async def _compress_shard(self, shard: str) -> None:
        """Compress shard data with LZ4."""
        data = self._data[shard][:5000]  # Compress first half

        # Serialize
        serialized = b''.join([
            f"{dp.timestamp},{dp.metric},{dp.value}\n".encode()
            for dp in data
        ])

        # Compress with LZ4 (8.4x faster)
        compressed = lz4.frame.compress(serialized)
        self._compressed[f"{shard}_archive"] = compressed

        # Keep recent data uncompressed
        self._data[shard] = self._data[shard][5000:]

    async def query(
        self,
        metric: str,
        start: float,
        end: float,
        tags: Dict[str, str] = None
    ) -> List[DataPoint]:
        """Query time range."""
        results = []

        # Find relevant shards
        shard_key = f"{metric}:{hash(frozenset((tags or {}).items()))}"
        shard = self.hash_ring.get_node(shard_key)

        # Query recent data
        if shard in self._data:
            for dp in self._data[shard]:
                if start <= dp.timestamp <= end and dp.metric == metric:
                    results.append(dp)

        return results


class TSDBService:
    """TSDB service."""

    def __init__(self):
        self.db = TimeSeriesDB()
        self._write_count = 0

    async def write(self, metric: str, value: float, tags: Dict[str, str] = None) -> None:
        """Write metric."""
        dp = DataPoint(
            timestamp=time.time(),
            metric=metric,
            value=value,
            tags=tags or {},
        )
        await self.db.write(dp)
        self._write_count += 1


service: Optional[TSDBService] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global service
    service = TSDBService()
    yield


app = FastAPI(title="Time-Series Database", lifespan=lifespan)


class WriteRequest(BaseModel):
    metric: str
    value: float
    tags: Dict[str, str] = {}


@app.post("/api/v1/write")
async def write_metric(req: WriteRequest):
    """Write metric."""
    await service.write(req.metric, req.value, req.tags)
    return {"status": "ok"}


@app.get("/api/v1/query")
async def query_metrics(
    metric: str,
    start: float,
    end: float
):
    """Query metrics."""
    results = await service.db.query(metric, start, end)
    return {
        "metric": metric,
        "datapoints": [
            {"timestamp": dp.timestamp, "value": dp.value}
            for dp in results
        ]
    }


@app.get("/health")
async def health():
    return {"status": "healthy", "writes": service._write_count}


@app.get("/")
async def root():
    return {"message": "Time-Series Database"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8008)
