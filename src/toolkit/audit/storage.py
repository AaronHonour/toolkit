"""Audit storage backends."""

from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from toolkit.audit.logger import AuditEntry, AuditAction


class AuditStorage(ABC):
    """Base audit storage interface."""

    @abstractmethod
    def save(self, entry: AuditEntry):
        """Save audit entry."""
        pass

    @abstractmethod
    def query(
        self,
        user_id: Optional[str] = None,
        resource: Optional[str] = None,
        action: Optional[AuditAction] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[AuditEntry]:
        """Query audit entries."""
        pass


class InMemoryAuditStorage(AuditStorage):
    """In-memory audit storage."""

    def __init__(self):
        """Initialize storage."""
        self.entries: List[AuditEntry] = []

    def save(self, entry: AuditEntry):
        """Save entry to memory."""
        self.entries.append(entry)

    def query(
        self,
        user_id: Optional[str] = None,
        resource: Optional[str] = None,
        action: Optional[AuditAction] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[AuditEntry]:
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

    def __init__(self, session_factory):
        """Initialize with database session factory."""
        self.session_factory = session_factory

    def save(self, entry: AuditEntry):
        """Save to database."""
        # Implementation depends on ORM model
        pass

    def query(
        self,
        user_id: Optional[str] = None,
        resource: Optional[str] = None,
        action: Optional[AuditAction] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[AuditEntry]:
        """Query from database."""
        # Implementation depends on ORM model
        return []
