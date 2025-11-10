"""In-memory event store for fast access.

Provides event sourcing capabilities with in-memory storage.
"""

from collections import defaultdict
from datetime import datetime, timedelta
from typing import List, Optional, Dict
from uuid import UUID

from src.domain.models.event import Event


class InMemoryEventStore:
    """In-memory event store for event sourcing.

    Stores events in memory for fast access and replay.
    For production, consider adding persistent storage (PostgreSQL, EventStoreDB).
    """

    __slots__ = ('_events', '_events_by_type', '_events_by_user', '_stats')

    def __init__(self):
        """Initialize event store."""
        self._events: List[Event] = []
        self._events_by_type: Dict[str, List[Event]] = defaultdict(list)
        self._events_by_user: Dict[str, List[Event]] = defaultdict(list)
        self._stats = {
            'total_events': 0,
            'events_by_type': defaultdict(int),
            'first_event_time': None,
            'last_event_time': None,
        }

    def append(self, event: Event) -> None:
        """Append event to store.

        Args:
            event: Event to append
        """
        self._events.append(event)
        self._events_by_type[event.event_type].append(event)
        self._events_by_user[event.user_id].append(event)

        # Update stats
        self._stats['total_events'] += 1
        self._stats['events_by_type'][event.event_type] += 1

        if self._stats['first_event_time'] is None:
            self._stats['first_event_time'] = event.timestamp

        self._stats['last_event_time'] = event.timestamp

    def append_batch(self, events: List[Event]) -> None:
        """Append batch of events.

        Args:
            events: List of events to append
        """
        for event in events:
            self.append(event)

    def get_by_id(self, event_id: UUID) -> Optional[Event]:
        """Get event by ID.

        Args:
            event_id: Event ID

        Returns:
            Event if found, None otherwise
        """
        for event in self._events:
            if event.id == event_id:
                return event
        return None

    def get_by_type(
        self,
        event_type: str,
        limit: Optional[int] = None,
    ) -> List[Event]:
        """Get events by type.

        Args:
            event_type: Event type
            limit: Maximum number of events

        Returns:
            List of events
        """
        events = self._events_by_type[event_type]
        if limit:
            return events[-limit:]
        return events

    def get_by_user(
        self,
        user_id: str,
        limit: Optional[int] = None,
    ) -> List[Event]:
        """Get events by user.

        Args:
            user_id: User ID
            limit: Maximum number of events

        Returns:
            List of events
        """
        events = self._events_by_user[user_id]
        if limit:
            return events[-limit:]
        return events

    def get_by_time_range(
        self,
        start: datetime,
        end: datetime,
        event_type: Optional[str] = None,
    ) -> List[Event]:
        """Get events within time range.

        Args:
            start: Start time
            end: End time
            event_type: Filter by event type (optional)

        Returns:
            List of events in range
        """
        events = self._events if event_type is None else self._events_by_type[event_type]

        return [
            event for event in events
            if start <= event.timestamp <= end
        ]

    def get_recent(
        self,
        duration: timedelta,
        event_type: Optional[str] = None,
    ) -> List[Event]:
        """Get recent events within duration.

        Args:
            duration: Time duration to look back
            event_type: Filter by event type (optional)

        Returns:
            List of recent events
        """
        end = datetime.utcnow()
        start = end - duration

        return self.get_by_time_range(start, end, event_type)

    def get_all(
        self,
        skip: int = 0,
        limit: Optional[int] = None,
    ) -> List[Event]:
        """Get all events with pagination.

        Args:
            skip: Number of events to skip
            limit: Maximum number of events

        Returns:
            List of events
        """
        events = self._events[skip:]
        if limit:
            events = events[:limit]
        return events

    def count_by_type(self) -> Dict[str, int]:
        """Get event counts by type.

        Returns:
            Dictionary of event type to count
        """
        return dict(self._stats['events_by_type'])

    def count_total(self) -> int:
        """Get total event count.

        Returns:
            Total number of events
        """
        return self._stats['total_events']

    def get_unique_users(self) -> int:
        """Get count of unique users.

        Returns:
            Number of unique users
        """
        return len(self._events_by_user)

    def get_event_types(self) -> List[str]:
        """Get all event types.

        Returns:
            List of event types
        """
        return list(self._events_by_type.keys())

    @property
    def stats(self) -> dict:
        """Get store statistics.

        Returns:
            Dictionary of statistics
        """
        return {
            'total_events': self._stats['total_events'],
            'unique_users': self.get_unique_users(),
            'event_types': len(self._events_by_type),
            'events_by_type': dict(self._stats['events_by_type']),
            'first_event_time': (
                self._stats['first_event_time'].isoformat()
                if self._stats['first_event_time']
                else None
            ),
            'last_event_time': (
                self._stats['last_event_time'].isoformat()
                if self._stats['last_event_time']
                else None
            ),
        }

    def clear(self) -> None:
        """Clear all events from store."""
        self._events.clear()
        self._events_by_type.clear()
        self._events_by_user.clear()
        self._stats = {
            'total_events': 0,
            'events_by_type': defaultdict(int),
            'first_event_time': None,
            'last_event_time': None,
        }

    def __len__(self) -> int:
        return len(self._events)

    def __repr__(self) -> str:
        return (
            f"InMemoryEventStore(events={len(self._events)}, "
            f"users={self.get_unique_users()}, "
            f"types={len(self._events_by_type)})"
        )
