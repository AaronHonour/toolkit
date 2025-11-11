"""
Middleware Module.

Provides request/response middleware pipeline with:
- Middleware chain execution
- Request/response context
- Built-in middleware (logging, metrics, auth, etc.)
"""

from .pipeline import MiddlewarePipeline, Middleware, Request, Response, NextHandler
from .builtin import (
    LoggingMiddleware,
    MetricsMiddleware,
    ErrorHandlerMiddleware,
    CORSMiddleware,
)

__all__ = [
    "MiddlewarePipeline",
    "Middleware",
    "Request",
    "Response",
    "NextHandler",
    "LoggingMiddleware",
    "MetricsMiddleware",
    "ErrorHandlerMiddleware",
    "CORSMiddleware",
]
