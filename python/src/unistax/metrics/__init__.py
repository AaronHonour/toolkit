"""
Metrics Module.

Provides application metrics collection and reporting with:
- Multiple backends (Prometheus, StatsD, in-memory)
- Counter, gauge, histogram, timer metrics
- Decorator-based instrumentation
- Automatic integration with other modules
"""

from .manager import MetricsManager, Metrics
from .backends import PrometheusBackend, StatsDBackend, InMemoryBackend
from .decorators import timer, counter, gauge

__all__ = [
    "MetricsManager",
    "Metrics",
    "PrometheusBackend",
    "StatsDBackend",
    "InMemoryBackend",
    "timer",
    "counter",
    "gauge",
]
