"""API response models."""

from typing import Any, Dict, Generic, List, Optional, TypeVar
from pydantic import BaseModel

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    """Standard API response."""

    success: bool = True
    data: Optional[T] = None
    message: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None


class ErrorResponse(BaseModel):
    """Error response."""

    success: bool = False
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None
    code: Optional[str] = None


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response."""

    success: bool = True
    data: List[T]
    page: int
    page_size: int
    total: int
    total_pages: int
    has_next: bool
    has_prev: bool
