"""API framework integration module."""

from unistax.api.app import APIApplication, RouteConfig
from unistax.api.router import APIRouter
from unistax.api.decorators import get, post, put, patch, delete
from unistax.api.responses import APIResponse, ErrorResponse, PaginatedResponse
from unistax.api.dependencies import Depends, inject

__all__ = [
    "APIApplication",
    "RouteConfig",
    "APIRouter",
    "get",
    "post",
    "put",
    "patch",
    "delete",
    "APIResponse",
    "ErrorResponse",
    "PaginatedResponse",
    "Depends",
    "inject",
]
