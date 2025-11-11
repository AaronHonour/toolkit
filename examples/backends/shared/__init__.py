"""Shared utilities for all example applications.

Provides common base classes, configuration, and monitoring utilities.
"""

from examples.shared.base import BaseApplication, BaseService, BaseRepository
from examples.shared.config import ExampleConfig, load_config
from examples.shared.monitoring import PerformanceMonitor, setup_monitoring

__all__ = [
    "BaseApplication",
    "BaseService",
    "BaseRepository",
    "ExampleConfig",
    "load_config",
    "PerformanceMonitor",
    "setup_monitoring",
]
