"""Real-Time Analytics Dashboard - Main Application.

High-performance analytics system with 1M+ events/sec capability.
"""

import asyncio
from contextlib import asynccontextmanager
from datetime import timedelta
from typing import List, Dict, Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from src.domain.models.event import Event, EventType
from src.infrastructure.streaming.event_buffer import (
    EventBuffer,
    EventBufferReader,
)
from src.infrastructure.streaming.deduplicator import (
    EventDeduplicator,
)
from src.infrastructure.event_store.memory_store import (
    InMemoryEventStore,
)
from src.application.projections.analytics_projection import (
    AnalyticsProjection,
)


# Global state
event_buffer: EventBuffer = None
deduplicator: EventDeduplicator = None
event_store: InMemoryEventStore = None
projection: AnalyticsProjection = None
websocket_manager: 'WebSocketManager' = None


class WebSocketManager:
    """Manages WebSocket connections for real-time updates."""

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass  # Connection closed


# Pydantic models
class EventCreate(BaseModel):
    event_type: str
    user_id: str
    properties: Dict[str, Any] = {}
    session_id: str | None = None
    source: str = "web"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global event_buffer, deduplicator, event_store, projection, websocket_manager

    # Initialize components
    event_buffer = EventBuffer(capacity=1000000, batch_size=1000)
    deduplicator = EventDeduplicator(expected_elements=10000000)
    event_store = InMemoryEventStore()
    projection = AnalyticsProjection(window_size=timedelta(hours=1))
    websocket_manager = WebSocketManager()

    # Start event processor
    async def process_events(batch):
        # Filter duplicates
        unique_events = deduplicator.filter_duplicates(batch.events)

        # Store events
        event_store.append_batch(unique_events)

        # Update projections
        projection.handle_batch(batch)

    reader = EventBufferReader(event_buffer, batch_size=1000)
    processor_task = asyncio.create_task(reader.start(process_events))

    # Start WebSocket broadcaster
    async def broadcast_metrics():
        while True:
            try:
                snapshot = projection.get_snapshot()
                await websocket_manager.broadcast(snapshot.to_dict())
            except:
                pass
            await asyncio.sleep(1)  # Update every second

    broadcaster_task = asyncio.create_task(broadcast_metrics())

    yield

    # Cleanup
    reader.stop()
    processor_task.cancel()
    broadcaster_task.cancel()


# Create FastAPI app
app = FastAPI(
    title="Real-Time Analytics Dashboard",
    description="High-performance analytics with 1M+ events/sec capability",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Event Ingestion Endpoints
@app.post("/api/v1/events", status_code=201)
async def ingest_event(event_data: EventCreate) -> Dict:
    """Ingest single event."""
    event = Event.create(
        event_type=event_data.event_type,
        user_id=event_data.user_id,
        properties=event_data.properties,
        session_id=event_data.session_id,
        source=event_data.source,
    )

    if event_buffer.write(event):
        return {"status": "accepted", "event_id": str(event.id)}
    else:
        raise HTTPException(status_code=503, detail="Buffer full, try again")


@app.post("/api/v1/events/batch", status_code=201)
async def ingest_events_batch(events_data: List[EventCreate]) -> Dict:
    """Ingest batch of events."""
    events = [
        Event.create(
            event_type=e.event_type,
            user_id=e.user_id,
            properties=e.properties,
            session_id=e.session_id,
            source=e.source,
        )
        for e in events_data
    ]

    written = event_buffer.write_batch(events)
    return {
        "status": "accepted",
        "total": len(events),
        "written": written,
        "rejected": len(events) - written,
    }


# Analytics Query Endpoints
@app.get("/api/v1/analytics/metrics")
async def get_metrics():
    """Get current metrics snapshot."""
    snapshot = projection.get_snapshot()
    return snapshot.to_dict()


@app.get("/api/v1/analytics/events/count")
async def get_event_counts():
    """Get event counts by type."""
    return projection.get_event_counts()


@app.get("/api/v1/analytics/users/top")
async def get_top_users(limit: int = Query(10, ge=1, le=100)):
    """Get most active users."""
    top_users = projection.get_top_users(limit=limit)
    return [
        {"user_id": user_id, "event_count": count}
        for user_id, count in top_users
    ]


@app.get("/api/v1/analytics/timeseries")
async def get_time_series(
    metric: str = Query(..., description="Metric name"),
    last_n: int = Query(60, ge=1, le=1000, description="Number of data points"),
):
    """Get time series data."""
    data = projection.get_time_series(metric, last_n=last_n)
    return {
        "metric": metric,
        "data_points": [
            {"timestamp": ts.isoformat(), "value": val}
            for ts, val in data
        ],
    }


@app.get("/api/v1/analytics/histograms/{metric_name}")
async def get_histogram(metric_name: str):
    """Get histogram percentiles."""
    percentiles = projection.get_histogram_percentiles(metric_name)
    if not percentiles:
        raise HTTPException(status_code=404, detail="Histogram not found")
    return percentiles


# WebSocket Endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time updates."""
    await websocket_manager.connect(websocket)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)


# Health Check
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "analytics-dashboard",
        "buffer": event_buffer.stats,
        "deduplicator": deduplicator.stats,
        "store": event_store.stats,
        "projection": projection.stats,
        "websocket_clients": len(websocket_manager.active_connections),
    }


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Real-Time Analytics Dashboard",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "websocket": "ws://localhost:8001/ws",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=False,
        workers=1,
        log_level="info",
    )
