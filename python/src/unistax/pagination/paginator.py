"""Pagination utilities."""

from dataclasses import dataclass
from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


@dataclass
class PaginationParams:
    """Pagination parameters."""

    page: int = 1
    page_size: int = 20
    offset: int | None = None

    def get_offset(self) -> int:
        """Calculate offset from page and page_size."""
        if self.offset is not None:
            return self.offset
        return (self.page - 1) * self.page_size

    def get_limit(self) -> int:
        """Get limit (page_size)."""
        return self.page_size


class Page(BaseModel, Generic[T]):
    """Paginated response."""

    items: list[T]
    page: int
    page_size: int
    total: int

    @property
    def total_pages(self) -> int:
        """Calculate total pages."""
        if self.page_size == 0:
            return 0
        return (self.total + self.page_size - 1) // self.page_size

    @property
    def has_next(self) -> bool:
        """Check if has next page."""
        return self.page < self.total_pages

    @property
    def has_prev(self) -> bool:
        """Check if has previous page."""
        return self.page > 1

    @property
    def next_page(self) -> int | None:
        """Get next page number."""
        return self.page + 1 if self.has_next else None

    @property
    def prev_page(self) -> int | None:
        """Get previous page number."""
        return self.page - 1 if self.has_prev else None


class Paginator:
    """Paginator utility."""

    @staticmethod
    def paginate(
        items: list[T],
        params: PaginationParams,
        total: int | None = None,
    ) -> Page[T]:
        """Paginate items.

        Args:
            items: Items to paginate
            params: Pagination parameters
            total: Total count (if known)

        Returns:
            Page with items
        """
        if total is None:
            total = len(items)

        return Page(
            items=items,
            page=params.page,
            page_size=params.page_size,
            total=total,
        )

    @staticmethod
    def paginate_query(query: any, params: PaginationParams) -> tuple[any, int]:
        """Paginate SQLAlchemy query.

        Args:
            query: SQLAlchemy query
            params: Pagination parameters

        Returns:
            Tuple of (paginated_query, total_count)
        """
        total = query.count()
        paginated = query.offset(params.get_offset()).limit(params.get_limit())
        return paginated, total
