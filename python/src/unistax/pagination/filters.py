"""Filtering utilities."""

from dataclasses import dataclass
from enum import Enum
from typing import Any


class FilterOperator(str, Enum):
    """Filter operators."""

    EQ = "eq"  # Equal
    NE = "ne"  # Not equal
    GT = "gt"  # Greater than
    GTE = "gte"  # Greater than or equal
    LT = "lt"  # Less than
    LTE = "lte"  # Less than or equal
    IN = "in"  # In list
    NOT_IN = "not_in"  # Not in list
    CONTAINS = "contains"  # Contains
    STARTS_WITH = "starts_with"  # Starts with
    ENDS_WITH = "ends_with"  # Ends with
    IS_NULL = "is_null"  # Is null
    IS_NOT_NULL = "is_not_null"  # Is not null


@dataclass
class Filter:
    """Filter specification."""

    field: str
    operator: FilterOperator
    value: Any = None

    def apply_to_query(self, query: Any, model: Any) -> Any:
        """Apply filter to SQLAlchemy query.

        Args:
            query: SQLAlchemy query
            model: SQLAlchemy model

        Returns:
            Filtered query
        """
        column = getattr(model, self.field)

        if self.operator == FilterOperator.EQ:
            return query.filter(column == self.value)
        elif self.operator == FilterOperator.NE:
            return query.filter(column != self.value)
        elif self.operator == FilterOperator.GT:
            return query.filter(column > self.value)
        elif self.operator == FilterOperator.GTE:
            return query.filter(column >= self.value)
        elif self.operator == FilterOperator.LT:
            return query.filter(column < self.value)
        elif self.operator == FilterOperator.LTE:
            return query.filter(column <= self.value)
        elif self.operator == FilterOperator.IN:
            return query.filter(column.in_(self.value))
        elif self.operator == FilterOperator.NOT_IN:
            return query.filter(~column.in_(self.value))
        elif self.operator == FilterOperator.CONTAINS:
            return query.filter(column.contains(self.value))
        elif self.operator == FilterOperator.STARTS_WITH:
            return query.filter(column.startswith(self.value))
        elif self.operator == FilterOperator.ENDS_WITH:
            return query.filter(column.endswith(self.value))
        elif self.operator == FilterOperator.IS_NULL:
            return query.filter(column.is_(None))
        elif self.operator == FilterOperator.IS_NOT_NULL:
            return query.filter(column.isnot(None))

        return query


class FilterSet:
    """Collection of filters."""

    def __init__(self, filters: list[Filter] | None = None) -> None:
        """Initialize filter set.

        Args:
            filters: List of filters
        """
        self.filters = filters or []

    def add_filter(self, field: str, operator: FilterOperator, value: Any = None) -> None:
        """Add filter.

        Args:
            field: Field name
            operator: Filter operator
            value: Filter value
        """
        self.filters.append(Filter(field, operator, value))

    def apply_to_query(self, query: Any, model: Any) -> Any:
        """Apply all filters to query.

        Args:
            query: SQLAlchemy query
            model: SQLAlchemy model

        Returns:
            Filtered query
        """
        for filter_spec in self.filters:
            query = filter_spec.apply_to_query(query, model)
        return query
