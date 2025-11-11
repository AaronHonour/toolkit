"""Service discovery module for automatic dependency detection.

Provides tools to automatically discover service dependencies from:
- API calls and HTTP requests
- Database connections
- Message queue interactions
- Configuration files
- Code analysis
"""

from unistax.discovery.base import (
    DependencyDiscoverer,
    DiscoveryResult,
    DiscoverySource,
)
from unistax.discovery.api_discoverer import APICallDiscoverer
from unistax.discovery.database_discoverer import DatabaseConnectionDiscoverer
from unistax.discovery.queue_discoverer import MessageQueueDiscoverer
from unistax.discovery.config_discoverer import ConfigurationDiscoverer

__all__ = [
    # Base
    "DependencyDiscoverer",
    "DiscoveryResult",
    "DiscoverySource",
    # Discoverers
    "APICallDiscoverer",
    "DatabaseConnectionDiscoverer",
    "MessageQueueDiscoverer",
    "ConfigurationDiscoverer",
]
