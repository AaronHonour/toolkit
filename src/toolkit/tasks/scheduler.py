"""Task scheduling using APScheduler."""

from typing import Any, Callable, Dict, Optional
from datetime import datetime
from dataclasses import dataclass
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.job import Job as APJob


@dataclass
class Job:
    """Job configuration."""

    id: str
    func: Callable
    trigger: str  # "cron", "interval", "date"
    trigger_args: Dict[str, Any]
    args: tuple = ()
    kwargs: Optional[Dict[str, Any]] = None
    name: Optional[str] = None
    misfire_grace_time: int = 60
    coalesce: bool = True
    max_instances: int = 1


class Scheduler:
    """Task scheduler using APScheduler."""

    def __init__(
        self,
        timezone: str = "UTC",
        job_defaults: Optional[Dict[str, Any]] = None,
        use_async: bool = False,
    ):
        """Initialize scheduler.

        Args:
            timezone: Timezone for scheduling
            job_defaults: Default job settings
            use_async: Use async scheduler
        """
        self.timezone = timezone
        self.use_async = use_async

        defaults = job_defaults or {
            "coalesce": True,
            "max_instances": 1,
            "misfire_grace_time": 60,
        }

        if use_async:
            self.scheduler = AsyncIOScheduler(
                timezone=timezone, job_defaults=defaults
            )
        else:
            self.scheduler = BackgroundScheduler(
                timezone=timezone, job_defaults=defaults
            )

        self._jobs: Dict[str, Job] = {}

    def start(self):
        """Start the scheduler."""
        if not self.scheduler.running:
            self.scheduler.start()

    def shutdown(self, wait: bool = True):
        """Shutdown the scheduler.

        Args:
            wait: Wait for running jobs to complete
        """
        if self.scheduler.running:
            self.scheduler.shutdown(wait=wait)

    def add_job(
        self,
        func: Callable,
        trigger: str,
        id: Optional[str] = None,
        name: Optional[str] = None,
        args: tuple = (),
        kwargs: Optional[Dict[str, Any]] = None,
        **trigger_args,
    ) -> str:
        """Add a job to the scheduler.

        Args:
            func: Function to execute
            trigger: Trigger type ("cron", "interval", "date")
            id: Job ID
            name: Job name
            args: Function arguments
            kwargs: Function keyword arguments
            **trigger_args: Trigger-specific arguments

        Returns:
            Job ID

        Example:
            # Interval trigger
            scheduler.add_job(
                my_func,
                "interval",
                minutes=30
            )

            # Cron trigger
            scheduler.add_job(
                my_func,
                "cron",
                hour=0,
                minute=0
            )
        """
        job_id = id or f"{func.__name__}_{datetime.now().timestamp()}"

        # Create trigger
        if trigger == "cron":
            trigger_obj = CronTrigger(**trigger_args, timezone=self.timezone)
        elif trigger == "interval":
            trigger_obj = IntervalTrigger(**trigger_args, timezone=self.timezone)
        elif trigger == "date":
            trigger_obj = DateTrigger(**trigger_args, timezone=self.timezone)
        else:
            raise ValueError(f"Unknown trigger type: {trigger}")

        # Add job
        self.scheduler.add_job(
            func,
            trigger_obj,
            id=job_id,
            name=name or func.__name__,
            args=args,
            kwargs=kwargs or {},
        )

        # Store job config
        self._jobs[job_id] = Job(
            id=job_id,
            func=func,
            trigger=trigger,
            trigger_args=trigger_args,
            args=args,
            kwargs=kwargs,
            name=name,
        )

        return job_id

    def add_cron_job(
        self,
        func: Callable,
        hour: str = "0",
        minute: str = "0",
        second: str = "0",
        day: str = "*",
        month: str = "*",
        day_of_week: str = "*",
        **kwargs,
    ) -> str:
        """Add a cron-style job.

        Args:
            func: Function to execute
            hour: Hour (0-23)
            minute: Minute (0-59)
            second: Second (0-59)
            day: Day of month (1-31)
            month: Month (1-12)
            day_of_week: Day of week (0-6, Mon-Sun)
            **kwargs: Additional job arguments

        Returns:
            Job ID

        Example:
            # Run every day at midnight
            scheduler.add_cron_job(cleanup, hour="0", minute="0")
        """
        return self.add_job(
            func,
            "cron",
            hour=hour,
            minute=minute,
            second=second,
            day=day,
            month=month,
            day_of_week=day_of_week,
            **kwargs,
        )

    def add_interval_job(
        self,
        func: Callable,
        weeks: int = 0,
        days: int = 0,
        hours: int = 0,
        minutes: int = 0,
        seconds: int = 0,
        **kwargs,
    ) -> str:
        """Add an interval-based job.

        Args:
            func: Function to execute
            weeks: Number of weeks
            days: Number of days
            hours: Number of hours
            minutes: Number of minutes
            seconds: Number of seconds
            **kwargs: Additional job arguments

        Returns:
            Job ID

        Example:
            # Run every 30 minutes
            scheduler.add_interval_job(sync_data, minutes=30)
        """
        return self.add_job(
            func,
            "interval",
            weeks=weeks,
            days=days,
            hours=hours,
            minutes=minutes,
            seconds=seconds,
            **kwargs,
        )

    def add_date_job(
        self,
        func: Callable,
        run_date: datetime,
        **kwargs,
    ) -> str:
        """Add a one-time job at specific date/time.

        Args:
            func: Function to execute
            run_date: When to run the job
            **kwargs: Additional job arguments

        Returns:
            Job ID

        Example:
            # Run once at specific time
            scheduler.add_date_job(send_reminder, run_date=datetime(2025, 1, 1))
        """
        return self.add_job(func, "date", run_date=run_date, **kwargs)

    def remove_job(self, job_id: str):
        """Remove a job.

        Args:
            job_id: Job ID to remove
        """
        self.scheduler.remove_job(job_id)
        if job_id in self._jobs:
            del self._jobs[job_id]

    def pause_job(self, job_id: str):
        """Pause a job.

        Args:
            job_id: Job ID to pause
        """
        self.scheduler.pause_job(job_id)

    def resume_job(self, job_id: str):
        """Resume a paused job.

        Args:
            job_id: Job ID to resume
        """
        self.scheduler.resume_job(job_id)

    def get_job(self, job_id: str) -> Optional[APJob]:
        """Get job by ID.

        Args:
            job_id: Job ID

        Returns:
            Job or None
        """
        return self.scheduler.get_job(job_id)

    def get_jobs(self) -> list[APJob]:
        """Get all jobs.

        Returns:
            List of jobs
        """
        return self.scheduler.get_jobs()

    def reschedule_job(
        self,
        job_id: str,
        trigger: str,
        **trigger_args,
    ):
        """Reschedule a job.

        Args:
            job_id: Job ID
            trigger: New trigger type
            **trigger_args: New trigger arguments
        """
        # Create new trigger
        if trigger == "cron":
            trigger_obj = CronTrigger(**trigger_args, timezone=self.timezone)
        elif trigger == "interval":
            trigger_obj = IntervalTrigger(**trigger_args, timezone=self.timezone)
        elif trigger == "date":
            trigger_obj = DateTrigger(**trigger_args, timezone=self.timezone)
        else:
            raise ValueError(f"Unknown trigger type: {trigger}")

        self.scheduler.reschedule_job(job_id, trigger=trigger_obj)

        # Update stored config
        if job_id in self._jobs:
            self._jobs[job_id].trigger = trigger
            self._jobs[job_id].trigger_args = trigger_args
