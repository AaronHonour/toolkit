"""Audit storage backends."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

from unistax.audit.logger import AuditAction, AuditEntry


class AuditStorage(ABC):
    """Base audit storage interface."""

    @abstractmethod
    def save(self, entry: AuditEntry) -> None:
        """Save audit entry."""
        pass

    @abstractmethod
    def query(
        self,
        user_id: str | None = None,
        resource: str | None = None,
        action: AuditAction | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        limit: int = 100,
    ) -> list[AuditEntry]:
        """Query audit entries."""
        pass


class InMemoryAuditStorage(AuditStorage):
    """In-memory audit storage."""

    def __init__(self) -> None:
        """Initialize storage."""
        self.entries: list[AuditEntry] = []

    def save(self, entry: AuditEntry) -> None:
        """Save entry to memory."""
        self.entries.append(entry)

    def query(
        self,
        user_id: str | None = None,
        resource: str | None = None,
        action: AuditAction | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        limit: int = 100,
    ) -> list[AuditEntry]:
        """Query entries from memory."""
        results = self.entries

        if user_id:
            results = [e for e in results if e.user_id == user_id]
        if resource:
            results = [e for e in results if e.resource == resource]
        if action:
            results = [e for e in results if e.action == action]
        if start_date:
            results = [e for e in results if e.timestamp >= start_date]
        if end_date:
            results = [e for e in results if e.timestamp <= end_date]

        return results[:limit]


class DBAuditStorage(AuditStorage):
    """Database audit storage."""

    def __init__(self, session_factory: Any) -> None:
        """Initialize with database session factory."""
        self.session_factory = session_factory

    def save(self, entry: AuditEntry) -> None:
        """Save to database."""
        # Implementation depends on ORM model
        pass

    def query(
        self,
        user_id: str | None = None,
        resource: str | None = None,
        action: AuditAction | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        limit: int = 100,
    ) -> list[AuditEntry]:
        """Query from database."""
        # Implementation depends on ORM model
        return []
