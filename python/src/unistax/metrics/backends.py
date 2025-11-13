"""Metrics backends for different storage/reporting systems.

Provides backends for Prometheus, StatsD, and in-memory storage.
"""

import threading
from abc import ABC, abstractmethod
from collections import defaultdict
from typing import Any


class MetricsBackend(ABC):
    """Abstract base class for metrics backends."""

    @abstractmethod
    def increment(
        self, name: str, value: float = 1.0, labels: dict[str, str] | None = None
    ) -> None:
        """Increment counter metric."""
        pass

    @abstractmethod
    def gauge(self, name: str, value: float, labels: dict[str, str] | None = None) -> None:
        """Set gauge metric."""
        pass

    @abstractmethod
    def histogram(self, name: str, value: float, labels: dict[str, str] | None = None) -> None:
        """Record histogram value."""
        pass

    @abstractmethod
    def get_metrics(self) -> dict[str, Any]:
        """Get all metrics."""
        pass

    @abstractmethod
    def reset(self) -> None:
        """Reset all metrics."""
        pass


class InMemoryBackend(MetricsBackend):
    """In-memory metrics backend for testing and development.

    Stores all metrics in memory with thread-safe operations.
    """

    def __init__(self) -> None:
        """Initialize in-memory backend."""
        self._lock = threading.RLock()
        self._counters: dict[str, float] = defaultdict(float)
        self._gauges: dict[str, float] = {}
        self._histograms: dict[str, list[float]] = defaultdict(list[Any])

    def _make_key(self, name: str, labels: dict[str, str] | None) -> str:
        """Create metric key from name and labels."""
        if not labels:
            return name

        label_str = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
        return f"{name}{{{label_str}}}"

    def increment(
        self, name: str, value: float = 1.0, labels: dict[str, str] | None = None
    ) -> None:
        """Increment counter."""
        key = self._make_key(name, labels)
        with self._lock:
            self._counters[key] += value

    def gauge(self, name: str, value: float, labels: dict[str, str] | None = None) -> None:
        """Set gauge value."""
        key = self._make_key(name, labels)
        with self._lock:
            self._gauges[key] = value

    def histogram(self, name: str, value: float, labels: dict[str, str] | None = None) -> None:
        """Record histogram value."""
        key = self._make_key(name, labels)
        with self._lock:
            self._histograms[key].append(value)

    def get_metrics(self) -> dict[str, Any]:
        """Get all metrics."""
        with self._lock:
            return {
                "counters": dict(self._counters),
                "gauges": dict(self._gauges),
                "histograms": {
                    k: {
                        "count": len(v),
                        "sum": sum(v),
                        "min": min(v) if v else 0,
                        "max": max(v) if v else 0,
                        "mean": sum(v) / len(v) if v else 0,
                    }
                    for k, v in self._histograms.items()
                },
            }

    def reset(self) -> None:
        """Reset all metrics."""
        with self._lock:
            self._counters.clear()
            self._gauges.clear()
            self._histograms.clear()


