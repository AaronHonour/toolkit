"""API framework integration module."""

from toolkit.api.app import APIApplication, RouteConfig
from toolkit.api.router import APIRouter
from toolkit.api.decorators import get, post, put, patch, delete
from toolkit.api.responses import APIResponse, ErrorResponse, PaginatedResponse
from toolkit.api.dependencies import Depends, inject

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
