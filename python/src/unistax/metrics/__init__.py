"""
Metrics Module.

Provides application metrics collection and reporting with:
- Multiple backends (Prometheus, StatsD, in-memory)
- Counter, gauge, histogram, timer metrics
- Decorator-based instrumentation
- Automatic integration with other modules
"""

from .backends import InMemoryBackend, PrometheusBackend, StatsDBackend
from .decorators import counter, gauge, timer
from .manager import Metrics, MetricsManager

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
