"""Task monitoring and status tracking."""

from enum import Enum
from typing import Any

from celery import Celery  # type: ignore[import-not-found]
from celery.result import AsyncResult  # type: ignore[import-not-found]


class TaskStatus(str, Enum):
    """Task status enumeration."""

    PENDING = "PENDING"
    STARTED = "STARTED"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    RETRY = "RETRY"
    REVOKED = "REVOKED"


class TaskMonitor:
    """Monitor task execution and status."""

    def __init__(self, app: Celery) -> None:
        """Initialize task monitor.

        Args:
            app: Celery application
        """
        self.app = app

    def get_task_status(self, task_id: str) -> TaskStatus:
        """Get task status.

        Args:
            task_id: Task ID

        Returns:
            Task status
        """
        result = AsyncResult(task_id, app=self.app)
        return TaskStatus(result.status)

    def get_task_result(self, task_id: str) -> Any:
        """Get task result.

        Args:
            task_id: Task ID

        Returns:
            Task result

        Raises:
            Exception: If task failed
        """
        result = AsyncResult(task_id, app=self.app)
        return result.get()

    def get_task_info(self, task_id: str) -> dict[str, Any]:
        """Get complete task information.

        Args:
            task_id: Task ID

        Returns:
            Task information dictionary
        """
        result = AsyncResult(task_id, app=self.app)

        info = {
            "task_id": task_id,
            "status": result.status,
            "ready": result.ready(),
            "successful": result.successful() if result.ready() else None,
            "failed": result.failed() if result.ready() else None,
        }

        if result.ready():
            if result.successful():
                info["result"] = result.result
            elif result.failed():
                info["error"] = str(result.info)
                info["traceback"] = result.traceback

        return info

    def is_task_complete(self, task_id: str) -> bool:
        """Check if task is complete.

        Args:
            task_id: Task ID

        Returns:
            True if complete
        """
        result = AsyncResult(task_id, app=self.app)
        return bool(result.ready())

    def is_task_successful(self, task_id: str) -> bool:
        """Check if task completed successfully.

        Args:
            task_id: Task ID

        Returns:
            True if successful
        """
        result = AsyncResult(task_id, app=self.app)
        return bool(result.successful())

    def wait_for_task(
        self,
        task_id: str,
        timeout: float | None = None,
        interval: float = 0.5,
    ) -> Any:
        """Wait for task to complete.

        Args:
            task_id: Task ID
            timeout: Maximum wait time (seconds)
            interval: Check interval (seconds)

        Returns:
            Task result

        Raises:
            TimeoutError: If timeout exceeded
            Exception: If task failed
        """
        result = AsyncResult(task_id, app=self.app)
        return result.get(timeout=timeout, interval=interval)

    def revoke_task(
        self,
        task_id: str,
        terminate: bool = False,
        signal: str = "SIGTERM",
    ) -> None:
        """Revoke a task.

        Args:
            task_id: Task ID
            terminate: Terminate if running
            signal: Signal to send if terminating
        """
        result = AsyncResult(task_id, app=self.app)
        result.revoke(terminate=terminate, signal=signal)

    def get_active_tasks(self) -> dict[str, list[Any]]:
        """Get active tasks on all workers.

        Returns:
            Dictionary of worker -> active tasks
        """
        inspector = self.app.control.inspect()
        return inspector.active() or {}

    def get_scheduled_tasks(self) -> dict[str, list[Any]]:
        """Get scheduled tasks on all workers.

        Returns:
            Dictionary of worker -> scheduled tasks
        """
        inspector = self.app.control.inspect()
        return inspector.scheduled() or {}

    def get_reserved_tasks(self) -> dict[str, list[Any]]:
        """Get reserved tasks on all workers.

        Returns:
            Dictionary of worker -> reserved tasks
        """
        inspector = self.app.control.inspect()
        return inspector.reserved() or {}

    def get_worker_stats(self) -> dict[str, dict[str, Any]]:
        """Get worker statistics.

        Returns:
            Dictionary of worker -> stats
        """
        inspector = self.app.control.inspect()
        return inspector.stats() or {}

    def get_registered_tasks(self) -> dict[str, list[str]]:
        """Get registered tasks on all workers.

        Returns:
            Dictionary of worker -> task names
        """
        inspector = self.app.control.inspect()
        return inspector.registered() or {}

    def ping_workers(self) -> dict[str, dict[str, str]]:
        """Ping all workers.

        Returns:
            Dictionary of worker -> pong response
        """
        inspector = self.app.control.inspect()
        return inspector.ping() or {}
