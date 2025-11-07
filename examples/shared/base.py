"""Base classes for all example applications.

Provides common patterns and interfaces used across examples.
"""

from abc import ABC, abstractmethod
from typing import Any, Generic, List, Optional, TypeVar
from dataclasses import dataclass
from datetime import datetime

from toolkit.logging import LoggerManager
from toolkit.metrics import MetricsManager
from toolkit.di import Container


T = TypeVar("T")
ID = TypeVar("ID")


class BaseApplication(ABC):
    """Base application class for all examples.

    Provides common setup for logging, metrics, and dependency injection.
    """

    def __init__(self):
        """Initialize base application."""
        self.logger = LoggerManager().get_logger(self.__class__.__name__)
        self.metrics = MetricsManager()
        self.container = Container()
        self._setup_dependencies()

    @abstractmethod
    def _setup_dependencies(self):
        """Setup dependency injection container.

        Override this to register your application dependencies.
        """
        pass

    @abstractmethod
    async def startup(self):
        """Application startup logic.

        Called when the application starts.
        """
        pass

    @abstractmethod
    async def shutdown(self):
        """Application shutdown logic.

        Called when the application stops.
        """
        pass


class BaseService(ABC):
    """Base service class for application services.

    Services contain business logic and orchestrate operations.
    """

    def __init__(self):
        """Initialize base service."""
        self.logger = LoggerManager().get_logger(self.__class__.__name__)
        self.metrics = MetricsManager()

    def _record_operation(self, operation: str, duration: float):
        """Record operation metrics.

        Args:
            operation: Operation name
            duration: Operation duration in seconds
        """
        self.metrics.timing(f"{self.__class__.__name__}.{operation}", duration)
        self.logger.debug(f"{operation} completed in {duration*1000:.2f}ms")


class BaseRepository(ABC, Generic[T, ID]):
    """Base repository interface for data access.

    Repositories handle data persistence and retrieval.
    Follows Repository pattern for clean separation.
    """

    def __init__(self):
        """Initialize base repository."""
        self.logger = LoggerManager().get_logger(self.__class__.__name__)

    @abstractmethod
    async def get_by_id(self, id: ID) -> Optional[T]:
        """Get entity by ID.

        Args:
            id: Entity identifier

        Returns:
            Entity or None if not found
        """
        pass

    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """Get all entities with pagination.

        Args:
            skip: Number of entities to skip
            limit: Maximum number of entities to return

        Returns:
            List of entities
        """
        pass

    @abstractmethod
    async def create(self, entity: T) -> T:
        """Create new entity.

        Args:
            entity: Entity to create

        Returns:
            Created entity with ID
        """
        pass

    @abstractmethod
    async def update(self, id: ID, entity: T) -> Optional[T]:
        """Update existing entity.

        Args:
            id: Entity identifier
            entity: Updated entity data

        Returns:
            Updated entity or None if not found
        """
        pass

    @abstractmethod
    async def delete(self, id: ID) -> bool:
        """Delete entity.

        Args:
            id: Entity identifier

        Returns:
            True if deleted, False if not found
        """
        pass

    @abstractmethod
    async def exists(self, id: ID) -> bool:
        """Check if entity exists.

        Args:
            id: Entity identifier

        Returns:
            True if exists, False otherwise
        """
        pass


@dataclass
class PagedResult(Generic[T]):
    """Paginated result container.

    Standard pagination response format across all examples.
    """

    items: List[T]
    total: int
    page: int
    page_size: int

    @property
    def total_pages(self) -> int:
        """Calculate total number of pages."""
        return (self.total + self.page_size - 1) // self.page_size

    @property
    def has_next(self) -> bool:
        """Check if there's a next page."""
        return self.page < self.total_pages

    @property
    def has_prev(self) -> bool:
        """Check if there's a previous page."""
        return self.page > 1


@dataclass
class AuditInfo:
    """Audit information for entities.

    Tracks creation and modification metadata.
    """

    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
    updated_by: Optional[str] = None

    @classmethod
    def create(cls, user: Optional[str] = None) -> "AuditInfo":
        """Create audit info for new entity.

        Args:
            user: User creating the entity

        Returns:
            New audit info
        """
        now = datetime.utcnow()
        return cls(
            created_at=now,
            updated_at=now,
            created_by=user,
            updated_by=user
        )

    def update(self, user: Optional[str] = None) -> "AuditInfo":
        """Update audit info for modified entity.

        Args:
            user: User updating the entity

        Returns:
            Updated audit info
        """
        self.updated_at = datetime.utcnow()
        self.updated_by = user
        return self
