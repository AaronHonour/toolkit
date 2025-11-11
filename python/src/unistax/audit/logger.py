"""Audit logging implementation."""

from enum import Enum
from typing import Any, Dict, Optional
from datetime import datetime
from dataclasses import dataclass, field
from unistax.audit.storage import AuditStorage


class AuditAction(str, Enum):
    """Audit action types."""

    CREATE = "CREATE"
    READ = "READ"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    ACCESS = "ACCESS"
    CHANGE = "CHANGE"


@dataclass
class AuditEntry:
    """Audit log entry."""

    action: AuditAction
    resource: str
    user_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    changes: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    success: bool = True
    error: Optional[str] = None


class AuditLogger:
    """Audit logger for tracking changes."""

    def __init__(self, storage: AuditStorage):
        """Initialize audit logger.

        Args:
            storage: Audit storage backend
        """
        self.storage = storage

    def log(
        self,
        action: AuditAction,
        resource: str,
        user_id: Optional[str] = None,
        changes: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        success: bool = True,
        error: Optional[str] = None,
    ) -> AuditEntry:
        """Log audit entry.

        Args:
            action: Audit action
            resource: Resource identifier
            user_id: User ID
            changes: Changes made
            metadata: Additional metadata
            ip_address: Client IP address
            user_agent: Client user agent
            success: Whether action succeeded
            error: Error message if failed

        Returns:
            Audit entry
        """
        entry = AuditEntry(
            action=action,
            resource=resource,
            user_id=user_id,
            changes=changes,
            metadata=metadata,
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
            error=error,
        )

        self.storage.save(entry)
        return entry

    def query(
        self,
        user_id: Optional[str] = None,
        resource: Optional[str] = None,
        action: Optional[AuditAction] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
    ) -> list[AuditEntry]:
        """Query audit logs.

        Args:
            user_id: Filter by user ID
            resource: Filter by resource
            action: Filter by action
            start_date: Filter by start date
            end_date: Filter by end date
            limit: Maximum entries to return

        Returns:
            List of audit entries
        """
        return self.storage.query(
            user_id=user_id,
            resource=resource,
            action=action,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
        )
