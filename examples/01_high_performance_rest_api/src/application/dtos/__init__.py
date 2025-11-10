"""Data Transfer Objects for API requests and responses."""

from src.application.dtos.product_dtos import (
    ProductDTO,
    CreateProductDTO,
    UpdateProductDTO,
    ProductListDTO,
)
from src.application.dtos.inventory_dtos import (
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
