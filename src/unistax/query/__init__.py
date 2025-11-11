"""Query builder and specification pattern module."""

from unistax.query.builder import QueryBuilder, Query
from unistax.query.specification import Specification, AndSpecification, OrSpecification, NotSpecification

__all__ = [
    "QueryBuilder",
    "Query",
    "Specification",
    "AndSpecification",
    "OrSpecification",
    "NotSpecification",
]
