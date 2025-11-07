"""Application commands for write operations (CQRS pattern)."""

from examples.01_high_performance_rest_api.src.application.commands.product_commands import (
    CreateProductCommand,
    UpdateProductCommand,
    DeleteProductCommand,
    BulkCreateProductsCommand,
    BulkUpdateProductStatusCommand,
    ProductCommandHandler,
)
from examples.01_high_performance_rest_api.src.application.commands.inventory_commands import (
    CreateInventoryCommand,
    UpdateInventoryCommand,
    ReserveStockCommand,
    ReleaseReservationCommand,
    FulfillReservationCommand,
    AddStockCommand,
    RemoveStockCommand,
    TransferStockCommand,
    InventoryCommandHandler,
)

__all__ = [
    # Product commands
    "CreateProductCommand",
    "UpdateProductCommand",
    "DeleteProductCommand",
    "BulkCreateProductsCommand",
    "BulkUpdateProductStatusCommand",
    "ProductCommandHandler",
    # Inventory commands
    "CreateInventoryCommand",
    "UpdateInventoryCommand",
    "ReserveStockCommand",
    "ReleaseReservationCommand",
    "FulfillReservationCommand",
    "AddStockCommand",
    "RemoveStockCommand",
    "TransferStockCommand",
    "InventoryCommandHandler",
]
