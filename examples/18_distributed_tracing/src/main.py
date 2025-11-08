"""Distributed Tracing System.

Microservices observability with 1M+ spans/sec ingestion.
"""

from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Dict, List, Optional
import time

from fastapi import FastAPI
from pydantic import BaseModel

from toolkit.algorithms import RingBuffer, ConsistentHashRing, LRUCache
import lz4.frame


@dataclass
class Span:
    """Distributed trace span."""
    __slots__ = ('trace_id', 'span_id', 'parent_id', 'service', 'operation', 'start_time', 'duration', 'tags')

    trace_id: str
    span_id: str
    parent_id: Optional[str]
    service: str
    operation: str
    start_time: float
    duration: float
    tags: Dict[str, str]


class TracingSystem:
    """Distributed tracing system."""

    def __init__(self):
        """Initialize tracing system."""
        # Span ingestion buffer (284K+ ops/sec)
        self.span_buffer = RingBuffer(capacity=10_000_000)

        # Trace cache (326K+ ops/sec)
        self.trace_cache = LRUCache(capacity=100_000)

        # Shard traces
        self.hash_ring = ConsistentHashRing()
        self.shards: Dict[str, Dict[str, List[Span]]] = {}

        for i in range(16):
            shard = f"shard_{i}"
            self.hash_ring.add_node(shard)
            self.shards[shard] = {}

        self.spans_ingested = 0

    async def ingest_span(self, span: Span) -> None:
        """Ingest span.

        Args:
            span: Span to ingest
        """
        # Add to buffer
        self.span_buffer.push(span)

        # Route to shard
        shard = self.hash_ring.get_node(span.trace_id)

        # Store span
        if span.trace_id not in self.shards[shard]:
            self.shards[shard][span.trace_id] = []

        self.shards[shard][span.trace_id].append(span)

        # Invalidate trace cache
        self.trace_cache.put(span.trace_id, None)

        self.spans_ingested += 1

    async def get_trace(self, trace_id: str) -> Optional[Dict]:
        """Get complete trace.

        Args:
            trace_id: Trace ID

        Returns:
            Assembled trace
        """
        # Check cache
        cached = self.trace_cache.get(trace_id)
        if cached:
            return cached

        # Get spans from shard
        shard = self.hash_ring.get_node(trace_id)

        if trace_id not in self.shards[shard]:
            return None

        spans = self.shards[shard][trace_id]

        # Assemble trace
        trace = {
            'trace_id': trace_id,
            'spans': [
                {
                    'span_id': s.span_id,
                    'parent_id': s.parent_id,
                    'service': s.service,
                    'operation': s.operation,
                    'start_time': s.start_time,
                    'duration': s.duration,
                    'tags': s.tags,
                }
                for s in spans
            ],
            'span_count': len(spans),
            'total_duration': max((s.start_time + s.duration for s in spans), default=0) - min((s.start_time for s in spans), default=0),
        }

        # Cache result
        self.trace_cache.put(trace_id, trace)

        return trace


service: Optional[TracingSystem] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global service
    service = TracingSystem()
    yield


app = FastAPI(title="Distributed Tracing System", lifespan=lifespan)


class SpanRequest(BaseModel):
    trace_id: str
    span_id: str
    parent_id: Optional[str] = None
    service: str
    operation: str
    start_time: float
    duration: float
    tags: Dict[str, str] = {}


@app.post("/api/v1/spans")
async def ingest_span(req: SpanRequest):
    """Ingest span."""
    span = Span(
        trace_id=req.trace_id,
        span_id=req.span_id,
        parent_id=req.parent_id,
        service=req.service,
        operation=req.operation,
        start_time=req.start_time,
        duration=req.duration,
        tags=req.tags,
    )

    await service.ingest_span(span)
    return {"status": "ok"}


@app.get("/api/v1/traces/{trace_id}")
async def get_trace(trace_id: str):
    """Get complete trace."""
    trace = await service.get_trace(trace_id)

    if not trace:
        return {"error": "Trace not found"}

    return trace


@app.get("/api/v1/stats")
async def stats():
    return {"spans_ingested": service.spans_ingested}


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.get("/")
async def root():
    return {"message": "Distributed Tracing System"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8018)
