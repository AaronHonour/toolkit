"""Product command handlers for write operations.

Implements CQRS pattern - commands represent intent to change state.
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from src.domain.models.product import (
    Product,
    ProductStatus,
)
from src.domain.repositories.product_repository import (
    ProductRepository,
)


# Command models (intent to change state)


@dataclass
class CreateProductCommand:
    """Command to create a new product."""

    sku: str
    name: str
    description: str
    category: str
    price: Decimal
    cost: Decimal
    tags: List[str]
    metadata: Optional[dict] = None


@dataclass
class UpdateProductCommand:
    """Command to update an existing product."""

    product_id: UUID
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    price: Optional[Decimal] = None
    cost: Optional[Decimal] = None
    status: Optional[ProductStatus] = None
    tags: Optional[List[str]] = None
    metadata: Optional[dict] = None


@dataclass
class DeleteProductCommand:
    """Command to delete a product."""

    product_id: UUID


@dataclass
class BulkCreateProductsCommand:
    """Command to create multiple products in batch."""

    products: List[CreateProductCommand]


@dataclass
class BulkUpdateProductStatusCommand:
    """Command to bulk update product status."""

    product_ids: List[UUID]
    status: ProductStatus


# Command handler


class ProductCommandHandler:
    """Handles product write operations.

    Orchestrates domain logic and repository operations for commands.
    """

    __slots__ = ("_repository",)

    def __init__(self, repository: ProductRepository):
        """Initialize command handler.

        Args:
            repository: Product repository implementation
        """
        self._repository = repository

    async def handle_create(self, command: CreateProductCommand) -> Product:
        """Handle create product command.

        Args:
            command: Create product command

        Returns:
            Created product

        Raises:
            ValueError: If SKU already exists
        """
        # Check if SKU already exists
        existing = await self._repository.get_by_sku(command.sku)
        if existing:
            raise ValueError(f"Product with SKU {command.sku} already exists")

        # Create domain entity
        product = Product.create(
            sku=command.sku,
            name=command.name,
            description=command.description,
            category=command.category,
            price=command.price,
            cost=command.cost,
            tags=command.tags,
            metadata=command.metadata,
        )

        # Persist
        return await self._repository.create(product)

    async def handle_update(self, command: UpdateProductCommand) -> Product:
        """Handle update product command.

        Args:
            command: Update product command

        Returns:
            Updated product

        Raises:
            ValueError: If product not found
        """
        # Get existing product
        product = await self._repository.get_by_id(command.product_id)
        if not product:
            raise ValueError(f"Product {command.product_id} not found")

        # Apply updates
        if command.name is not None:
            product = product.update_info(
                name=command.name,
                description=command.description or product.description,
                category=command.category or product.category,
            )

        if command.price is not None:
            product = product.update_pricing(command.price, command.cost or product.cost)

        if command.status is not None:
            product.status = command.status

        if command.tags is not None:
            for tag in command.tags:
                if tag not in product.tags:
                    product = product.add_tag(tag)

        if command.metadata is not None:
            for key, value in command.metadata.items():
                product = product.update_metadata(key, value)

        # Persist
        return await self._repository.update(product)

    async def handle_delete(self, command: DeleteProductCommand) -> bool:
        """Handle delete product command.

        Args:
            command: Delete product command

        Returns:
            True if deleted, False if not found
        """
        return await self._repository.delete(command.product_id)

    async def handle_bulk_create(
        self, command: BulkCreateProductsCommand
    ) -> List[Product]:
        """Handle bulk create products command.

        Args:
            command: Bulk create command

        Returns:
            List of created products
        """
        # Create domain entities
        products = [
            Product.create(
                sku=cmd.sku,
                name=cmd.name,
                description=cmd.description,
                category=cmd.category,
                price=cmd.price,
                cost=cmd.cost,
                tags=cmd.tags,
                metadata=cmd.metadata,
            )
            for cmd in command.products
        ]

        # Bulk persist (optimized with batching)
        return await self._repository.bulk_create(products)

    async def handle_bulk_update_status(
        self, command: BulkUpdateProductStatusCommand
    ) -> int:
        """Handle bulk update product status command.

        Args:
            command: Bulk update status command

        Returns:
            Number of products updated
        """
        return await self._repository.bulk_update_status(
            command.product_ids, command.status
        )
