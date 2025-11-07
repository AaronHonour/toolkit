"""Repository interfaces for domain models."""

from examples.01_high_performance_rest_api.src.domain.repositories.product_repository import (
    ProductRepository,
)
from examples.01_high_performance_rest_api.src.domain.repositories.inventory_repository import (
    InventoryRepository,
)

__all__ = [
    "ProductRepository",
    "InventoryRepository",
]
