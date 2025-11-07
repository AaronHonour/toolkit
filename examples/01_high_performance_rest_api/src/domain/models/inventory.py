"""Inventory domain model."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class StockStatus(str, Enum):
    """Stock status enumeration."""

    IN_STOCK = "in_stock"
    LOW_STOCK = "low_stock"
    OUT_OF_STOCK = "out_of_stock"
    DISCONTINUED = "discontinued"


@dataclass
class InventoryItem:
    """Inventory item entity.

    Tracks product stock levels and availability.
    Optimized with __slots__ for memory efficiency.
    """

    __slots__ = (
        "id",
        "product_id",
        "quantity",
        "reserved",
        "reorder_point",
        "reorder_quantity",
        "warehouse_location",
        "status",
        "last_restock_date",
        "updated_at",
    )

    id: Optional[int]
    product_id: int
    quantity: int
    reserved: int
    reorder_point: int
    reorder_quantity: int
    warehouse_location: str
    status: StockStatus
    last_restock_date: Optional[datetime]
    updated_at: datetime

    def __init__(
        self,
        product_id: int,
        quantity: int = 0,
        reserved: int = 0,
        reorder_point: int = 10,
        reorder_quantity: int = 100,
        warehouse_location: str = "MAIN",
        status: StockStatus = StockStatus.IN_STOCK,
        id: Optional[int] = None,
        last_restock_date: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        """Initialize inventory item.

        Args:
            product_id: Associated product ID
            quantity: Total quantity in stock
            reserved: Reserved quantity (pending orders)
            reorder_point: Quantity threshold for reordering
            reorder_quantity: Quantity to reorder
            warehouse_location: Warehouse location code
            status: Stock status
            id: Optional ID (set by repository)
            last_restock_date: Last restock date
            updated_at: Update timestamp
        """
        self.id = id
        self.product_id = product_id
        self.quantity = quantity
        self.reserved = reserved
        self.reorder_point = reorder_point
        self.reorder_quantity = reorder_quantity
        self.warehouse_location = warehouse_location
        self.status = status
        self.last_restock_date = last_restock_date
        self.updated_at = updated_at or datetime.utcnow()

    @property
    def available(self) -> int:
        """Calculate available quantity.

        Returns:
            Available quantity (total - reserved)
        """
        return max(0, self.quantity - self.reserved)

    @property
    def needs_reorder(self) -> bool:
        """Check if reorder is needed.

        Returns:
            True if available quantity is below reorder point
        """
        return self.available <= self.reorder_point

    def is_in_stock(self) -> bool:
        """Check if item is in stock.

        Returns:
            True if available quantity > 0
        """
        return self.available > 0

    def is_low_stock(self) -> bool:
        """Check if stock is low.

        Returns:
            True if needs reorder but still available
        """
        return self.needs_reorder and self.is_in_stock()

    def reserve(self, quantity: int) -> bool:
        """Reserve quantity for order.

        Args:
            quantity: Quantity to reserve

        Returns:
            True if reservation successful

        Raises:
            ValueError: If quantity invalid or insufficient stock
        """
        if quantity <= 0:
            raise ValueError("Quantity must be positive")

        if self.available < quantity:
            return False

        self.reserved += quantity
        self._update_status()
        return True

    def release(self, quantity: int):
        """Release reserved quantity.

        Args:
            quantity: Quantity to release

        Raises:
            ValueError: If quantity invalid or exceeds reserved
        """
        if quantity <= 0:
            raise ValueError("Quantity must be positive")

        if quantity > self.reserved:
            raise ValueError("Cannot release more than reserved")

        self.reserved -= quantity
        self._update_status()

    def fulfill(self, quantity: int):
        """Fulfill order (remove from both reserved and total).

        Args:
            quantity: Quantity to fulfill

        Raises:
            ValueError: If quantity invalid or exceeds reserved
        """
        if quantity <= 0:
            raise ValueError("Quantity must be positive")

        if quantity > self.reserved:
            raise ValueError("Cannot fulfill more than reserved")

        self.reserved -= quantity
        self.quantity -= quantity
        self._update_status()

    def restock(self, quantity: int):
        """Add stock quantity.

        Args:
            quantity: Quantity to add

        Raises:
            ValueError: If quantity invalid
        """
        if quantity <= 0:
            raise ValueError("Quantity must be positive")

        self.quantity += quantity
        self.last_restock_date = datetime.utcnow()
        self._update_status()

    def adjust(self, quantity: int, reason: str = "adjustment"):
        """Adjust stock quantity (can be positive or negative).

        Args:
            quantity: Quantity adjustment (positive or negative)
            reason: Reason for adjustment
        """
        new_quantity = self.quantity + quantity

        if new_quantity < 0:
            raise ValueError("Cannot adjust to negative quantity")

        self.quantity = new_quantity
        self._update_status()

    def _update_status(self):
        """Update stock status based on current quantity."""
        self.updated_at = datetime.utcnow()

        if self.status == StockStatus.DISCONTINUED:
            return  # Don't change discontinued status

        if not self.is_in_stock():
            self.status = StockStatus.OUT_OF_STOCK
        elif self.is_low_stock():
            self.status = StockStatus.LOW_STOCK
        else:
            self.status = StockStatus.IN_STOCK

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"InventoryItem(product_id={self.product_id}, "
            f"quantity={self.quantity}, available={self.available}, status={self.status})"
        )
