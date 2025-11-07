"""Pydantic schemas for API request/response validation."""

from examples.01_high_performance_rest_api.src.presentation.schemas.product_schemas import (
    ProductResponse,
    ProductCreate,
    ProductUpdate,
    ProductListResponse,
)
from examples.01_high_performance_rest_api.src.presentation.schemas.inventory_schemas import (
    InventoryResponse,
    InventoryCreate,
    InventoryUpdate,
    StockOperation,
    TransferStock,
    InventoryListResponse,
)

__all__ = [
    # Product schemas
    "ProductResponse",
    "ProductCreate",
    "ProductUpdate",
    "ProductListResponse",
    # Inventory schemas
    "InventoryResponse",
    "InventoryCreate",
    "InventoryUpdate",
    "StockOperation",
    "TransferStock",
    "InventoryListResponse",
]
