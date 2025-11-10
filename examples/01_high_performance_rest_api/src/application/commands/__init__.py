"""Application commands for write operations (CQRS pattern)."""

from src.application.commands.product_commands import (
    CreateProductCommand,
    UpdateProductCommand,
    DeleteProductCommand,
    BulkCreateProductsCommand,
    BulkUpdateProductStatusCommand,
    ProductCommandHandler,
)
from src.application.commands.inventory_commands import (
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
