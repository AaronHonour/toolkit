"""Event System Module.

Provides pub/sub event bus with:
- Event definition and typing
- Multiple handlers per event
- Async/sync support
- Event filtering
"""

from .bus import Event, EventBus, event_handler
from .dispatcher import EventDispatcher

__all__ = ["EventBus", "Event", "event_handler", "EventDispatcher"]
