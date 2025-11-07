"""Data Transfer Objects for API requests and responses."""

from examples.01_high_performance_rest_api.src.application.dtos.product_dtos import (
    ProductDTO,
    CreateProductDTO,
    UpdateProductDTO,
    ProductListDTO,
)
from examples.01_high_performance_rest_api.src.application.dtos.inventory_dtos import (
    InventoryItemDTO,
    CreateInventoryDTO,
    UpdateInventoryDTO,
    InventoryListDTO,
    StockOperationDTO,
)

__all__ = [
    # Product DTOs
    "ProductDTO",
    "CreateProductDTO",
    "UpdateProductDTO",
    "ProductListDTO",
    # Inventory DTOs
    "InventoryItemDTO",
    "CreateInventoryDTO",
    "UpdateInventoryDTO",
    "InventoryListDTO",
    "StockOperationDTO",
]
