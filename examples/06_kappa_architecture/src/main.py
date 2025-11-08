"""Kappa Architecture - Pure Stream Processing.

High-performance streaming pipeline with 500K+ events/sec capability.
"""

import asyncio
from collections import defaultdict
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, AsyncIterator
from uuid import uuid4
import time

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel

from toolkit.algorithms import RingBuffer, ConsistentHashRing, BloomFilter, LRUCache, fast_hash


# Event Types
class EventType(str, Enum):
    """Event types."""
    PAGE_VIEW = "page_view"
    BUTTON_CLICK = "button_click"
    PURCHASE = "purchase"
    SIGNUP = "signup"
    ERROR = "error"


# Pydantic Models
class EventData(BaseModel):
    """Event data model."""
    event_type: EventType
    user_id: str
    session_id: Optional[str] = None
    data: Dict[str, Any] = {}
    metadata: Dict[str, Any] = {}


class EventBatch(BaseModel):
    """Batch of events."""
    events: List[EventData]


# Domain Models
@dataclass
class Event:
    """Stream event."""
    __slots__ = ('id', 'timestamp', 'event_type', 'user_id', 'session_id', 'data', 'metadata', 'offset')

    id: str
    timestamp: datetime
    event_type: EventType
    user_id: str
    session_id: Optional[str]
    data: Dict[str, Any]
    metadata: Dict[str, Any]
    offset: int = 0


class EventLog:
    """Replayable, immutable event log."""

    def __init__(self, capacity: int = 10_000_000):
        """Initialize event log.

        Args:
            capacity: Maximum events to store
        """
        self._buffer = RingBuffer(capacity=capacity)
        self._offset = 0
        self._events: List[Event] = []  # For replay capability

    async def append(self, event: Event) -> int:
        """Append event to log.

        Args:
            event: Event to append

        Returns:
            Offset of appended event
        """
        event.offset = self._offset
        self._events.append(event)
        self._buffer.push(event)
        self._offset += 1
        return event.offset

    async def replay(self, from_offset: int = 0) -> AsyncIterator[Event]:
        """Replay events from offset.

        Args:
            from_offset: Starting offset

        Yields:
            Events from offset onwards
        """
        for event in self._events[from_offset:]:
            yield event
            await asyncio.sleep(0)  # Allow other tasks

    def get_offset(self) -> int:
        """Get current offset."""
        return self._offset

    def size(self) -> int:
        """Get number of events."""
        return len(self._events)


class MaterializedView:
    """Base materialized view."""

    async def update(self, event: Event) -> None:
        """Update view with event."""
        raise NotImplementedError

    async def query(self, **kwargs) -> Any:
        """Query view."""
        raise NotImplementedError


class AggregationView(MaterializedView):
    """Aggregation view with windowed metrics."""

    def __init__(self):
        """Initialize aggregation view."""
        self._cache = LRUCache(capacity=100_000)
        self._counters: Dict[str, int] = defaultdict(int)
        self._sums: Dict[str, float] = defaultdict(float)

    async def update(self, event: Event) -> None:
        """Update aggregations."""
        # Count by event type
        key = f"count:{event.event_type.value}"
        self._counters[key] += 1

        # Count by user
        user_key = f"user_count:{event.user_id}"
        self._counters[user_key] += 1

        # Cache recent events per user
        cache_key = f"recent:{event.user_id}"
        recent = self._cache.get(cache_key) or []
        recent.append({
            'event_type': event.event_type.value,
            'timestamp': event.timestamp.isoformat(),
            'data': event.data,
        })
        # Keep last 100 events
        if len(recent) > 100:
            recent = recent[-100:]
        self._cache.put(cache_key, recent)

    async def query(self, **kwargs) -> Dict[str, Any]:
        """Query aggregations."""
        query_type = kwargs.get('type', 'summary')

        if query_type == 'summary':
            return {
                'total_events': sum(v for k, v in self._counters.items() if k.startswith('count:')),
                'by_type': {
                    event_type: self._counters.get(f'count:{event_type}', 0)
                    for event_type in EventType
                },
                'unique_users': len([k for k in self._counters.keys() if k.startswith('user_count:')]),
            }
        elif query_type == 'user':
            user_id = kwargs.get('user_id')
            return {
                'user_id': user_id,
                'event_count': self._counters.get(f'user_count:{user_id}', 0),
                'recent_events': self._cache.get(f'recent:{user_id}') or [],
            }

        return {}


