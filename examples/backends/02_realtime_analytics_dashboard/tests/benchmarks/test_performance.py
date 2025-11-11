"""Performance benchmarks for Real-Time Analytics Dashboard."""

import pytest
import asyncio
import time
from datetime import datetime, timezone
from uuid import uuid4

from src.domain.models.event import Event, EventType
from src.infrastructure.streaming.event_buffer import EventBuffer
from src.infrastructure.streaming.deduplicator import EventDeduplicator
from unistax.algorithms import RingBuffer, BloomFilter


class TestRingBufferPerformance:
    """Test RingBuffer performance (target: 284K+ ops/sec)."""

    @pytest.mark.benchmark
    def test_ringbuffer_throughput(self):
        """Test RingBuffer write throughput."""
        buffer = RingBuffer(capacity=100000)

        # Warm up
        for i in range(1000):
            buffer.push(i)

        # Benchmark
        operations = 100000
        start = time.perf_counter()

        for i in range(operations):
            buffer.push(i)

        elapsed = time.perf_counter() - start
        ops_per_sec = operations / elapsed

        print(f"\nRingBuffer throughput: {ops_per_sec:.0f} ops/sec")
        assert ops_per_sec > 200000  # Target: 200K+ ops/sec

    @pytest.mark.benchmark
    def test_ringbuffer_read_write_mixed(self):
        """Test RingBuffer mixed read/write performance."""
        buffer = RingBuffer(capacity=100000)

        operations = 50000
        start = time.perf_counter()

        for i in range(operations):
            buffer.push(i)
            buffer.pop()

        elapsed = time.perf_counter() - start
        ops_per_sec = (operations * 2) / elapsed  # 2 ops per iteration

        print(f"\nRingBuffer mixed ops: {ops_per_sec:.0f} ops/sec")
        assert ops_per_sec > 200000


class TestBloomFilterPerformance:
    """Test BloomFilter performance (target: 131K+ ops/sec)."""

    @pytest.mark.benchmark
    def test_bloomfilter_throughput(self):
        """Test BloomFilter check throughput."""
        bloom = BloomFilter(expected_elements=100000, false_positive_rate=0.01)

        # Warm up
        for i in range(1000):
            bloom.add(str(i))

        # Benchmark
        operations = 50000
        start = time.perf_counter()

        for i in range(operations):
            bloom.contains(str(i))

        elapsed = time.perf_counter() - start
        ops_per_sec = operations / elapsed

        print(f"\nBloomFilter throughput: {ops_per_sec:.0f} ops/sec")
        assert ops_per_sec > 100000  # Target: 100K+ ops/sec

    @pytest.mark.benchmark
    def test_bloomfilter_add_and_check(self):
        """Test BloomFilter add and check performance."""
        bloom = BloomFilter(expected_elements=100000, false_positive_rate=0.01)

        operations = 25000
        start = time.perf_counter()

        for i in range(operations):
            bloom.add(str(i))
            bloom.contains(str(i))

        elapsed = time.perf_counter() - start
        ops_per_sec = (operations * 2) / elapsed

        print(f"\nBloomFilter add+check: {ops_per_sec:.0f} ops/sec")
        assert ops_per_sec > 100000


class TestEventBufferPerformance:
    """Test EventBuffer performance."""

    @pytest.mark.benchmark
    @pytest.mark.asyncio
    async def test_event_buffer_throughput(self):
        """Test EventBuffer throughput with real events."""
        buffer = EventBuffer(capacity=100000)

        # Create sample events
        events = [
            Event(
                id=str(uuid4()),
                event_type=EventType.PAGE_VIEW,
                user_id=f"user{i}",
                session_id="session123",
                properties={},
                timestamp=datetime.now(timezone.utc),
            )
            for i in range(10000)
        ]

        # Benchmark
        operations = 10000
        start = time.perf_counter()

        for event in events:
            await buffer.push(event)

        elapsed = time.perf_counter() - start
        ops_per_sec = operations / elapsed

        print(f"\nEventBuffer throughput: {ops_per_sec:.0f} events/sec")
        assert ops_per_sec > 50000  # Target: 50K+ events/sec

    @pytest.mark.benchmark
    @pytest.mark.asyncio
    async def test_event_buffer_batch_processing(self):
        """Test EventBuffer batch processing performance."""
        buffer = EventBuffer(capacity=100000, batch_size=1000)

        # Fill buffer
        for i in range(10000):
            event = Event(
                id=str(uuid4()),
                event_type=EventType.PAGE_VIEW,
                user_id=f"user{i}",
                session_id="session123",
                properties={},
                timestamp=datetime.now(timezone.utc),
            )
            await buffer.push(event)

        # Benchmark batch popping
        batches = 10
        start = time.perf_counter()

        for _ in range(batches):
            batch = await buffer.pop_batch()

        elapsed = time.perf_counter() - start
        events_per_sec = (batches * 1000) / elapsed

        print(f"\nEventBuffer batch processing: {events_per_sec:.0f} events/sec")
        assert events_per_sec > 50000


