"""Lifecycle hooks."""

import asyncio
import inspect
from typing import Any, Callable


class LifecycleHook:
    """
    Lifecycle hook wrapper.

    Handles both sync and async functions.
    """

    def __init__(self, event: str, func: Callable):
        self.event = event
        self.func = func
        self.is_async = inspect.iscoroutinefunction(func)

    async def execute(self) -> Any:
        """
        Execute the hook function.

        Returns:
            Function result
        """
        if self.is_async:
            return await self.func()
        else:
            # Run sync function in executor
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, self.func)

    def __repr__(self) -> str:
        return f"LifecycleHook(event={self.event}, func={self.func.__name__})"
