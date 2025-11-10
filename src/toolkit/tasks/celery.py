"""Celery integration for distributed task processing."""

from typing import Any, Callable, Dict, Optional
from celery import Celery, Task
from celery.schedules import crontab
from toolkit.config import ConfigManager


class CeleryManager:
    """Manage Celery application for distributed tasks."""

    def __init__(
        self,
        broker_url: str,
        result_backend: Optional[str] = None,
        task_serializer: str = "json",
        result_serializer: str = "json",
        accept_content: Optional[list[str]] = None,
        timezone: str = "UTC",
        enable_utc: bool = True,
        **kwargs,
    ):
        """Initialize Celery manager.

        Args:
            broker_url: Message broker URL (e.g., redis://localhost:6379/0)
            result_backend: Result backend URL
            task_serializer: Task serialization format
            result_serializer: Result serialization format
            accept_content: Accepted content types
            timezone: Timezone for schedules
            enable_utc: Enable UTC timezone
            **kwargs: Additional Celery configuration
        """
        self.app = Celery("toolkit_tasks")

        # Configure Celery
        self.app.conf.update(
            broker_url=broker_url,
            result_backend=result_backend or broker_url,
            task_serializer=task_serializer,
            result_serializer=result_serializer,
            accept_content=accept_content or ["json"],
            timezone=timezone,
            enable_utc=enable_utc,
            **kwargs,
        )

        self._scheduled_tasks: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def from_yaml(cls, path: str, prefix: str = "tasks") -> "CeleryManager":
        """Create from YAML configuration.

        Args:
            path: Path to YAML file
            prefix: Configuration prefix

        Returns:
            CeleryManager instance
        """
        config_manager = ConfigManager.from_yaml(path)
        config = config_manager.get(prefix, default={})

        return cls(
            broker_url=config.get("broker_url", "redis://localhost:6379/0"),
            result_backend=config.get("result_backend"),
            task_serializer=config.get("task_serializer", "json"),
            result_serializer=config.get("result_serializer", "json"),
            accept_content=config.get("accept_content", ["json"]),
            timezone=config.get("timezone", "UTC"),
            enable_utc=config.get("enable_utc", True),
            **config.get("extra", {}),
        )

    def task(
        self,
        name: Optional[str] = None,
        bind: bool = False,
        max_retries: int = 3,
        default_retry_delay: int = 60,
        **options,
    ) -> Callable:
        """Decorator to create a Celery task.

        Args:
            name: Task name
            bind: Bind task instance as first argument
            max_retries: Maximum retry attempts
            default_retry_delay: Delay between retries (seconds)
            **options: Additional task options

        Returns:
            Task decorator

        Example:
            @celery_manager.task(name="send_email")
            def send_email(to: str, subject: str, body: str):
                # Send email logic
                pass
        """
        return self.app.task(
            name=name,
            bind=bind,
            max_retries=max_retries,
            default_retry_delay=default_retry_delay,
            **options,
        )

    def add_periodic_task(
        self,
        schedule: Any,
        task: str,
        args: tuple = (),
        kwargs: Optional[dict] = None,
        name: Optional[str] = None,
        **options,
    ):
        """Add a periodic task.

        Args:
            schedule: Schedule (crontab or interval)
            task: Task name
            args: Task arguments
            kwargs: Task keyword arguments
            name: Schedule entry name
            **options: Additional options
        """
        self.app.conf.beat_schedule = self.app.conf.beat_schedule or {}
        entry_name = name or f"{task}_schedule"

        self.app.conf.beat_schedule[entry_name] = {
            "task": task,
            "schedule": schedule,
            "args": args,
            "kwargs": kwargs or {},
            **options,
        }

        self._scheduled_tasks[entry_name] = {
            "task": task,
            "schedule": schedule,
            "args": args,
            "kwargs": kwargs or {},
        }

    def schedule_cron(
        self,
        task: str,
        minute: str = "*",
        hour: str = "*",
        day_of_week: str = "*",
        day_of_month: str = "*",
        month_of_year: str = "*",
        args: tuple = (),
        kwargs: Optional[dict] = None,
        name: Optional[str] = None,
    ):
        """Schedule task with cron expression.

        Args:
            task: Task name
            minute: Minute (0-59)
            hour: Hour (0-23)
            day_of_week: Day of week (0-6, Mon-Sun)
            day_of_month: Day of month (1-31)
            month_of_year: Month (1-12)
            args: Task arguments
            kwargs: Task keyword arguments
            name: Schedule entry name

        Example:
            # Run every day at midnight
            celery_manager.schedule_cron(
                "cleanup_task",
                hour="0",
                minute="0"
            )
        """
        schedule = crontab(
            minute=minute,
            hour=hour,
            day_of_week=day_of_week,
            day_of_month=day_of_month,
            month_of_year=month_of_year,
        )

        self.add_periodic_task(
            schedule=schedule,
            task=task,
            args=args,
            kwargs=kwargs,
            name=name,
        )

    def send_task(
        self,
        name: str,
        args: tuple = (),
        kwargs: Optional[dict] = None,
        countdown: Optional[int] = None,
        eta: Optional[Any] = None,
        **options,
    ) -> Any:
        """Send a task for execution.

        Args:
            name: Task name
            args: Task arguments
            kwargs: Task keyword arguments
            countdown: Delay before execution (seconds)
            eta: Specific execution time
            **options: Additional options

        Returns:
            AsyncResult
        """
        return self.app.send_task(
            name,
            args=args,
            kwargs=kwargs or {},
            countdown=countdown,
            eta=eta,
            **options,
        )

    def get_scheduled_tasks(self) -> Dict[str, Dict[str, Any]]:
        """Get all scheduled tasks.

        Returns:
            Dictionary of scheduled tasks
        """
        return self._scheduled_tasks.copy()


# Global task decorator (convenience)
def task(*args, **kwargs) -> Callable:
    """Global task decorator.

    Returns:
        Task decorator
    """
    # This requires a global celery_manager instance to be set
    from toolkit.tasks.worker import get_celery_app

    app = get_celery_app()
    return app.task(*args, **kwargs)
