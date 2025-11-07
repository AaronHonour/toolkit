"""Audit decorators."""

from typing import Callable
from functools import wraps
from toolkit.audit.logger import AuditLogger, AuditAction

_audit_logger: AuditLogger = None


def set_audit_logger(logger: AuditLogger):
    """Set global audit logger."""
    global _audit_logger
    _audit_logger = logger


def audit(action: AuditAction, resource: str):
    """Decorator to audit function calls."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                if _audit_logger:
                    _audit_logger.log(action=action, resource=resource, success=True)
                return result
            except Exception as e:
                if _audit_logger:
                    _audit_logger.log(action=action, resource=resource, success=False, error=str(e))
                raise

        return wrapper

    return decorator
