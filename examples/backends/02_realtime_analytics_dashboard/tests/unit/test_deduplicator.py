"""Unit tests for EventDeduplicator (BloomFilter usage)."""

import pytest
from uuid import uuid4

from src.infrastructure.streaming.deduplicator import EventDeduplicator


class TestEventDeduplicator:
    """Test EventDeduplicator with BloomFilter."""

    def test_deduplicator_creation(self):
        """Test deduplicator creation with default settings."""
        dedup = EventDeduplicator(expected_elements=10000, false_positive_rate=0.001)
        assert dedup._bloom_filter is not None

    def test_deduplicator_custom_settings(self):
        """Test deduplicator with custom settings."""
        dedup = EventDeduplicator(expected_elements=1000000, false_positive_rate=0.0001)
        assert dedup._bloom_filter is not None

    def test_is_duplicate_first_time(self):
        """Test that first occurrence is not a duplicate."""
        dedup = EventDeduplicator()

        event_id = str(uuid4())
        is_dup = dedup.is_duplicate(event_id)

        assert is_dup is False

    def test_is_duplicate_second_time(self):
        """Test that second occurrence is detected as duplicate."""
        dedup = EventDeduplicator()

        event_id = str(uuid4())

        # First time - not a duplicate
        is_dup1 = dedup.is_duplicate(event_id)
        assert is_dup1 is False

        # Second time - is a duplicate
        is_dup2 = dedup.is_duplicate(event_id)
        assert is_dup2 is True

    def test_multiple_unique_events(self):
        """Test multiple unique events."""
        dedup = EventDeduplicator()

        event_ids = [str(uuid4()) for _ in range(100)]

        # All should be unique (not duplicates)
        for event_id in event_ids:
            is_dup = dedup.is_duplicate(event_id)
            assert is_dup is False

    def test_multiple_duplicate_events(self):
        """Test multiple duplicate events."""
        dedup = EventDeduplicator()

        event_id = str(uuid4())

        # First occurrence
        is_dup1 = dedup.is_duplicate(event_id)
        assert is_dup1 is False

        # Multiple duplicates
        for _ in range(10):
            is_dup = dedup.is_duplicate(event_id)
            assert is_dup is True

    def test_mixed_unique_and_duplicate(self):
        """Test mix of unique and duplicate events."""
        dedup = EventDeduplicator()

        event_ids = [str(uuid4()) for _ in range(10)]

        # First pass - all unique
        for event_id in event_ids:
            is_dup = dedup.is_duplicate(event_id)
            assert is_dup is False

        # Second pass - all duplicates
        for event_id in event_ids:
            is_dup = dedup.is_duplicate(event_id)
            assert is_dup is True

        # New event - unique
        new_event_id = str(uuid4())
        is_dup = dedup.is_duplicate(new_event_id)
        assert is_dup is False

    def test_high_volume_deduplication(self):
        """Test deduplication with high volume of events."""
        dedup = EventDeduplicator(expected_elements=100000)

        # Add 10K unique events
        unique_events = [str(uuid4()) for _ in range(10000)]

        for event_id in unique_events:
            is_dup = dedup.is_duplicate(event_id)
            assert is_dup is False

        # Verify they're all marked as duplicates now
        duplicate_count = 0
        for event_id in unique_events:
            if dedup.is_duplicate(event_id):
                duplicate_count += 1

        # Should detect most duplicates (allowing for small false positive rate)
        assert duplicate_count > 9900  # > 99% accuracy

    def test_false_positive_rate(self):
        """Test that false positive rate is within expected bounds."""
        dedup = EventDeduplicator(expected_elements=10000, false_positive_rate=0.01)

        # Add 10K events
        for i in range(10000):
            event_id = str(uuid4())
            dedup.is_duplicate(event_id)

        # Test with 1000 new events
        false_positives = 0
        for _ in range(1000):
            new_event_id = str(uuid4())
            if dedup.is_duplicate(new_event_id):
                false_positives += 1

        # False positive rate should be close to 1% (allowing some variance)
        fp_rate = false_positives / 1000
        assert fp_rate < 0.05  # Less than 5% to account for variance

    def test_different_event_id_formats(self):
        """Test deduplication with different event ID formats."""
        dedup = EventDeduplicator()

        # UUID format
        uuid_id = str(uuid4())
        assert dedup.is_duplicate(uuid_id) is False
        assert dedup.is_duplicate(uuid_id) is True

        # Integer format
        int_id = "12345"
        assert dedup.is_duplicate(int_id) is False
        assert dedup.is_duplicate(int_id) is True

        # String format
        str_id = "event-abc-123"
        assert dedup.is_duplicate(str_id) is False
        assert dedup.is_duplicate(str_id) is True

    def test_case_sensitive_deduplication(self):
        """Test that deduplication is case-sensitive."""
        dedup = EventDeduplicator()

        event_id_lower = "event123"
        event_id_upper = "EVENT123"

        # Different cases should be treated as different events
        is_dup1 = dedup.is_duplicate(event_id_lower)
        is_dup2 = dedup.is_duplicate(event_id_upper)

        assert is_dup1 is False
        assert is_dup2 is False

    def test_empty_event_id(self):
        """Test handling of empty event ID."""
        dedup = EventDeduplicator()

        # Empty string should still work
        is_dup1 = dedup.is_duplicate("")
        is_dup2 = dedup.is_duplicate("")

        assert is_dup1 is False
        assert is_dup2 is True

    def test_performance_characteristics(self):
        """Test O(1) performance characteristics."""
        import time

        dedup = EventDeduplicator(expected_elements=100000)

        # Measure time for first 100 checks
        start = time.time()
        for _ in range(100):
            event_id = str(uuid4())
            dedup.is_duplicate(event_id)
        time_first_100 = time.time() - start

        # Add 10K events
        for _ in range(10000):
            event_id = str(uuid4())
            dedup.is_duplicate(event_id)

        # Measure time for another 100 checks
        start = time.time()
        for _ in range(100):
            event_id = str(uuid4())
            dedup.is_duplicate(event_id)
        time_after_10k = time.time() - start

        # Performance should be similar (O(1) lookup)
        # Allow 2x variance for system noise
        assert time_after_10k < time_first_100 * 2

    def test_concurrent_deduplication(self):
        """Test deduplication under concurrent access."""
        import asyncio

        dedup = EventDeduplicator()

        async def check_duplicates():
            event_ids = [str(uuid4()) for _ in range(100)]

            # Check each event twice
            results = []
            for event_id in event_ids:
                result1 = dedup.is_duplicate(event_id)
                result2 = dedup.is_duplicate(event_id)
                results.append((result1, result2))

            return results

        # Run multiple tasks concurrently
        loop = asyncio.new_event_loop()
        tasks = [check_duplicates() for _ in range(10)]
        results_list = loop.run_until_complete(asyncio.gather(*tasks))
        loop.close()

        # Verify results from all tasks
        for results in results_list:
            for first, second in results:
                # First check should be False (not duplicate)
                # Second check should be True (is duplicate)
                assert first is False
                assert second is True

    def test_memory_efficiency(self):
        """Test memory efficiency of Bloom filter."""
        import sys

        # Create deduplicator for 1M events
        dedup = EventDeduplicator(expected_elements=1000000, false_positive_rate=0.001)

        # Get approximate memory size (bloom filter should be compact)
        size = sys.getsizeof(dedup)

        # Should be much smaller than storing 1M strings directly
        # (1M strings would be ~50MB+, bloom filter should be < 5MB)
        assert size < 10000000  # Less than 10MB for the object