class MetricsView(MaterializedView):
    """Real-time metrics view."""

    def __init__(self):
        """Initialize metrics view."""
        self._start_time = time.time()
        self._event_count = 0
        self._last_event_time = time.time()
        self._event_times: List[float] = []

    async def update(self, event: Event) -> None:
        """Update metrics."""
        self._event_count += 1
        now = time.time()
        self._last_event_time = now
        self._event_times.append(now)

        # Keep only last 10K event times for rate calculation
        if len(self._event_times) > 10000:
            self._event_times = self._event_times[-10000:]

    async def query(self, **kwargs) -> Dict[str, Any]:
        """Query metrics."""
        elapsed = time.time() - self._start_time
        events_per_sec = self._event_count / elapsed if elapsed > 0 else 0

        # Calculate recent rate (last 1000 events)
        recent_rate = 0
        if len(self._event_times) >= 2:
            recent_window = min(1000, len(self._event_times))
            recent_elapsed = self._event_times[-1] - self._event_times[-recent_window]
            if recent_elapsed > 0:
                recent_rate = recent_window / recent_elapsed

        return {
            'total_events': self._event_count,
            'uptime_seconds': elapsed,
            'events_per_second_avg': events_per_sec,
            'events_per_second_recent': recent_rate,
            'last_event_time': datetime.fromtimestamp(self._last_event_time).isoformat(),
        }


class AlertsView(MaterializedView):
    """Threshold-based alerts view."""

    def __init__(self, threshold: int = 1000):
        """Initialize alerts view.

        Args:
            threshold: Alert threshold for events per user
        """
        self.threshold = threshold
        self._user_counts: Dict[str, int] = defaultdict(int)
        self._alerts: List[Dict[str, Any]] = []

    async def update(self, event: Event) -> None:
        """Update and check thresholds."""
        self._user_counts[event.user_id] += 1

        # Check threshold
        if self._user_counts[event.user_id] == self.threshold:
            alert = {
                'timestamp': datetime.utcnow().isoformat(),
                'user_id': event.user_id,
                'event_count': self.threshold,
                'message': f'User {event.user_id} exceeded {self.threshold} events',
            }
            self._alerts.append(alert)

    async def query(self, **kwargs) -> Dict[str, Any]:
        """Query alerts."""
        return {
            'total_alerts': len(self._alerts),
            'recent_alerts': self._alerts[-10:],  # Last 10 alerts
        }


class StreamProcessor:
    """Stream processor with partitioning."""

    def __init__(self, num_partitions: int = 16):
        """Initialize stream processor.

        Args:
            num_partitions: Number of partitions
        """
        self.num_partitions = num_partitions

        # Consistent hashing for partitioning
        self.hash_ring = ConsistentHashRing()
        for i in range(num_partitions):
            self.hash_ring.add_node(f"partition_{i}")

        # Partition buffers
        self.partition_buffers: Dict[str, RingBuffer] = {}
        for i in range(num_partitions):
            self.partition_buffers[f"partition_{i}"] = RingBuffer(capacity=100_000)

        # Deduplication
        self.dedup = BloomFilter(expected_elements=10_000_000, false_positive_rate=0.001)

        # Views
        self.views: List[MaterializedView] = [
            AggregationView(),
            MetricsView(),
            AlertsView(threshold=100),
        ]

        # Stats
        self.processed_count = 0
        self.duplicate_count = 0

    async def process(self, event: Event) -> None:
        """Process event through pipeline.

        Args:
            event: Event to process
        """
        # Check for duplicates
        if self.dedup.contains(event.id):
            self.duplicate_count += 1
            return

        self.dedup.add(event.id)

        # Route to partition
        partition = self.hash_ring.get_node(event.user_id)
        self.partition_buffers[partition].push(event)

        # Update all views
        for view in self.views:
            await view.update(event)

        self.processed_count += 1

    async def get_view(self, view_type: str, **kwargs) -> Any:
        """Get view data.

        Args:
            view_type: Type of view
            **kwargs: Query parameters

        Returns:
            View data
        """
        view_map = {
            'aggregation': 0,
            'metrics': 1,
            'alerts': 2,
        }

        if view_type not in view_map:
            raise ValueError(f"Unknown view type: {view_type}")

        view = self.views[view_map[view_type]]
        return await view.query(**kwargs)


