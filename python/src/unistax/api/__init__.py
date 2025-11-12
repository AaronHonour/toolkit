"""API framework integration module."""

from unistax.api.app import APIApplication, RouteConfig
from unistax.api.decorators import delete, get, patch, post, put
from unistax.api.dependencies import Depends, inject
from unistax.api.responses import APIResponse, ErrorResponse, PaginatedResponse
from unistax.api.router import APIRouter

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
