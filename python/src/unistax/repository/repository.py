"""Repository pattern implementation."""

from abc import ABC, abstractmethod
from typing import Any, Generic, List, Optional, TypeVar

T = TypeVar("T")


class IRepository(ABC, Generic[T]):
    """Repository interface."""

    @abstractmethod
    async def get(self, id: Any) -> Optional[T]:
        """Get entity by ID."""
        pass

    @abstractmethod
    async def find(self, **kwargs) -> List[T]:
        """Find entities matching criteria."""
        pass

    @abstractmethod
    async def add(self, entity: T) -> T:
        """Add new entity."""
        pass

    @abstractmethod
    async def update(self, entity: T) -> T:
        """Update existing entity."""
        pass

    @abstractmethod
    async def delete(self, id: Any) -> bool:
        """Delete entity by ID."""
        pass


class Repository(IRepository[T]):
    """
    Base repository implementation.

    Provides common CRUD operations.

    Examples:
        >>> class UserRepository(Repository[User]):
        ...     async def find_by_email(self, email: str) -> Optional[User]:
        ...         return await self.find_one(email=email)
    """

    def __init__(self, session: Optional[Any] = None):
        self._session = session
        self._entities: Dict[Any, T] = {}  # In-memory store for example

    async def get(self, id: Any) -> Optional[T]:
        """Get entity by ID."""
        return self._entities.get(id)

    async def find(self, **kwargs) -> List[T]:
        """Find entities matching criteria."""
        results = []
        for entity in self._entities.values():
            match = True
            for key, value in kwargs.items():
                if not hasattr(entity, key) or getattr(entity, key) != value:
                    match = False
                    break
            if match:
                results.append(entity)
        return results

    async def find_one(self, **kwargs) -> Optional[T]:
        """Find single entity matching criteria."""
        results = await self.find(**kwargs)
        return results[0] if results else None

    async def add(self, entity: T) -> T:
        """Add new entity."""
        entity_id = getattr(entity, "id", None)
        if entity_id is None:
            # Generate ID if needed
            entity_id = len(self._entities) + 1
            setattr(entity, "id", entity_id)

        self._entities[entity_id] = entity
        return entity

    async def update(self, entity: T) -> T:
        """Update existing entity."""
        entity_id = getattr(entity, "id")
        self._entities[entity_id] = entity
        return entity

    async def delete(self, id: Any) -> bool:
        """Delete entity by ID."""
        if id in self._entities:
            del self._entities[id]
            return True
        return False

    async def count(self, **kwargs) -> int:
        """Count entities matching criteria."""
        results = await self.find(**kwargs)
        return len(results)
