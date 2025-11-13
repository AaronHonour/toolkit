"""API response models."""

from typing import Any, Generic, TypeVar

from pydantic import BaseModel  # type: ignore[import-not-found]

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):  # type: ignore[misc]
    """Standard API response."""

    success: bool = True
    data: T | None = None
    message: str | None = None
    meta: dict[str, Any] | None = None


class ErrorResponse(BaseModel):  # type: ignore[misc]
    """Error response."""

    success: bool = False
    error: str
    message: str
    details: dict[str, Any] | None = None
    code: str | None = None


class PaginatedResponse(BaseModel, Generic[T]):  # type: ignore[misc]
    """Paginated response."""

    success: bool = True
    data: list[T]
    page: int
    page_size: int
    total: int
    total_pages: int
    has_next: bool
    has_prev: bool
