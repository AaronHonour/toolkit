"""
Logging context management.

Provides thread-local context for logging.
"""

from contextvars import ContextVar
from typing import Any, Dict

# Context for request/correlation IDs
log_context: ContextVar[Dict[str, Any]] = ContextVar("log_context", default={})
