"""
HTTP Client Module.

Provides enterprise HTTP client with:
- Automatic retries with exponential backoff
- Circuit breaker pattern
- Request/response logging
- Timeout management
- Connection pooling
"""

from .client import HTTPClient, Request, Response
from .retry import RetryStrategy, ExponentialBackoff
from .circuit_breaker import CircuitBreaker, CircuitState

__all__ = [
    "HTTPClient",
    "Request",
    "Response",
    "RetryStrategy",
    "ExponentialBackoff",
    "CircuitBreaker",
    "CircuitState",
]
