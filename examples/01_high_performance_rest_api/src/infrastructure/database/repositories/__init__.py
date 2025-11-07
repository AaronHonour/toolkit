"""SQL repository implementations with performance optimizations."""

from examples.01_high_performance_rest_api.src.infrastructure.database.repositories.product_repository import (
    SQLProductRepository,
)
from examples.01_high_performance_rest_api.src.infrastructure.database.repositories.inventory_repository import (
    SQLInventoryRepository,
)

__all__ = [
    "SQLProductRepository",
    "SQLInventoryRepository",
]