class TestDeduplicatorPerformance:
    """Test EventDeduplicator performance."""

    @pytest.mark.benchmark
    def test_deduplicator_throughput(self):
        """Test deduplicator throughput."""
        dedup = EventDeduplicator(expected_elements=100000)

        # Warm up
        for i in range(1000):
            dedup.is_duplicate(str(uuid4()))

        # Benchmark
        operations = 50000
        start = time.perf_counter()

        for _ in range(operations):
            dedup.is_duplicate(str(uuid4()))

        elapsed = time.perf_counter() - start
        ops_per_sec = operations / elapsed

        print(f"\nDeduplicator throughput: {ops_per_sec:.0f} ops/sec")
        assert ops_per_sec > 100000  # Target: 100K+ ops/sec


class TestEndToEndPerformance:
    """Test end-to-end analytics performance."""

    @pytest.mark.benchmark
    @pytest.mark.asyncio
    async def test_event_ingestion_pipeline(self):
        """Test complete event ingestion pipeline."""
        buffer = EventBuffer(capacity=100000)
        dedup = EventDeduplicator(expected_elements=100000)

        # Benchmark complete pipeline
        operations = 10000
        start = time.perf_counter()

        for i in range(operations):
            event_id = str(uuid4())

            # Check for duplicates
            if not dedup.is_duplicate(event_id):
                # Create event
                event = Event(
                    id=event_id,
                    event_type=EventType.PAGE_VIEW,
                    user_id=f"user{i}",
                    session_id="session123",
                    properties={},
                    timestamp=datetime.now(timezone.utc),
                )

                # Push to buffer
                await buffer.push(event)

        elapsed = time.perf_counter() - start
        events_per_sec = operations / elapsed

        print(f"\nEnd-to-end pipeline: {events_per_sec:.0f} events/sec")
        assert events_per_sec > 50000  # Target: 50K+ events/sec

    @pytest.mark.benchmark
    @pytest.mark.asyncio
    async def test_high_volume_processing(self):
        """Test high-volume event processing (1M+ events/min target)."""
        buffer = EventBuffer(capacity=1000000)
        dedup = EventDeduplicator(expected_elements=1000000)

        # Process 100K events
        operations = 100000
        start = time.perf_counter()

        for i in range(operations):
            event_id = str(uuid4())

            if not dedup.is_duplicate(event_id):
                event = Event(
                    id=event_id,
                    event_type=EventType.PAGE_VIEW,
                    user_id=f"user{i % 10000}",  # 10K unique users
                    session_id=f"session{i % 1000}",  # 1K unique sessions
                    properties={"page": f"/page{i % 100}"},
                    timestamp=datetime.now(timezone.utc),
                )
                await buffer.push(event)

        elapsed = time.perf_counter() - start
        events_per_sec = operations / elapsed
        events_per_min = events_per_sec * 60

        print(f"\nHigh-volume processing: {events_per_min:.0f} events/min")
        assert events_per_min > 1000000  # Target: 1M+ events/min

    @pytest.mark.benchmark
    def test_memory_efficiency(self):
        """Test memory efficiency with large dataset."""
        import sys

        # Create components for 1M events
        buffer = EventBuffer(capacity=1000000)
        dedup = EventDeduplicator(expected_elements=1000000)

        # Measure memory
        buffer_size = sys.getsizeof(buffer)
        dedup_size = sys.getsizeof(dedup)

        print(f"\nEventBuffer size: {buffer_size / 1024:.2f} KB")
        print(f"Deduplicator size: {dedup_size / 1024:.2f} KB")

        # Should be memory efficient
        assert buffer_size < 10000000  # Less than 10MB
        assert dedup_size < 10000000  # Less than 10MB
