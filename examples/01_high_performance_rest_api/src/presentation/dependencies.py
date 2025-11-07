"""FastAPI dependency injection.

Provides dependencies for database sessions and application services.
"""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from examples.01_high_performance_rest_api.src.application.services.product_service import (
    ProductService,
)
from examples.01_high_performance_rest_api.src.application.services.inventory_service import (
    InventoryService,
)
from examples.01_high_performance_rest_api.src.infrastructure.database.session import (
    get_session,
)
from examples.01_high_performance_rest_api.src.infrastructure.database.repositories import (
    SQLProductRepository,
    SQLInventoryRepository,
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session dependency.

    Yields:
        AsyncSession instance with automatic cleanup

    Example:
        @app.get("/products")
        async def list_products(session: AsyncSession = Depends(get_db_session)):
            ...
    """
    db = get_session()
    async with db.session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def get_product_service(
    session: AsyncSession = None,
) -> ProductService:
    """Get product service dependency.

    Args:
        session: Database session (injected by FastAPI)

    Returns:
        ProductService instance

    Example:
        @app.get("/products")
        async def list_products(
            service: ProductService = Depends(get_product_service)
        ):
            return await service.get_all()
    """
    if session is None:
        # For testing or manual usage
        db = get_session()
        async with db.session() as session:
            repository = SQLProductRepository(session)
            return ProductService(repository)
    else:
        repository = SQLProductRepository(session)
        return ProductService(repository)


async def get_inventory_service(
    session: AsyncSession = None,
) -> InventoryService:
    """Get inventory service dependency.

    Args:
        session: Database session (injected by FastAPI)

    Returns:
        InventoryService instance

    Example:
        @app.get("/inventory")
        async def list_inventory(
            service: InventoryService = Depends(get_inventory_service)
        ):
            return await service.get_all()
    """
    if session is None:
        db = get_session()
        async with db.session() as session:
            repository = SQLInventoryRepository(session)
            return InventoryService(repository)
    else:
        repository = SQLInventoryRepository(session)
        return InventoryService(repository)
