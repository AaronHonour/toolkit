"""Async operation helpers for better performance."""

import asyncio
from collections.abc import Callable, Coroutine
from concurrent.futures import ThreadPoolExecutor
from typing import Any, TypeVar

T = TypeVar("T")


class AsyncPool:
    """Async operation pool for concurrent execution."""

    def __init__(self, max_workers: int = 10) -> None:
        """Initialize async pool.

        Args:
            max_workers: Maximum concurrent workers
        """
        self.max_workers = max_workers
        self.semaphore = asyncio.Semaphore(max_workers)

    async def execute(self, coro: Coroutine[Any, Any, T]) -> T:
        """Execute coroutine with semaphore.

        Args:
            coro: Coroutine to execute

        Returns:
            Coroutine result
        """
        async with self.semaphore:
            return await coro

    async def map(self, func: Callable[[Any], Coroutine[Any, Any, T]], items: list[Any]) -> list[T]:
        """Map async function over items concurrently.

        Args:
            func: Async function
            items: Items to process

        Returns:
            List of results
        """
        tasks = [self.execute(func(item)) for item in items]
        return await asyncio.gather(*tasks)


async def async_batch(
    items: list[T], batch_size: int, processor: Callable[[list[T]], Coroutine[Any, Any, Any]]
) -> Any:
    """Process items in async batches.

    Args:
        items: Items to process
        batch_size: Batch size
        processor: Async batch processor

    Example:
        async def process_batch(items):
            return await db.bulk_insert(items)

        await async_batch(items, 100, process_batch)
    """
    tasks = []
    for i in range(0, len(items), batch_size):
        batch = items[i : i + batch_size]
        tasks.append(processor(batch))

    return await asyncio.gather(*tasks)


def run_in_executor(
    func: Callable[..., Any], *args: Any, executor: ThreadPoolExecutor | None = None, **kwargs: Any
) -> Any:
    """Run blocking function in executor.

    Args:
        func: Blocking function
        *args: Function arguments
        executor: Optional thread pool executor
        **kwargs: Function keyword arguments

    Returns:
        Coroutine that runs function in executor
    """
    loop = asyncio.get_event_loop()
    return loop.run_in_executor(executor, lambda: func(*args, **kwargs))
