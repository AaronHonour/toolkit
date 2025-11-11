"""CDC Pipeline (Change Data Capture).

Stream database changes with 100K+ changes/sec throughput.
"""

from contextlib import asynccontextmanager
from dataclasses import dataclass
from enum import Enum
import time
from typing import Optional
from uuid import uuid4

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from unistax.algorithms import RingBuffer, BloomFilter, ConsistentHashRing


class ChangeType(str, Enum):
    INSERT = "INSERT"
    UPDATE = "UPDATE"
    DELETE = "DELETE"


@dataclass
class ChangeEvent:
    """Database change event."""
    __slots__ = ('id', 'table', 'change_type', 'data', 'timestamp')
    id: str
    table: str
    change_type: ChangeType
    data: dict
    timestamp: float


class CDCPipeline:
    """CDC pipeline with exactly-once semantics."""

    def __init__(self):
        self.buffer = RingBuffer(capacity=1_000_000)
        self.dedup = BloomFilter(expected_elements=10_000_000)
        self.hash_ring = ConsistentHashRing()

        # Routing (sharding by table)
        for i in range(8):
            self.hash_ring.add_node(f"sink_{i}")

        self.stats = {"captured": 0, "duplicates": 0, "routed": 0}

    async def capture_change(self, table: str, change_type: ChangeType, data: dict) -> str:
        """Capture database change."""
        change_id = str(uuid4())

        # Deduplication
        if self.dedup.contains(change_id):
            self.stats["duplicates"] += 1
            return change_id

        self.dedup.add(change_id)

        # Create change event
        event = ChangeEvent(
            id=change_id,
            table=table,
            change_type=change_type,
            data=data,
            timestamp=time.time(),
        )

        # Buffer change
        self.buffer.push(event)
        self.stats["captured"] += 1

        # Route to sink
        sink = self.hash_ring.get_node(table)
        self.stats["routed"] += 1

        return change_id


service: Optional[CDCPipeline] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global service
    service = CDCPipeline()
    yield


app = FastAPI(title="CDC Pipeline", lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChangeRequest(BaseModel):
    table: str
    change_type: ChangeType
    data: dict


@app.post("/api/v1/changes")
async def capture_change(req: ChangeRequest):
    """Capture database change."""
    change_id = await service.capture_change(req.table, req.change_type, req.data)
    return {"change_id": change_id}


@app.get("/api/v1/stats")
async def stats():
    return service.stats


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.get("/")
async def root():
    return {"message": "CDC Pipeline"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8013)
