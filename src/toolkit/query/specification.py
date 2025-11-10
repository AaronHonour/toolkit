"""Specification pattern for queries."""

from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

T = TypeVar("T")


class Specification(ABC, Generic[T]):
    """Base specification interface."""

    @abstractmethod
    def is_satisfied_by(self, candidate: T) -> bool:
        """Check if candidate satisfies specification.

        Args:
            candidate: Object to check

        Returns:
            True if satisfied
        """
        pass

    def and_(self, other: "Specification[T]") -> "Specification[T]":
        """Combine with AND logic.

        Args:
            other: Other specification

        Returns:
            Combined specification
        """
        return AndSpecification(self, other)

    def or_(self, other: "Specification[T]") -> "Specification[T]":
        """Combine with OR logic.

        Args:
            other: Other specification

        Returns:
            Combined specification
        """
        return OrSpecification(self, other)

    def not_(self) -> "Specification[T]":
        """Negate specification.

        Returns:
            Negated specification
        """
        return NotSpecification(self)


class AndSpecification(Specification[T]):
    """AND combination of specifications."""

    def __init__(self, left: Specification[T], right: Specification[T]):
        """Initialize AND specification.

        Args:
            left: Left specification
            right: Right specification
        """
        self.left = left
        self.right = right

    def is_satisfied_by(self, candidate: T) -> bool:
        """Check if both specifications are satisfied."""
        return self.left.is_satisfied_by(candidate) and self.right.is_satisfied_by(candidate)


class OrSpecification(Specification[T]):
    """OR combination of specifications."""

    def __init__(self, left: Specification[T], right: Specification[T]):
        """Initialize OR specification.

        Args:
            left: Left specification
            right: Right specification
        """
        self.left = left
        self.right = right

    def is_satisfied_by(self, candidate: T) -> bool:
        """Check if either specification is satisfied."""
        return self.left.is_satisfied_by(candidate) or self.right.is_satisfied_by(candidate)


class NotSpecification(Specification[T]):
    """NOT negation of specification."""

    def __init__(self, spec: Specification[T]):
        """Initialize NOT specification.

        Args:
            spec: Specification to negate
        """
        self.spec = spec

    def is_satisfied_by(self, candidate: T) -> bool:
        """Check if specification is not satisfied."""
        return not self.spec.is_satisfied_by(candidate)
