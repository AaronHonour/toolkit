"""Unit tests for Product domain model."""

from decimal import Decimal
from datetime import datetime

import pytest

from examples.01_high_performance_rest_api.src.domain.models.product import (
    Product,
    ProductStatus,
)


@pytest.mark.unit
class TestProductModel:
    """Test Product domain model."""

    def test_create_product(self):
        """Test creating a product."""
        product = Product.create(
            sku="TEST-001",
            name="Test Product",
            description="A test product",
            category="Test",
            price=Decimal("99.99"),
            cost=Decimal("45.00"),
            tags=["test"],
            metadata={"key": "value"},
        )

        assert product.id is not None
        assert product.sku == "TEST-001"
        assert product.name == "Test Product"
        assert product.status == ProductStatus.ACTIVE
        assert product.price == Decimal("99.99")
        assert product.cost == Decimal("45.00")
        assert "test" in product.tags
        assert product.metadata["key"] == "value"
        assert isinstance(product.created_at, datetime)
        assert isinstance(product.updated_at, datetime)

    def test_product_margin_calculation(self):
        """Test profit margin calculation."""
        product = Product.create(
            sku="TEST-002",
            name="Test",
            description="Test",
            category="Test",
            price=Decimal("100.00"),
            cost=Decimal("60.00"),
            tags=[],
        )

        # Margin = (price - cost) / price = (100 - 60) / 100 = 0.40
        assert product.margin == Decimal("0.40")

    def test_product_margin_zero_price(self):
        """Test margin calculation with zero price."""
        product = Product.create(
            sku="TEST-003",
            name="Test",
            description="Test",
            category="Test",
            price=Decimal("0.00"),
            cost=Decimal("10.00"),
            tags=[],
        )

        assert product.margin == Decimal("0")

    def test_is_active(self):
        """Test is_active property."""
        product = Product.create(
            sku="TEST-004",
            name="Test",
            description="Test",
            category="Test",
            price=Decimal("99.99"),
            cost=Decimal("45.00"),
            tags=[],
        )

        assert product.is_active is True

        product.status = ProductStatus.DISCONTINUED
        assert product.is_active is False

    def test_update_info(self):
        """Test updating product information."""
        product = Product.create(
            sku="TEST-005",
            name="Original Name",
            description="Original Description",
            category="Original",
            price=Decimal("99.99"),
            cost=Decimal("45.00"),
            tags=[],
        )

        updated = product.update_info(
            name="New Name",
            description="New Description",
            category="New Category",
        )

        assert updated.name == "New Name"
        assert updated.description == "New Description"
        assert updated.category == "New Category"
        assert updated.sku == product.sku  # SKU shouldn't change

    def test_update_pricing(self):
        """Test updating product pricing."""
        product = Product.create(
            sku="TEST-006",
            name="Test",
            description="Test",
            category="Test",
            price=Decimal("99.99"),
            cost=Decimal("45.00"),
            tags=[],
        )

        updated = product.update_pricing(
            price=Decimal("109.99"),
            cost=Decimal("50.00"),
        )

        assert updated.price == Decimal("109.99")
        assert updated.cost == Decimal("50.00")

    def test_add_tag(self):
        """Test adding tags to product."""
        product = Product.create(
            sku="TEST-007",
            name="Test",
            description="Test",
            category="Test",
            price=Decimal("99.99"),
            cost=Decimal("45.00"),
            tags=["initial"],
        )

        updated = product.add_tag("new-tag")
        assert "initial" in updated.tags
        assert "new-tag" in updated.tags
        assert len(updated.tags) == 2

        # Adding duplicate shouldn't change tags
        updated2 = updated.add_tag("new-tag")
        assert len(updated2.tags) == 2

    def test_remove_tag(self):
        """Test removing tags from product."""
        product = Product.create(
            sku="TEST-008",
            name="Test",
            description="Test",
            category="Test",
            price=Decimal("99.99"),
            cost=Decimal("45.00"),
            tags=["tag1", "tag2", "tag3"],
        )

        updated = product.remove_tag("tag2")
        assert "tag1" in updated.tags
        assert "tag2" not in updated.tags
        assert "tag3" in updated.tags
        assert len(updated.tags) == 2

    def test_has_tag(self):
        """Test checking if product has tag."""
        product = Product.create(
            sku="TEST-009",
            name="Test",
            description="Test",
            category="Test",
            price=Decimal("99.99"),
            cost=Decimal("45.00"),
            tags=["premium", "featured"],
        )

        assert product.has_tag("premium") is True
        assert product.has_tag("featured") is True
        assert product.has_tag("nonexistent") is False

    def test_update_metadata(self):
        """Test updating metadata."""
        product = Product.create(
            sku="TEST-010",
            name="Test",
            description="Test",
            category="Test",
            price=Decimal("99.99"),
            cost=Decimal("45.00"),
            tags=[],
            metadata={"key1": "value1"},
        )

        updated = product.update_metadata("key2", "value2")
        assert updated.metadata["key1"] == "value1"
        assert updated.metadata["key2"] == "value2"

    def test_slots_optimization(self):
        """Test that __slots__ is properly defined for memory optimization."""
        product = Product.create(
            sku="TEST-011",
            name="Test",
            description="Test",
            category="Test",
            price=Decimal("99.99"),
            cost=Decimal("45.00"),
            tags=[],
        )

        # __slots__ objects don't have __dict__
        assert not hasattr(product, "__dict__")

    def test_product_validation(self):
        """Test product validation rules."""
        # Price must be positive
        with pytest.raises(ValueError):
            Product.create(
                sku="TEST-012",
                name="Test",
                description="Test",
                category="Test",
                price=Decimal("-10.00"),
                cost=Decimal("5.00"),
                tags=[],
            )

        # Cost must be positive
        with pytest.raises(ValueError):
            Product.create(
                sku="TEST-013",
                name="Test",
                description="Test",
                category="Test",
                price=Decimal("10.00"),
                cost=Decimal("-5.00"),
                tags=[],
            )
