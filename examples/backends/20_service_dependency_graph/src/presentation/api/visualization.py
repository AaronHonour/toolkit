"""API endpoints for graph visualization."""

from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import Response
from typing import Any, Dict

from src.application.services.graph_service import get_graph_service, GraphService

router = APIRouter()


@router.get("")
async def visualize_graph(
    format: str = Query(default="d3", description="Visualization format (d3, cytoscape, mermaid, graphviz)"),
    graph_service: GraphService = Depends(get_graph_service),
) -> Any:
    """Export dependency graph in various visualization formats."""
    # Validate format
    valid_formats = ["d3", "d3_force", "cytoscape", "mermaid", "graphviz"]
    if format not in valid_formats:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid format. Must be one of: {', '.join(valid_formats)}",
        )

    # Normalize format
    if format == "d3":
        format = "d3_force"

    try:
        result = graph_service.visualize(format)

        # Return appropriate response type
        if format in ("mermaid", "graphviz"):
            # Return as plain text
            return Response(content=result, media_type="text/plain")
        else:
            # Return as JSON
            return result

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )


@router.get("/stats")
async def get_visualization_stats(
    graph_service: GraphService = Depends(get_graph_service),
) -> Dict[str, Any]:
    """Get statistics about the graph for visualization."""
    service_count = graph_service.get_service_count()
    dependency_count = graph_service.get_dependency_count()

    return {
        "service_count": service_count,
        "dependency_count": dependency_count,
        "avg_dependencies_per_service": (
            dependency_count / service_count if service_count > 0 else 0
        ),
        "supported_formats": ["d3", "cytoscape", "mermaid", "graphviz"],
    }
