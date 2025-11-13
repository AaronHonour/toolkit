"""Metrics manager implementation.

Provides unified interface for collecting and reporting metrics.
"""

import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from .backends import InMemoryBackend, MetricsBackend, PrometheusBackend, StatsDBackend


class MetricsManager:
    """Unified metrics manager supporting multiple backends.

    Examples:
        >>> metrics = MetricsManager(backend="prometheus")
        >>> metrics.counter("requests.total", labels={"endpoint": "/api/users"})
        >>> metrics.gauge("queue.size", 42)
        >>> with metrics.timer("db.query.duration"):
        ...     # Timed operation
        ...     pass
    """

    def __init__(
        self,
        backend: str | MetricsBackend = "memory",
        prefix: str = "",
        labels: dict[str, str] | None = None,
    ) -> None:
        """Initialize metrics manager.

        Args:
            backend: Backend type or instance ("prometheus", "statsd", "memory")
            prefix: Metric name prefix
            labels: Default labels for all metrics
        """
        if isinstance(backend, str):
            self._backend = self._create_backend(backend)
        else:
            self._backend = backend

        self._prefix = prefix
        self._default_labels = labels or {}

    @classmethod
    def from_yaml(cls, path: str | Path) -> "MetricsManager":
        """Create metrics manager from YAML configuration.

        Args:
            path: Path to YAML config

        Returns:
            Configured metrics manager
        """
        from ..config import ConfigManager

        config = ConfigManager.from_yaml(path)
        backend_type = config.get("metrics.backend", "memory")
        prefix = config.get("metrics.prefix", "")
        labels = config.get_dict("metrics.labels", {})

        # Backend-specific configuration
        backend_config = config.get_dict("metrics.backend_config", {})

        if backend_type == "prometheus":
            backend = PrometheusBackend(**backend_config)
        elif backend_type == "statsd":
            backend = StatsDBackend(**backend_config)
        else:
            backend = InMemoryBackend()

        return cls(backend=backend, prefix=prefix, labels=labels)

    def _create_backend(self, backend_type: str) -> MetricsBackend:
        """Create metrics backend by type."""
        if backend_type == "prometheus":
            return PrometheusBackend()
        elif backend_type == "statsd":
            return StatsDBackend()
        else:
            return InMemoryBackend()

    def _format_name(self, name: str) -> str:
        """Format metric name with prefix."""
        if self._prefix:
            return f"{self._prefix}.{name}"
        return name

    def _merge_labels(self, labels: dict[str, str] | None) -> dict[str, str]:
        """Merge labels with defaults."""
        merged = dict(self._default_labels)
        if labels:
            merged.update(labels)
        return merged

    def counter(self, name: str, value: float = 1.0, labels: dict[str, str] | None = None) -> None:
        """Increment counter metric.

        Args:
            name: Metric name
            value: Increment value
            labels: Metric labels
        """
        formatted_name = self._format_name(name)
        merged_labels = self._merge_labels(labels)
        self._backend.increment(formatted_name, value, merged_labels)

    def gauge(self, name: str, value: float, labels: dict[str, str] | None = None) -> None:
        """Set gauge metric.

        Args:
            name: Metric name
            value: Gauge value
            labels: Metric labels
        """
        formatted_name = self._format_name(name)
        merged_labels = self._merge_labels(labels)
        self._backend.gauge(formatted_name, value, merged_labels)

    def histogram(self, name: str, value: float, labels: dict[str, str] | None = None) -> None:
        """Record histogram value.

        Args:
            name: Metric name
            value: Observed value
            labels: Metric labels
        """
        formatted_name = self._format_name(name)
        merged_labels = self._merge_labels(labels)
        self._backend.histogram(formatted_name, value, merged_labels)

    @contextmanager
    def timer(self, name: str, labels: dict[str, str] | None = None):
        """Context manager for timing operations.

        Args:
            name: Metric name
            labels: Metric labels

        Examples:
            >>> with metrics.timer("api.request.duration"):
            ...     # Timed operation
            ...     process_request()
        """
        start_time = time.perf_counter()
        try:
            yield
        finally:
            duration = time.perf_counter() - start_time
            self.histogram(name, duration, labels)

    def time_function(self, name: str, labels: dict[str, str] | None = None):
        """Decorator for timing functions.

        Args:
            name: Metric name
            labels: Metric labels

        Examples:
            >>> @metrics.time_function("user.fetch.duration")
            ... def get_user(user_id):
            ...     return db.query(...)
        """
        from functools import wraps

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                with self.timer(name, labels):
                    return func(*args, **kwargs)

            return wrapper

        return decorator

    def get_metrics(self) -> dict[str, Any]:
        """Get all collected metrics.

        Returns:
            Dictionary of metrics
        """
        return self._backend.get_metrics()

    def reset(self) -> None:
        """Reset all metrics."""
        self._backend.reset()


# Global metrics instance
_global_metrics: MetricsManager | None = None


def get_metrics() -> MetricsManager:
    """Get global metrics instance."""
    global _global_metrics
    if _global_metrics is None:
        _global_metrics = MetricsManager()
    return _global_metrics


def set_metrics(metrics: MetricsManager) -> None:
    """Set global metrics instance."""
    global _global_metrics
    _global_metrics = metrics


# Convenience alias
Metrics = get_metrics
