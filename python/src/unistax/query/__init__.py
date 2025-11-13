"""Query builder and specification pattern module."""

from unistax.query.builder import Query, QueryBuilder
from unistax.query.specification import (
    AndSpecification,
    NotSpecification,
    OrSpecification,
    Specification,
)

__all__ = [
    "QueryBuilder",
    "Query",
    "Specification",
    "AndSpecification",
    "OrSpecification",
    "NotSpecification",
]
