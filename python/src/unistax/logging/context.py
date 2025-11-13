"""Logging context management.

Provides thread-local context for logging.
"""

from contextvars import ContextVar
from typing import Any

# Context for request/correlation IDs
log_context: ContextVar[dict[str, Any] | None] = ContextVar("log_context", default=None)
