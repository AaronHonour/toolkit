"""Event bus implementation."""

import asyncio
import inspect
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from typing import Any, TypeVar
from uuid import uuid4

T = TypeVar("T", bound="Event")


@dataclass
class Event:
    """Base event class."""

    event_id: str | None = None
    timestamp: datetime | None = None

    def __post_init__(self) -> None:
        """Initialize defaults."""
        if self.event_id is None:
            self.event_id = str(uuid4())
        if self.timestamp is None:
            self.timestamp = datetime.now()


class EventBus:
    """Event bus for pub/sub pattern.

    Examples:
        >>> bus = EventBus()
        >>>
        >>> @bus.subscribe(UserCreated)
        ... async def on_user_created(event: UserCreated):
        ...     await send_email(event.user_id)
        >>>
        >>> await bus.publish(UserCreated(user_id=123))
    """

    def __init__(self) -> None:
        """Initialize EventBus."""
        self._handlers: dict[type[Event], list[Callable[..., Any]]] = {}

    def subscribe(self, event_type: type[T]) -> Callable[..., Any]:
        """Subscribe to event type.

        Args:
            event_type: Event class to subscribe to

        Returns:
            Decorator function
        """

        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            if event_type not in self._handlers:
                self._handlers[event_type] = []
            self._handlers[event_type].append(func)
            return func

        return decorator

    async def publish(self, event: Event) -> None:
        """Publish event to all subscribers.

        Args:
            event: Event instance
        """
        event_type = type(event)

        if event_type not in self._handlers:
            return

        # Execute all handlers
        tasks = []
        for handler in self._handlers[event_type]:
            if inspect.iscoroutinefunction(handler):
                tasks.append(handler(event))
            else:
                # Run sync handlers in executor
                loop = asyncio.get_event_loop()
                tasks.append(loop.run_in_executor(None, handler, event))

        # Wait for all handlers
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    def unsubscribe(self, event_type: type[Event], handler: Callable[..., Any]) -> None:
        """Unsubscribe handler from event."""
        if event_type in self._handlers:
            self._handlers[event_type] = [h for h in self._handlers[event_type] if h != handler]


def event_handler(event_type: type[Event]) -> Callable[..., Any]:
    """Decorator to mark function as event handler.

    Args:
        event_type: Event type to handle

    Returns:
        Decorator function
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        func.__event_type__ = event_type  # type: ignore[attr-defined]
        return func

    return decorator
