"""Lambda Architecture.

Batch + Speed + Serving layers for comprehensive data processing.
"""

from contextlib import asynccontextmanager
from collections import defaultdict
import time
from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel

from toolkit.algorithms import RingBuffer, LRUCache


class BatchLayer:
    """Batch processing layer."""

    def __init__(self):
        self.data = defaultdict(int)

    async def process_batch(self, records: list[dict]) -> None:
        """Process batch of records."""
        for record in records:
            key = record.get("key", "default")
            value = record.get("value", 0)
            self.data[key] += value


class SpeedLayer:
    """Real-time speed layer."""

    def __init__(self):
        self.buffer = RingBuffer(capacity=1_000_000)
        self.real_time_data = defaultdict(int)

    async def process_event(self, event: dict) -> None:
        """Process real-time event."""
        self.buffer.push(event)
        key = event.get("key", "default")
        value = event.get("value", 0)
        self.real_time_data[key] += value


class ServingLayer:
    """Serving layer merges batch + speed views."""

    def __init__(self, batch_layer: BatchLayer, speed_layer: SpeedLayer):
        self.batch = batch_layer
        self.speed = speed_layer
        self.cache = LRUCache(capacity=100_000)

    async def query(self, key: str) -> dict:
        """Query merged view."""
        # Check cache
        cached = self.cache.get(key)
        if cached:
            return cached

        # Merge batch + speed
        batch_value = self.batch.data.get(key, 0)
        speed_value = self.speed.real_time_data.get(key, 0)
        result = {
            "key": key,
            "batch_value": batch_value,
            "speed_value": speed_value,
            "total": batch_value + speed_value,
        }

        # Cache result
        self.cache.put(key, result)
        return result


class LambdaService:
    """Lambda architecture service."""

    def __init__(self):
        self.batch = BatchLayer()
        self.speed = SpeedLayer()
        self.serving = ServingLayer(self.batch, self.speed)


service: Optional[LambdaService] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global service
    service = LambdaService()
    yield


app = FastAPI(title="Lambda Architecture", lifespan=lifespan)


class Event(BaseModel):
    key: str
    value: float


@app.post("/api/v1/events")
async def ingest_event(event: Event):
    """Ingest real-time event (speed layer)."""
    await service.speed.process_event(event.dict())
    return {"status": "ok"}


@app.post("/api/v1/batch")
async def process_batch(records: list[Event]):
    """Process batch (batch layer)."""
    await service.batch.process_batch([r.dict() for r in records])
    return {"status": "ok", "count": len(records)}


@app.get("/api/v1/query/{key}")
async def query(key: str):
    """Query merged view (serving layer)."""
    return await service.serving.query(key)


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.get("/")
async def root():
    return {"message": "Lambda Architecture"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8012)
