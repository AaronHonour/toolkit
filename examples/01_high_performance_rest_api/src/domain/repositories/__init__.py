"""Repository interfaces for domain models."""

from src.domain.repositories.product_repository import (
    ProductRepository,
)
from src.domain.repositories.inventory_repository import (
    InventoryRepository,
)

__all__ = [
    "ProductRepository",
    "InventoryRepository",
]
