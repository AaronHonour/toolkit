"""Resilience Module.

Provides resilience patterns: circuit breaker, bulkhead, fallback.
"""

from .circuit_breaker import CircuitBreaker, CircuitState
from .fallback import Fallback

__all__ = ["CircuitBreaker", "CircuitState", "Fallback"]
