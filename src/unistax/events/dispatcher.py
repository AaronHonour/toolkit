"""Event dispatcher for routing events."""

from typing import Any, Callable, Dict, List, Type

from .bus import Event


class EventDispatcher:
    """
    Event dispatcher with priority and filtering.

    Extends EventBus with additional features.
    """

    def __init__(self):
        self._handlers: Dict[Type[Event], List[tuple[int, Callable]]] = {}

    def register(
        self, event_type: Type[Event], handler: Callable, priority: int = 0
    ) -> None:
        """
        Register event handler with priority.

        Args:
            event_type: Event type
            handler: Handler function
            priority: Handler priority (higher = earlier)
        """
        if event_type not in self._handlers:
            self._handlers[event_type] = []

        self._handlers[event_type].append((priority, handler))
        # Sort by priority (descending)
        self._handlers[event_type].sort(key=lambda x: x[0], reverse=True)

    async def dispatch(self, event: Event) -> None:
        """Dispatch event to handlers in priority order."""
        event_type = type(event)

        if event_type not in self._handlers:
            return

        for priority, handler in self._handlers[event_type]:
            await handler(event)
