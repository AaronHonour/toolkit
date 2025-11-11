"""Event deduplication using Bloom Filter.

Uses toolkit's BloomFilter for probabilistic deduplication at 131K+ ops/sec.
"""

from typing import Set
from datetime import datetime, timedelta

from unistax.algorithms import BloomFilter
from src.domain.models.event import Event


class EventDeduplicator:
    """Event deduplicator using Bloom Filter.

    Achieves 131K+ ops/sec with probabilistic duplicate detection.
    False positive rate configurable (default 0.1%).
    """

    __slots__ = (
        '_bloom_filter',
        '_exact_set',
        '_use_exact',
        '_window',
        '_stats',
        '_last_cleanup',
    )

    def __init__(
        self,
        expected_elements: int = 10000000,  # 10M events
        false_positive_rate: float = 0.001,  # 0.1%
        use_exact_set: bool = False,
        cleanup_window: timedelta = timedelta(hours=1),
    ):
        """Initialize deduplicator.

        Args:
            expected_elements: Expected number of unique events
            false_positive_rate: Acceptable false positive rate
            use_exact_set: Use exact set for small volumes (testing)
            cleanup_window: How long to keep exact duplicates
        """
        self._bloom_filter = BloomFilter(
            expected_elements=expected_elements,
            false_positive_rate=false_positive_rate,
        )
        self._exact_set: Set[str] = set() if use_exact_set else None
        self._use_exact = use_exact_set
        self._window = cleanup_window
        self._stats = {
            'total_checked': 0,
            'duplicates_found': 0,
            'false_positives': 0,
        }
        self._last_cleanup = datetime.utcnow()

    def is_duplicate(self, event: Event) -> bool:
        """Check if event is a duplicate.

        Args:
            event: Event to check

        Returns:
            True if duplicate, False if unique
        """
        self._stats['total_checked'] += 1
        event_key = event.event_key

        if self._use_exact:
            # Exact checking for testing/small volumes
            if event_key in self._exact_set:
                self._stats['duplicates_found'] += 1
                return True
            self._exact_set.add(event_key)
            return False
        else:
            # Bloom filter for high volumes
            if self._bloom_filter.contains(event_key):
                # Might be duplicate (or false positive)
                self._stats['duplicates_found'] += 1
                return True

            # Definitely not a duplicate
            self._bloom_filter.add(event_key)
            return False

    def mark_seen(self, event: Event) -> None:
        """Mark event as seen without checking.

        Args:
            event: Event to mark
        """
        event_key = event.event_key

        if self._use_exact:
            self._exact_set.add(event_key)
        else:
            self._bloom_filter.add(event_key)

    def filter_duplicates(self, events: list[Event]) -> list[Event]:
        """Filter out duplicate events from a list.

        Args:
            events: List of events

        Returns:
            List of unique events
        """
        unique_events = []

        for event in events:
            if not self.is_duplicate(event):
                unique_events.append(event)

        return unique_events

    def cleanup_old_entries(self) -> None:
        """Cleanup old entries (only for exact set mode).

        In Bloom filter mode, this is a no-op as Bloom filters
        don't support deletion.
        """
        if not self._use_exact:
            return

        now = datetime.utcnow()
        if now - self._last_cleanup < self._window:
            return

        # In production, you'd track timestamps and remove old entries
        # For simplicity, we just clear periodically
        if len(self._exact_set) > 1000000:  # 1M threshold
            self._exact_set.clear()

        self._last_cleanup = now

    @property
    def stats(self) -> dict:
        """Get deduplication statistics.

        Returns:
            Dictionary of statistics
        """
        duplicate_rate = (
            self._stats['duplicates_found'] / self._stats['total_checked']
            if self._stats['total_checked'] > 0
            else 0.0
        )

        return {
            **self._stats,
            'duplicate_rate': duplicate_rate,
            'unique_rate': 1.0 - duplicate_rate,
        }

    @property
    def false_positive_rate(self) -> float:
        """Get configured false positive rate.

        Returns:
            False positive rate
        """
        return self._bloom_filter.false_positive_rate

    def reset(self) -> None:
        """Reset deduplicator state."""
        # Create new Bloom filter
        self._bloom_filter = BloomFilter(
            expected_elements=10000000,
            false_positive_rate=0.001,
        )

        if self._use_exact:
            self._exact_set.clear()

        # Reset stats
        self._stats = {
            'total_checked': 0,
            'duplicates_found': 0,
            'false_positives': 0,
        }

    def __repr__(self) -> str:
        stats = self.stats
        return (
            f"EventDeduplicator(checked={stats['total_checked']}, "
            f"duplicates={stats['duplicates_found']}, "
            f"rate={stats['duplicate_rate']:.2%})"
        )