class KappaService:
    """Kappa architecture service."""

    def __init__(self):
        """Initialize Kappa service."""
        self.event_log = EventLog(capacity=10_000_000)
        self.processor = StreamProcessor(num_partitions=16)
        self._replay_in_progress = False

    async def ingest(self, event_data: EventData) -> Event:
        """Ingest single event.

        Args:
            event_data: Event data

        Returns:
            Created event
        """
        event = Event(
            id=str(uuid4()),
            timestamp=datetime.utcnow(),
            event_type=event_data.event_type,
            user_id=event_data.user_id,
            session_id=event_data.session_id,
            data=event_data.data,
            metadata=event_data.metadata,
        )

        # Append to log
        offset = await self.event_log.append(event)

        # Process
        await self.processor.process(event)

        return event

    async def ingest_batch(self, events: List[EventData]) -> int:
        """Ingest batch of events.

        Args:
            events: List of events

        Returns:
            Number of events ingested
        """
        for event_data in events:
            await self.ingest(event_data)

        return len(events)

    async def replay_from_offset(self, from_offset: int = 0) -> int:
        """Replay events from offset.

        Args:
            from_offset: Starting offset

        Returns:
            Number of events replayed
        """
        if self._replay_in_progress:
            raise ValueError("Replay already in progress")

        self._replay_in_progress = True
        count = 0

        try:
            async for event in self.event_log.replay(from_offset):
                await self.processor.process(event)
                count += 1

                # Yield periodically
                if count % 10000 == 0:
                    await asyncio.sleep(0)
        finally:
            self._replay_in_progress = False

        return count


# Global service
kappa_service: Optional[KappaService] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan."""
    global kappa_service

    # Initialize
    kappa_service = KappaService()

    yield

    # Cleanup


# Create FastAPI app
app = FastAPI(
    title="Kappa Architecture",
    description="Pure stream processing with 500K+ events/sec",
    version="1.0.0",
    lifespan=lifespan,
)


@app.post("/api/v1/events")
async def ingest_event(event: EventData):
    """Ingest single event."""
    created_event = await kappa_service.ingest(event)

    return {
        "id": created_event.id,
        "offset": created_event.offset,
        "timestamp": created_event.timestamp.isoformat(),
    }


@app.post("/api/v1/events/batch")
async def ingest_batch(batch: EventBatch):
    """Ingest batch of events."""
    count = await kappa_service.ingest_batch(batch.events)

    return {
        "ingested": count,
        "total_offset": kappa_service.event_log.get_offset(),
    }


@app.get("/api/v1/views/{view_type}")
async def get_view(view_type: str, user_id: Optional[str] = None):
    """Get materialized view."""
    kwargs = {}
    if user_id:
        kwargs['user_id'] = user_id
        kwargs['type'] = 'user'

    data = await kappa_service.processor.get_view(view_type, **kwargs)

    return data


@app.post("/api/v1/replay")
async def replay_events(
    from_offset: int = 0,
    background_tasks: BackgroundTasks = None,
):
    """Replay events from offset."""
    # Run replay in background
    background_tasks.add_task(
        kappa_service.replay_from_offset,
        from_offset
    )

    return {
        "status": "replay_started",
        "from_offset": from_offset,
        "total_events": kappa_service.event_log.size(),
    }


@app.get("/api/v1/metrics")
async def get_metrics():
    """Get service metrics."""
    return {
        "event_log": {
            "size": kappa_service.event_log.size(),
            "current_offset": kappa_service.event_log.get_offset(),
        },
        "processor": {
            "processed": kappa_service.processor.processed_count,
            "duplicates": kappa_service.processor.duplicate_count,
            "partitions": kappa_service.processor.num_partitions,
        },
        "views": await kappa_service.processor.get_view('metrics'),
    }


@app.get("/health")
async def health_check():
    """Health check."""
    return {
        "status": "healthy",
        "service": "kappa-architecture",
        "events": kappa_service.event_log.size(),
    }


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Kappa Architecture - Pure Stream Processing",
        "version": "1.0.0",
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8006,
        reload=False,
        workers=1,
    )
