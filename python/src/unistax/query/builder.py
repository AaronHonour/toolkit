"""Query builder for composable queries."""

from typing import Any, List, Optional
from dataclasses import dataclass, field


@dataclass
class Query:
    """Query representation."""

    filters: List[dict] = field(default_factory=list)
    sorts: List[dict] = field(default_factory=list)
    limit: Optional[int] = None
    offset: Optional[int] = None
    select_fields: Optional[List[str]] = None


class QueryBuilder:
    """Fluent query builder."""

    def __init__(self):
        """Initialize query builder."""
        self._query = Query()

    def where(self, field: str, operator: str, value: Any) -> "QueryBuilder":
        """Add filter condition.

        Args:
            field: Field name
            operator: Operator (eq, ne, gt, lt, in, etc.)
            value: Filter value

        Returns:
            QueryBuilder for chaining
        """
        self._query.filters.append({
            "field": field,
            "operator": operator,
            "value": value,
        })
        return self

    def order_by(self, field: str, direction: str = "asc") -> "QueryBuilder":
        """Add sort condition.

        Args:
            field: Field name
            direction: Sort direction (asc/desc)

        Returns:
            QueryBuilder for chaining
        """
        self._query.sorts.append({
            "field": field,
            "direction": direction,
        })
        return self

    def limit(self, limit: int) -> "QueryBuilder":
        """Set query limit.

        Args:
            limit: Maximum results

        Returns:
            QueryBuilder for chaining
        """
        self._query.limit = limit
        return self

    def offset(self, offset: int) -> "QueryBuilder":
        """Set query offset.

        Args:
            offset: Results offset

        Returns:
            QueryBuilder for chaining
        """
        self._query.offset = offset
        return self

    def select(self, *fields: str) -> "QueryBuilder":
        """Select specific fields.

        Args:
            *fields: Field names

        Returns:
            QueryBuilder for chaining
        """
        self._query.select_fields = list(fields)
        return self

    def build(self) -> Query:
        """Build query.

        Returns:
            Query object
        """
        return self._query

    def apply_to_sqlalchemy(self, query: Any, model: Any) -> Any:
        """Apply query to SQLAlchemy query object.

        Args:
            query: SQLAlchemy query
            model: SQLAlchemy model

        Returns:
            Modified query
        """
        # Apply filters
        for filter_spec in self._query.filters:
            column = getattr(model, filter_spec["field"])
            op = filter_spec["operator"]
            val = filter_spec["value"]

            if op == "eq":
                query = query.filter(column == val)
            elif op == "ne":
                query = query.filter(column != val)
            elif op == "gt":
                query = query.filter(column > val)
            elif op == "lt":
                query = query.filter(column < val)
            elif op == "in":
                query = query.filter(column.in_(val))

        # Apply sorting
        for sort_spec in self._query.sorts:
            column = getattr(model, sort_spec["field"])
            if sort_spec["direction"] == "desc":
                query = query.order_by(column.desc())
            else:
                query = query.order_by(column.asc())

        # Apply pagination
        if self._query.offset:
            query = query.offset(self._query.offset)
        if self._query.limit:
            query = query.limit(self._query.limit)

        return query
