"""Sorting utilities."""

from dataclasses import dataclass
from enum import Enum


class SortOrder(str, Enum):
    """Sort order."""

    ASC = "asc"
    DESC = "desc"


@dataclass
class SortField:
    """Sort field specification."""

    field: str
    order: SortOrder = SortOrder.ASC

    def apply_to_query(self, query: any, model: any) -> any:
        """Apply sort to SQLAlchemy query.

        Args:
            query: SQLAlchemy query
            model: SQLAlchemy model

        Returns:
            Sorted query
        """
        column = getattr(model, self.field)

        if self.order == SortOrder.DESC:
            return query.order_by(column.desc())
        return query.order_by(column.asc())


class Sorter:
    """Sorting utility."""

    def __init__(self, sort_fields: list[SortField] | None = None):
        """Initialize sorter.

        Args:
            sort_fields: List of sort fields
        """
        self.sort_fields = sort_fields or []

    def add_sort(self, field: str, order: SortOrder = SortOrder.ASC):
        """Add sort field.

        Args:
            field: Field name
            order: Sort order
        """
        self.sort_fields.append(SortField(field, order))

    def apply_to_query(self, query: any, model: any) -> any:
        """Apply all sorts to query.

        Args:
            query: SQLAlchemy query
            model: SQLAlchemy model

        Returns:
            Sorted query
        """
        for sort_field in self.sort_fields:
            query = sort_field.apply_to_query(query, model)
        return query