class PrometheusBackend(MetricsBackend):
    """Prometheus metrics backend.

    Uses prometheus_client library if available, falls back to in-memory.
    """

    def __init__(self, port: int = 9090, registry: Any | None = None) -> None:
        """Initialize Prometheus backend.

        Args:
            port: HTTP server port for metrics endpoint
            registry: Prometheus registry (uses default if None)
        """
        self._port = port
        self._fallback = InMemoryBackend()

        try:
            from prometheus_client import CollectorRegistry  # type: ignore[import-not-found]

            self._registry = registry or CollectorRegistry()
            self._metrics: dict[str, Any] = {}
            self._prometheus_available = True
        except ImportError:
            self._prometheus_available = False

    def _get_or_create_metric(
        self, name: str, metric_type: str, labels: dict[str, str] | None
    ) -> Any:
        """Get or create Prometheus metric."""
        if not self._prometheus_available:
            return None

        import prometheus_client

        label_names = list(labels.keys()) if labels else []
        key = f"{metric_type}:{name}:{','.join(sorted(label_names))}"

        if key not in self._metrics:
            if metric_type == "counter":
                metric_class = prometheus_client.Counter
            elif metric_type == "gauge":
                metric_class = prometheus_client.Gauge
            else:  # histogram
                metric_class = prometheus_client.Histogram

            self._metrics[key] = metric_class(
                name.replace(".", "_"),
                f"{name} metric",
                labelnames=label_names,
                registry=self._registry,
            )

        return self._metrics[key]

    def increment(
        self, name: str, value: float = 1.0, labels: dict[str, str] | None = None
    ) -> None:
        """Increment counter."""
        if not self._prometheus_available:
            self._fallback.increment(name, value, labels)
            return

        metric = self._get_or_create_metric(name, "counter", labels)
        if labels:
            metric.labels(**labels).inc(value)
        else:
            metric.inc(value)

    def gauge(self, name: str, value: float, labels: dict[str, str] | None = None) -> None:
        """Set gauge value."""
        if not self._prometheus_available:
            self._fallback.gauge(name, value, labels)
            return

        metric = self._get_or_create_metric(name, "gauge", labels)
        if labels:
            metric.labels(**labels).set(value)
        else:
            metric.set(value)

    def histogram(self, name: str, value: float, labels: dict[str, str] | None = None) -> None:
        """Record histogram value."""
        if not self._prometheus_available:
            self._fallback.histogram(name, value, labels)
            return

        metric = self._get_or_create_metric(name, "histogram", labels)
        if labels:
            metric.labels(**labels).observe(value)
        else:
            metric.observe(value)

    def get_metrics(self) -> dict[str, Any]:
        """Get all metrics."""
        if not self._prometheus_available:
            return self._fallback.get_metrics()

        # Return Prometheus metrics in text format
        return prometheus_client.Summary(*args, **kwargs)  # type: ignore

        import prometheus_client; return prometheus_client.generate_latest(self._registry)

    def reset(self) -> None:
        """Reset all metrics."""
        if not self._prometheus_available:
            self._fallback.reset()
            return

        self._metrics.clear()


class StatsDBackend(MetricsBackend):
    """StatsD metrics backend.

    Sends metrics to StatsD server if available, falls back to in-memory.
    """

    def __init__(self, host: str = "localhost", port: int = 8125, prefix: str = "") -> None:
        """Initialize StatsD backend.

        Args:
            host: StatsD server host
            port: StatsD server port
            prefix: Metric prefix
        """
        self._host = host
        self._port = port
        self._prefix = prefix
        self._fallback = InMemoryBackend()

        try:
            import statsd  # type: ignore[import-not-found]

            self._client = statsd.StatsClient(host, port, prefix=prefix)
            self._statsd_available = True
        except ImportError:
            self._statsd_available = False

    def _format_name(self, name: str, labels: dict[str, str] | None) -> str:
        """Format metric name with labels."""
        if not labels:
            return name

        # StatsD doesn't natively support labels, append to name
        label_str = ".".join(f"{k}.{v}" for k, v in sorted(labels.items()))
        return f"{name}.{label_str}"

    def increment(
        self, name: str, value: float = 1.0, labels: dict[str, str] | None = None
    ) -> None:
        """Increment counter."""
        if not self._statsd_available:
            self._fallback.increment(name, value, labels)
            return

        formatted_name = self._format_name(name, labels)
        self._client.incr(formatted_name, int(value))

    def gauge(self, name: str, value: float, labels: dict[str, str] | None = None) -> None:
        """Set gauge value."""
        if not self._statsd_available:
            self._fallback.gauge(name, value, labels)
            return

        formatted_name = self._format_name(name, labels)
        self._client.gauge(formatted_name, value)

    def histogram(self, name: str, value: float, labels: dict[str, str] | None = None) -> None:
        """Record histogram value."""
        if not self._statsd_available:
            self._fallback.histogram(name, value, labels)
            return

        formatted_name = self._format_name(name, labels)
        self._client.timing(formatted_name, value * 1000)  # Convert to ms

    def get_metrics(self) -> dict[str, Any]:
        """Get all metrics (from fallback)."""
        return self._fallback.get_metrics()

    def reset(self) -> None:
        """Reset metrics (fallback only)."""
        self._fallback.reset()
