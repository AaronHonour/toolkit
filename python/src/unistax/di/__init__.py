"""Dependency Injection Module.

Provides a comprehensive DI container with:
- Auto-wiring based on type hints
- Lifetime management (singleton, transient, scoped)
- Factory registration
- Circular dependency detection
- Configuration binding
"""

from .container import Container, Lifetime, inject, injectable
from .decorators import scoped, singleton, transient
from .exceptions import CircularDependencyError, DependencyResolutionError

__all__ = [
    "Container",
    "injectable",
    "inject",
    "Lifetime",
    "singleton",
    "transient",
    "scoped",
    "DependencyResolutionError",
    "CircularDependencyError",
]
