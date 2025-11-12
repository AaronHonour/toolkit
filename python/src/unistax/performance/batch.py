"""Batch processing for improved performance."""

import asyncio
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass
from queue import Empty, Queue
from typing import TypeVar

T = TypeVar("T")
R = TypeVar("R")


@dataclass
class BatchConfig:
    """Batch processing configuration."""

    max_batch_size: int = 100
    max_wait_time: float = 0.1  # seconds
    max_retries: int = 3


class BatchProcessor:
    """Batch multiple operations for efficiency."""

    def __init__(
        self,
        processor_func: Callable[[list[T]], list[R]],
        config: BatchConfig | None = None
    ):
        """Initialize batch processor.

        Args:
            processor_func: Function to process batch
            config: Batch configuration

        Example:
            def process_batch(items):
                return db.bulk_insert(items)

            processor = BatchProcessor(process_batch)
            result = processor.add(item)
        """
        self.processor_func = processor_func
        self.config = config or BatchConfig()

        self.queue: Queue = Queue()
        self.results: dict = {}
        self.lock = threading.Lock()
        self.worker_thread: threading.Thread | None = None
        self.running = False

    def start(self):
        """Start batch worker."""
        if self.running:
            return

        self.running = True
        self.worker_thread = threading.Thread(target=self._worker, daemon=True)
        self.worker_thread.start()

    def stop(self):
        """Stop batch worker."""
        self.running = False
        if self.worker_thread:
            self.worker_thread.join(timeout=5.0)

    def add(self, item: T, timeout: float = 5.0) -> R:
        """Add item to batch queue.

        Args:
            item: Item to process
            timeout: Wait timeout

        Returns:
            Processing result

        Raises:
            TimeoutError: If result not available in time
        """
        if not self.running:
            self.start()

        item_id = id(item)
        result_event = threading.Event()

        self.queue.put((item_id, item, result_event))

        # Wait for result
        if not result_event.wait(timeout=timeout):
            raise TimeoutError(f"Batch processing timeout after {timeout}s")

        with self.lock:
            result = self.results.pop(item_id, None)

        if result is None:
            raise RuntimeError("Batch processing failed")

        if isinstance(result, Exception):
            raise result

        return result

    def _worker(self):
        """Worker thread for batch processing."""
        while self.running:
            batch = self._collect_batch()

            if not batch:
                time.sleep(0.01)  # Short sleep to avoid busy waiting
                continue

            self._process_batch(batch)

    def _collect_batch(self) -> list[tuple]:
        """Collect items for batch.

        Returns:
            List of (item_id, item, result_event) tuples
        """
        batch = []
        deadline = time.time() + self.config.max_wait_time

        while len(batch) < self.config.max_batch_size and time.time() < deadline:
            try:
                item = self.queue.get(timeout=0.01)
                batch.append(item)
            except Empty:
                if batch:
                    break  # Process what we have
                continue

        return batch

    def _process_batch(self, batch: list[tuple]):
        """Process batch of items.

        Args:
            batch: List of (item_id, item, result_event) tuples
        """
        item_ids = [item_id for item_id, _, _ in batch]
        items = [item for _, item, _ in batch]
        events = [event for _, _, event in batch]

        try:
            # Process batch
            results = self.processor_func(items)

            # Store results
            with self.lock:
                for item_id, result in zip(item_ids, results, strict=False):
                    self.results[item_id] = result

        except Exception as e:
            # Store error for all items
            with self.lock:
                for item_id in item_ids:
                    self.results[item_id] = e

        finally:
            # Signal completion
            for event in events:
                event.set()


class AsyncBatchProcessor:
    """Async batch processor."""

    def __init__(
        self,
        processor_func: Callable[[list[T]], asyncio.Future[list[R]]],
        config: BatchConfig | None = None
    ):
        """Initialize async batch processor.

        Args:
            processor_func: Async function to process batch
            config: Batch configuration
        """
        self.processor_func = processor_func
        self.config = config or BatchConfig()

        self.queue: asyncio.Queue = asyncio.Queue()
        self.results: dict = {}
        self.lock = asyncio.Lock()
        self.worker_task: asyncio.Task | None = None
        self.running = False

    async def start(self):
        """Start batch worker."""
        if self.running:
            return

        self.running = True
        self.worker_task = asyncio.create_task(self._worker())

    async def stop(self):
        """Stop batch worker."""
        self.running = False
        if self.worker_task:
            await self.worker_task

    async def add(self, item: T, timeout: float = 5.0) -> R:
        """Add item to batch queue.

        Args:
            item: Item to process
            timeout: Wait timeout

        Returns:
            Processing result
        """
        if not self.running:
            await self.start()

        item_id = id(item)
        result_future = asyncio.Future()

        await self.queue.put((item_id, item, result_future))

        # Wait for result
        try:
            result = await asyncio.wait_for(result_future, timeout=timeout)
        except asyncio.TimeoutError:
            raise TimeoutError(f"Batch processing timeout after {timeout}s")

        if isinstance(result, Exception):
            raise result

        return result

    async def _worker(self):
        """Worker for batch processing."""
        while self.running:
            batch = await self._collect_batch()

            if not batch:
                await asyncio.sleep(0.01)
                continue

            await self._process_batch(batch)

    async def _collect_batch(self) -> list[tuple]:
        """Collect items for batch.

        Returns:
            List of (item_id, item, result_future) tuples
        """
        batch = []
        deadline = time.time() + self.config.max_wait_time

        while len(batch) < self.config.max_batch_size and time.time() < deadline:
            try:
                item = await asyncio.wait_for(
                    self.queue.get(),
                    timeout=0.01
                )
                batch.append(item)
            except asyncio.TimeoutError:
                if batch:
                    break
                continue

        return batch

    async def _process_batch(self, batch: list[tuple]):
        """Process batch of items.

        Args:
            batch: List of (item_id, item, result_future) tuples
        """
        [item_id for item_id, _, _ in batch]
        items = [item for _, item, _ in batch]
        futures = [future for _, _, future in batch]

        try:
            # Process batch
            results = await self.processor_func(items)

            # Set results
            for future, result in zip(futures, results, strict=False):
                if not future.done():
                    future.set_result(result)

        except Exception as e:
            # Set error for all items
            for future in futures:
                if not future.done():
                    future.set_exception(e)


def batch_calls(batch_size: int = 100):
    """Decorator to batch function calls.

    Example:
        @batch_calls(batch_size=50)
        def process_items(items):
            return db.bulk_insert(items)

        # Calls are automatically batched
        for item in items:
            result = process_items(item)
    """
    def decorator(func: Callable) -> Callable:
        processor = BatchProcessor(func, BatchConfig(max_batch_size=batch_size))
        processor.start()

        def wrapper(item):
            return processor.add(item)

        wrapper._batch_processor = processor  # Store reference
        return wrapper

    return decorator
