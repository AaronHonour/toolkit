"""Application queries for read operations (CQRS pattern)."""

from examples.01_high_performance_rest_api.src.application.queries.product_queries import (
    GetProductByIdQuery,
    GetProductBySkuQuery,
    GetAllProductsQuery,
    GetProductsByCategoryQuery,
    SearchProductsQuery,
    GetProductsByTagsQuery,
    GetProductsByPriceRangeQuery,
    GetLowMarginProductsQuery,
    ProductQueryHandler,
)
from examples.01_high_performance_rest_api.src.application.queries.inventory_queries import (
    GetInventoryByIdQuery,
    GetInventoryByProductIdQuery,
    GetAllInventoryQuery,
    GetInventoryByLocationQuery,
    GetLowStockItemsQuery,
    GetOutOfStockItemsQuery,
    GetItemsNeedingRestockQuery,
    GetInventorySnapshotQuery,
    InventoryQueryHandler,
)

__all__ = [
    # Product queries
    "GetProductByIdQuery",
    "GetProductBySkuQuery",
    "GetAllProductsQuery",
    "GetProductsByCategoryQuery",
    "SearchProductsQuery",
    "GetProductsByTagsQuery",
    "GetProductsByPriceRangeQuery",
    "GetLowMarginProductsQuery",
    "ProductQueryHandler",
    # Inventory queries
    "GetInventoryByIdQuery",
    "GetInventoryByProductIdQuery",
    "GetAllInventoryQuery",
    "GetInventoryByLocationQuery",
    "GetLowStockItemsQuery",
    "GetOutOfStockItemsQuery",
    "GetItemsNeedingRestockQuery",
    "GetInventorySnapshotQuery",
    "InventoryQueryHandler",
]
