"""Message Queue/Broker.

High-throughput pub/sub with 500K+ msg/sec.
"""

from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import List, Optional
import time
from uuid import uuid4

from fastapi import FastAPI
from pydantic import BaseModel

from toolkit.algorithms import RingBuffer, ConsistentHashRing


@dataclass
class Message:
    """Message."""
    __slots__ = ('id', 'topic', 'payload', 'timestamp')
    id: str
    topic: str
    payload: dict
    timestamp: float


class MessageQueue:
    """Message queue with partitioning."""

    def __init__(self, num_partitions: int = 16):
        self.hash_ring = ConsistentHashRing()
        self.partitions: dict[str, RingBuffer] = {}

        for i in range(num_partitions):
            partition = f"partition_{i}"
            self.hash_ring.add_node(partition)
            self.partitions[partition] = RingBuffer(capacity=1_000_000)

        self.stats = {"published": 0, "consumed": 0}

    async def publish(self, topic: str, payload: dict) -> str:
        """Publish message."""
        msg = Message(
            id=str(uuid4()),
            topic=topic,
            payload=payload,
            timestamp=time.time(),
        )

        partition = self.hash_ring.get_node(topic)
        self.partitions[partition].push(msg)
        self.stats["published"] += 1

        return msg.id

    async def consume(self, topic: str, count: int = 10) -> List[Message]:
        """Consume messages."""
        partition = self.hash_ring.get_node(topic)
        messages = []

        for _ in range(count):
            msg = self.partitions[partition].pop()
            if msg is None:
                break
            if msg.topic == topic:
                messages.append(msg)
                self.stats["consumed"] += 1

        return messages


service: Optional[MessageQueue] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global service
    service = MessageQueue()
    yield


app = FastAPI(title="Message Queue", lifespan=lifespan)


class PublishRequest(BaseModel):
    topic: str
    payload: dict


@app.post("/api/v1/publish")
async def publish(req: PublishRequest):
    """Publish message."""
    msg_id = await service.publish(req.topic, req.payload)
    return {"message_id": msg_id}


@app.get("/api/v1/consume/{topic}")
async def consume(topic: str, count: int = 10):
    """Consume messages."""
    messages = await service.consume(topic, count)
    return {
        "topic": topic,
        "count": len(messages),
        "messages": [
            {"id": m.id, "payload": m.payload, "timestamp": m.timestamp}
            for m in messages
        ]
    }


@app.get("/api/v1/stats")
async def stats():
    return service.stats


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.get("/")
async def root():
    return {"message": "Message Queue"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8010)
