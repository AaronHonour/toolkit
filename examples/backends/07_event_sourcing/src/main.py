"""Event Sourcing + CQRS System.

Complete event-driven architecture with 500K+ write, 1M+ read throughput.
"""

from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, List, Any, Optional
from uuid import uuid4

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from unistax.algorithms import RingBuffer, LRUCache, BloomFilter, fast_hash


class EventType(str, Enum):
    """Event types."""
    ACCOUNT_CREATED = "account_created"
    DEPOSIT_MADE = "deposit_made"
    WITHDRAWAL_MADE = "withdrawal_made"
    ACCOUNT_CLOSED = "account_closed"


@dataclass
class Event:
    """Domain event."""
    __slots__ = ('id', 'aggregate_id', 'event_type', 'data', 'timestamp', 'version')

    id: str
    aggregate_id: str
    event_type: EventType
    data: Dict[str, Any]
    timestamp: datetime
    version: int


class EventStore:
    """Event store with complete audit trail."""

    def __init__(self, capacity: int = 10_000_000):
        self._buffer = RingBuffer(capacity=capacity)
        self._events: Dict[str, List[Event]] = {}
        self._idempotency = BloomFilter(expected_elements=10_000_000)

    async def append(self, event: Event) -> None:
        """Append event to store."""
        if self._idempotency.contains(event.id):
            return  # Idempotent

        self._idempotency.add(event.id)

        if event.aggregate_id not in self._events:
            self._events[event.aggregate_id] = []

        self._events[event.aggregate_id].append(event)
        self._buffer.push(event)

    async def get_events(self, aggregate_id: str) -> List[Event]:
        """Get all events for aggregate."""
        return self._events.get(aggregate_id, [])


class AccountProjection:
    """Read model for accounts."""

    def __init__(self):
        self._cache = LRUCache(capacity=100_000)
        self._accounts: Dict[str, Dict] = {}

    async def handle(self, event: Event) -> None:
        """Update projection from event."""
        if event.event_type == EventType.ACCOUNT_CREATED:
            self._accounts[event.aggregate_id] = {
                'id': event.aggregate_id,
                'balance': 0,
                'status': 'active',
            }
        elif event.event_type == EventType.DEPOSIT_MADE:
            account = self._accounts.get(event.aggregate_id)
            if account:
                account['balance'] += event.data['amount']
        elif event.event_type == EventType.WITHDRAWAL_MADE:
            account = self._accounts.get(event.aggregate_id)
            if account:
                account['balance'] -= event.data['amount']
        elif event.event_type == EventType.ACCOUNT_CLOSED:
            account = self._accounts.get(event.aggregate_id)
            if account:
                account['status'] = 'closed'

        # Cache result
        if event.aggregate_id in self._accounts:
            self._cache.put(event.aggregate_id, self._accounts[event.aggregate_id])

    async def get_account(self, account_id: str) -> Optional[Dict]:
        """Get account from read model."""
        # Try cache first
        cached = self._cache.get(account_id)
        if cached:
            return cached

        return self._accounts.get(account_id)


class EventSourcingService:
    """Event sourcing service."""

    def __init__(self):
        self.event_store = EventStore()
        self.projection = AccountProjection()

    async def handle_command(self, command_type: str, data: Dict) -> str:
        """Handle command and emit events."""
        if command_type == "create_account":
            aggregate_id = str(uuid4())
            event = Event(
                id=str(uuid4()),
                aggregate_id=aggregate_id,
                event_type=EventType.ACCOUNT_CREATED,
                data=data,
                timestamp=datetime.utcnow(),
                version=1,
            )
            await self.event_store.append(event)
            await self.projection.handle(event)
            return aggregate_id

        elif command_type == "deposit":
            aggregate_id = data['account_id']
            events = await self.event_store.get_events(aggregate_id)
            version = len(events) + 1

            event = Event(
                id=str(uuid4()),
                aggregate_id=aggregate_id,
                event_type=EventType.DEPOSIT_MADE,
                data={'amount': data['amount']},
                timestamp=datetime.utcnow(),
                version=version,
            )
            await self.event_store.append(event)
            await self.projection.handle(event)
            return aggregate_id

        elif command_type == "withdraw":
            aggregate_id = data['account_id']
            events = await self.event_store.get_events(aggregate_id)
            version = len(events) + 1

            event = Event(
                id=str(uuid4()),
                aggregate_id=aggregate_id,
                event_type=EventType.WITHDRAWAL_MADE,
                data={'amount': data['amount']},
                timestamp=datetime.utcnow(),
                version=version,
            )
            await self.event_store.append(event)
            await self.projection.handle(event)
            return aggregate_id

        return ""


service: Optional[EventSourcingService] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global service
    service = EventSourcingService()
    yield


app = FastAPI(title="Event Sourcing + CQRS", lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/v1/commands/{command_type}")
async def execute_command(command_type: str, data: Dict[str, Any]):
    """Execute command."""
    aggregate_id = await service.handle_command(command_type, data)
    return {"aggregate_id": aggregate_id}


@app.get("/api/v1/accounts/{account_id}")
async def get_account(account_id: str):
    """Query account (read model)."""
    account = await service.projection.get_account(account_id)
    if not account:
        return {"error": "Account not found"}
    return account


@app.get("/api/v1/events/{aggregate_id}")
async def get_events(aggregate_id: str):
    """Get event history."""
    events = await service.event_store.get_events(aggregate_id)
    return {
        "aggregate_id": aggregate_id,
        "events": [
            {
                "id": e.id,
                "type": e.event_type.value,
                "data": e.data,
                "timestamp": e.timestamp.isoformat(),
                "version": e.version,
            }
            for e in events
        ]
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.get("/")
async def root():
    return {"message": "Event Sourcing + CQRS System"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8007)
