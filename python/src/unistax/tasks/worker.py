"""Worker management for background tasks."""

from dataclasses import dataclass

from celery import Celery

# Global Celery app instance
_celery_app: Celery | None = None


@dataclass
class WorkerConfig:
    """Worker configuration."""

    concurrency: int = 4
    pool: str = "prefork"  # prefork, eventlet, gevent, solo
    max_tasks_per_child: int = 1000
    time_limit: int = 3600  # Hard time limit (seconds)
    soft_time_limit: int = 3000  # Soft time limit (seconds)
    task_acks_late: bool = True
    worker_prefetch_multiplier: int = 4
    worker_max_memory_per_child: int = 200000  # KB


class Worker:
    """Celery worker manager."""

    def __init__(self, app: Celery, config: WorkerConfig | None = None):
        """Initialize worker.

        Args:
            app: Celery application
            config: Worker configuration
        """
        self.app = app
        self.config = config or WorkerConfig()
        self._apply_config()

    def _apply_config(self):
        """Apply worker configuration to Celery app."""
        self.app.conf.update(
            worker_prefetch_multiplier=self.config.worker_prefetch_multiplier,
            worker_max_tasks_per_child=self.config.max_tasks_per_child,
            worker_max_memory_per_child=self.config.worker_max_memory_per_child,
            task_acks_late=self.config.task_acks_late,
            task_time_limit=self.config.time_limit,
            task_soft_time_limit=self.config.soft_time_limit,
        )

    def start(
        self,
        loglevel: str = "info",
        logfile: str | None = None,
        pidfile: str | None = None,
    ):
        """Start the worker.

        Args:
            loglevel: Log level (debug, info, warning, error, critical)
            logfile: Path to log file
            pidfile: Path to PID file

        Example:
            worker = Worker(celery_app)
            worker.start(loglevel="info")
        """
        argv = [
            "worker",
            f"--concurrency={self.config.concurrency}",
            f"--pool={self.config.pool}",
            f"--loglevel={loglevel}",
        ]

        if logfile:
            argv.append(f"--logfile={logfile}")

        if pidfile:
            argv.append(f"--pidfile={pidfile}")

        self.app.worker_main(argv)

    def inspect(self):
        """Get worker inspection interface.

        Returns:
            Celery inspect interface

        Example:
            inspector = worker.inspect()
            active_tasks = inspector.active()
        """
        return self.app.control.inspect()

    def purge(self):
        """Purge all waiting tasks.

        Returns:
            Number of tasks purged
        """
        return self.app.control.purge()

    def revoke(self, task_id: str, terminate: bool = False):
        """Revoke a task.

        Args:
            task_id: Task ID to revoke
            terminate: Terminate if already running
        """
        self.app.control.revoke(task_id, terminate=terminate)


def set_celery_app(app: Celery):
    """Set global Celery app.

    Args:
        app: Celery application
    """
    global _celery_app
    _celery_app = app


def get_celery_app() -> Celery:
    """Get global Celery app.

    Returns:
        Celery application

    Raises:
        RuntimeError: If app not set
    """
    if _celery_app is None:
        raise RuntimeError("Celery app not set. Call set_celery_app() first.")
    return _celery_app
