"""API endpoints router."""

from fastapi import APIRouter

from examples.01_high_performance_rest_api.src.presentation.api import (
    products,
    inventory,
)

api_router = APIRouter()

# Include sub-routers
api_router.include_router(
    products.router,
    prefix="/products",
    tags=["products"]
)

api_router.include_router(
    inventory.router,
    prefix="/inventory",
    tags=["inventory"]
)

__all__ = ["api_router"]
