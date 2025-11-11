"""API endpoints for dependency management."""

from fastapi import APIRouter, HTTPException, Depends
from typing import List

from src.presentation.schemas.dependency_schemas import (
    DependencyCreate,
    DependencyResponse,
)
from src.application.services.graph_service import get_graph_service, GraphService

router = APIRouter()


@router.post("", response_model=DependencyResponse, status_code=201)
async def create_dependency(
    dependency: DependencyCreate,
    graph_service: GraphService = Depends(get_graph_service),
) -> DependencyResponse:
    """Record a dependency between services."""
    # Verify source and target services exist
    source_service = graph_service.get_service(dependency.source)
    target_service = graph_service.get_service(dependency.target)

    if not source_service:
        raise HTTPException(
            status_code=404,
            detail=f"Source service '{dependency.source}' not found",
        )

    if not target_service:
        raise HTTPException(
            status_code=404,
            detail=f"Target service '{dependency.target}' not found",
        )

    # Create dependency
    created = graph_service.add_dependency(
        source=dependency.source,
        target=dependency.target,
        dependency_type=dependency.dependency_type,
        weight=dependency.weight,
        metadata=dependency.metadata,
    )

    return DependencyResponse(
        id=str(created.id),
        source=created.source,
        target=created.target,
        dependency_type=created.dependency_type.value,
        weight=created.weight,
        latency_p99=created.latency_p99,
        error_rate=created.error_rate,
        request_rate=created.request_rate,
        metadata=created.metadata,
        created_at=created.created_at,
        updated_at=created.updated_at,
    )


@router.get("", response_model=List[DependencyResponse])
async def list_dependencies(
    graph_service: GraphService = Depends(get_graph_service),
) -> List[DependencyResponse]:
    """List all dependencies."""
    dependencies = graph_service.get_all_dependencies()

    return [
        DependencyResponse(
            id=str(d.id),
            source=d.source,
            target=d.target,
            dependency_type=d.dependency_type.value,
            weight=d.weight,
            latency_p99=d.latency_p99,
            error_rate=d.error_rate,
            request_rate=d.request_rate,
            metadata=d.metadata,
            created_at=d.created_at,
            updated_at=d.updated_at,
        )
        for d in dependencies
    ]


@router.get("/{source}/{target}", response_model=DependencyResponse)
async def get_dependency(
    source: str,
    target: str,
    graph_service: GraphService = Depends(get_graph_service),
) -> DependencyResponse:
    """Get a specific dependency."""
    dependency = graph_service.get_dependency(source, target)

    if not dependency:
        raise HTTPException(
            status_code=404,
            detail=f"Dependency from '{source}' to '{target}' not found",
        )

    return DependencyResponse(
        id=str(dependency.id),
        source=dependency.source,
        target=dependency.target,
        dependency_type=dependency.dependency_type.value,
        weight=dependency.weight,
        latency_p99=dependency.latency_p99,
        error_rate=dependency.error_rate,
        request_rate=dependency.request_rate,
        metadata=dependency.metadata,
        created_at=dependency.created_at,
        updated_at=dependency.updated_at,
    )
