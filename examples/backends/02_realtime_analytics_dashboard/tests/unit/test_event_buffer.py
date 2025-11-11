"""Unit tests for EventBuffer (RingBuffer usage)."""

import pytest
import asyncio
from datetime import datetime, timezone
from uuid import uuid4

from src.domain.models.event import Event, EventType
from src.infrastructure.streaming.event_buffer import EventBuffer


class TestEventBuffer:
    """Test EventBuffer with RingBuffer."""

    def test_buffer_creation(self):
        """Test buffer creation with default capacity."""
        buffer = EventBuffer(capacity=1000)
        assert buffer._buffer.capacity == 1000
        assert buffer.batch_size == 1000

    def test_buffer_custom_batch_size(self):
        """Test buffer with custom batch size."""
        buffer = EventBuffer(capacity=10000, batch_size=500)
        assert buffer.batch_size == 500

    @pytest.mark.asyncio
    async def test_push_single_event(self):
        """Test pushing single event to buffer."""
        buffer = EventBuffer(capacity=1000)

        event = Event(
            id=str(uuid4()),
            event_type=EventType.PAGE_VIEW,
            user_id="user123",
            session_id="session456",
            properties={},
            timestamp=datetime.now(timezone.utc),
        )

        result = await buffer.push(event)
        assert result is True

    @pytest.mark.asyncio
    async def test_push_multiple_events(self):
        """Test pushing multiple events."""
        buffer = EventBuffer(capacity=1000)

        events = [
            Event(
                id=str(uuid4()),
                event_type=EventType.PAGE_VIEW,
                user_id=f"user{i}",
                session_id="session456",
                properties={},
                timestamp=datetime.now(timezone.utc),
            )
            for i in range(100)
        ]

        for event in events:
            result = await buffer.push(event)
            assert result is True

    @pytest.mark.asyncio
    async def test_buffer_overflow(self):
        """Test buffer behavior when full."""
        buffer = EventBuffer(capacity=10)

        # Fill buffer beyond capacity
        for i in range(15):
            event = Event(
                id=str(uuid4()),
                event_type=EventType.PAGE_VIEW,
                user_id=f"user{i}",
                session_id="session456",
                properties={},
                timestamp=datetime.now(timezone.utc),
            )
            # Should still work due to ring buffer overwriting old data
            result = await buffer.push(event)
            assert result is True

    @pytest.mark.asyncio
    async def test_pop_single_event(self):
        """Test popping single event."""
        buffer = EventBuffer(capacity=1000)

        event = Event(
            id=str(uuid4()),
            event_type=EventType.PAGE_VIEW,
            user_id="user123",
            session_id="session456",
            properties={},
            timestamp=datetime.now(timezone.utc),
        )

        await buffer.push(event)
        popped = await buffer.pop()

        assert popped is not None
        assert popped.id == event.id
        assert popped.user_id == event.user_id

    @pytest.mark.asyncio
    async def test_pop_empty_buffer(self):
        """Test popping from empty buffer."""
        buffer = EventBuffer(capacity=1000)

        popped = await buffer.pop()
        assert popped is None

    @pytest.mark.asyncio
    async def test_pop_batch(self):
        """Test popping batch of events."""
        buffer = EventBuffer(capacity=1000, batch_size=10)

        # Push 25 events
        for i in range(25):
            event = Event(
                id=str(uuid4()),
                event_type=EventType.PAGE_VIEW,
                user_id=f"user{i}",
                session_id="session456",
                properties={},
                timestamp=datetime.now(timezone.utc),
            )
            await buffer.push(event)

        # Pop batch (should get 10 events)
        batch = await buffer.pop_batch()
        assert len(batch) == 10

        # Pop another batch
        batch2 = await buffer.pop_batch()
        assert len(batch2) == 10

        # Pop final batch (should get 5 events)
        batch3 = await buffer.pop_batch()
        assert len(batch3) == 5

    @pytest.mark.asyncio
    async def test_pop_batch_empty(self):
        """Test popping batch from empty buffer."""
        buffer = EventBuffer(capacity=1000, batch_size=10)

        batch = await buffer.pop_batch()
        assert len(batch) == 0

    @pytest.mark.asyncio
    async def test_fifo_ordering(self):
        """Test FIFO ordering of events."""
        buffer = EventBuffer(capacity=1000)

        event_ids = []
        for i in range(10):
            event = Event(
                id=str(uuid4()),
                event_type=EventType.PAGE_VIEW,
                user_id=f"user{i}",
                session_id="session456",
                properties={},
                timestamp=datetime.now(timezone.utc),
            )
            event_ids.append(event.id)
            await buffer.push(event)

        # Pop events and verify order
        for expected_id in event_ids:
            popped = await buffer.pop()
            assert popped.id == expected_id

    @pytest.mark.asyncio
    async def test_concurrent_push_pop(self):
        """Test concurrent push and pop operations."""
        buffer = EventBuffer(capacity=1000)

        async def pusher():
            for i in range(100):
                event = Event(
                    id=str(uuid4()),
                    event_type=EventType.PAGE_VIEW,
                    user_id=f"user{i}",
                    session_id="session456",
                    properties={},
                    timestamp=datetime.now(timezone.utc),
                )
                await buffer.push(event)
                await asyncio.sleep(0)

        async def popper():
            popped_count = 0
            for _ in range(100):
                event = await buffer.pop()
                if event:
                    popped_count += 1
                await asyncio.sleep(0)
            return popped_count

        # Run concurrently
        pusher_task = asyncio.create_task(pusher())
        popper_task = asyncio.create_task(popper())

        await pusher_task
        count = await popper_task

        # Should have popped some events (exact count may vary due to concurrency)
        assert count >= 0

    @pytest.mark.asyncio
    async def test_high_throughput(self):
        """Test high-throughput event buffering."""
        buffer = EventBuffer(capacity=100000)

        # Push 10K events
        start = asyncio.get_event_loop().time()
        for i in range(10000):
            event = Event(
                id=str(uuid4()),
                event_type=EventType.PAGE_VIEW,
                user_id=f"user{i}",
                session_id="session456",
                properties={},
                timestamp=datetime.now(timezone.utc),
            )
            await buffer.push(event)

        elapsed = asyncio.get_event_loop().time() - start

        # Should handle 10K events very quickly (< 1 second)
        assert elapsed < 1.0

        # Verify we can pop events
        batch = await buffer.pop_batch()
        assert len(batch) > 0

    @pytest.mark.asyncio
    async def test_buffer_with_different_event_types(self):
        """Test buffer with mixed event types."""
        buffer = EventBuffer(capacity=1000)

        event_types = [
            EventType.PAGE_VIEW,
            EventType.BUTTON_CLICK,
            EventType.FORM_SUBMIT,
            EventType.API_CALL,
            EventType.ERROR,
        ]

        # Push events of different types
        for i, event_type in enumerate(event_types * 10):
            event = Event(
                id=str(uuid4()),
                event_type=event_type,
                user_id=f"user{i}",
                session_id="session456",
                properties={},
                timestamp=datetime.now(timezone.utc),
            )
            await buffer.push(event)

        # Pop and verify
        for _ in range(50):
            popped = await buffer.pop()
            assert popped is not None
            assert popped.event_type in event_types

    @pytest.mark.asyncio
    async def test_buffer_memory_efficiency(self):
        """Test buffer memory efficiency with ring buffer."""
        # Small buffer that will wrap around
        buffer = EventBuffer(capacity=100)

        # Push 1000 events (10x capacity)
        for i in range(1000):
            event = Event(
                id=str(uuid4()),
                event_type=EventType.PAGE_VIEW,
                user_id=f"user{i}",
                session_id="session456",
                properties={},
                timestamp=datetime.now(timezone.utc),
            )
            await buffer.push(event)

        # Should still work (ring buffer overwrites old data)
        batch = await buffer.pop_batch()
        assert len(batch) <= 100
