"""Event domain model for analytics system.

Events represent user actions or system occurrences that are tracked and analyzed.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional
from uuid import UUID, uuid4


class EventType(str, Enum):
    """Predefined event types."""

    # User events
    PAGE_VIEW = "page_view"
    BUTTON_CLICK = "button_click"
    FORM_SUBMIT = "form_submit"
    VIDEO_PLAY = "video_play"

    # E-commerce events
    PRODUCT_VIEW = "product_view"
    ADD_TO_CART = "add_to_cart"
    PURCHASE = "purchase"
    CHECKOUT_START = "checkout_start"

    # System events
    API_CALL = "api_call"
    ERROR = "error"
    LOGIN = "login"
    LOGOUT = "logout"

    # Custom
    CUSTOM = "custom"


@dataclass
class Event:
    """Event domain entity with __slots__ optimization.

    Represents a single event in the analytics system.
    Memory optimized with __slots__ for high-volume event processing.
    """

    __slots__ = (
        'id',
        'event_type',
        'user_id',
        'session_id',
        'properties',
        'timestamp',
        'source',
        'version',
    )

    id: UUID
    event_type: str
    user_id: str
    session_id: Optional[str]
    properties: Dict[str, Any]
    timestamp: datetime
    source: str
    version: str

    @classmethod
    def create(
        cls,
        event_type: str,
        user_id: str,
        properties: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None,
        source: str = "web",
        version: str = "1.0",
    ) -> "Event":
        """Create a new event.

        Args:
            event_type: Type of event
            user_id: User identifier
            properties: Event properties/metadata
            session_id: Session identifier (optional)
            source: Event source (web, mobile, api, etc.)
            version: Event schema version

        Returns:
            New Event instance
        """
        return cls(
            id=uuid4(),
            event_type=event_type,
            user_id=user_id,
            session_id=session_id,
            properties=properties or {},
            timestamp=datetime.utcnow(),
            source=source,
            version=version,
        )

    def get_property(self, key: str, default: Any = None) -> Any:
        """Get event property value.

        Args:
            key: Property key
            default: Default value if key not found

        Returns:
            Property value or default
        """
        return self.properties.get(key, default)

    def set_property(self, key: str, value: Any) -> "Event":
        """Set event property (returns new instance).

        Args:
            key: Property key
            value: Property value

        Returns:
            New Event instance with updated property
        """
        new_properties = self.properties.copy()
        new_properties[key] = value

        return Event(
            id=self.id,
            event_type=self.event_type,
            user_id=self.user_id,
            session_id=self.session_id,
            properties=new_properties,
            timestamp=self.timestamp,
            source=self.source,
            version=self.version,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary.

        Returns:
            Event as dictionary
        """
        return {
            'id': str(self.id),
            'event_type': self.event_type,
            'user_id': self.user_id,
            'session_id': self.session_id,
            'properties': self.properties,
            'timestamp': self.timestamp.isoformat(),
            'source': self.source,
            'version': self.version,
        }

    @property
    def event_key(self) -> str:
        """Generate unique event key for deduplication.

        Returns:
            Event key based on id and timestamp
        """
        return f"{self.id}:{self.timestamp.timestamp()}"

    def __repr__(self) -> str:
        return (
            f"Event(id={self.id}, type={self.event_type}, "
            f"user={self.user_id}, ts={self.timestamp})"
        )


@dataclass
class EventBatch:
    """Batch of events for efficient processing.

    Memory optimized with __slots__.
    """

    __slots__ = ('events', 'batch_id', 'received_at')

    events: list[Event]
    batch_id: UUID
    received_at: datetime

    @classmethod
    def create(cls, events: list[Event]) -> "EventBatch":
        """Create event batch.

        Args:
            events: List of events

        Returns:
            New EventBatch instance
        """
        return cls(
            events=events,
            batch_id=uuid4(),
            received_at=datetime.utcnow(),
        )

    @property
    def size(self) -> int:
        """Get batch size.

        Returns:
            Number of events in batch
        """
        return len(self.events)

    @property
    def event_types(self) -> set[str]:
        """Get unique event types in batch.

        Returns:
            Set of event types
        """
        return {e.event_type for e in self.events}

    @property
    def user_ids(self) -> set[str]:
        """Get unique user IDs in batch.

        Returns:
            Set of user IDs
        """
        return {e.user_id for e in self.events}

    def filter_by_type(self, event_type: str) -> list[Event]:
        """Filter events by type.

        Args:
            event_type: Event type to filter

        Returns:
            List of filtered events
        """
        return [e for e in self.events if e.event_type == event_type]

    def filter_by_user(self, user_id: str) -> list[Event]:
        """Filter events by user.

        Args:
            user_id: User ID to filter

        Returns:
            List of filtered events
        """
        return [e for e in self.events if e.user_id == user_id]

    def __repr__(self) -> str:
        return f"EventBatch(id={self.batch_id}, size={self.size}, ts={self.received_at})"
