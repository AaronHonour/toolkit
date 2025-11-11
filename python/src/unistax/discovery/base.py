"""Base classes for service dependency discovery."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any, Set
from enum import Enum
from datetime import datetime


class DiscoverySource(str, Enum):
    """Source of dependency discovery."""

    API_CALL = "api_call"
    DATABASE = "database"
    MESSAGE_QUEUE = "message_queue"
    CACHE = "cache"
    CONFIGURATION = "configuration"
    CODE_ANALYSIS = "code_analysis"
    RUNTIME_TRACE = "runtime_trace"
    LOG_ANALYSIS = "log_analysis"


@dataclass
class DiscoveryResult:
    """Result of dependency discovery."""

    source_service: str
    target_service: str
    dependency_type: str
    source: DiscoverySource
    confidence: float = 1.0  # 0.0 to 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    discovered_at: datetime = field(default_factory=datetime.utcnow)

    def __hash__(self) -> int:
        """Make result hashable for deduplication."""
        return hash((self.source_service, self.target_service, self.dependency_type))


class DependencyDiscoverer(ABC):
    """Base class for dependency discoverers."""

    def __init__(self, service_name: str) -> None:
        """Initialize discoverer for a specific service.

        Args:
            service_name: Name of the service being analyzed
        """
        self.service_name = service_name
        self._discovered: Set[DiscoveryResult] = set()

    @abstractmethod
    async def discover(self) -> List[DiscoveryResult]:
        """Discover dependencies.

        Returns:
            List of discovered dependencies
        """
        pass

    def get_discovered_count(self) -> int:
        """Get the number of unique dependencies discovered."""
        return len(self._discovered)

    def clear_cache(self) -> None:
        """Clear the cache of discovered dependencies."""
        self._discovered.clear()
