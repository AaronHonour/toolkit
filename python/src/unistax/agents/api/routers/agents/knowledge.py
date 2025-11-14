"""Knowledge graph endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from unistax.agents.api.dependencies import get_knowledge_graph
from unistax.agents.api.schemas import (
    AddEdgeRequest,
    AddNodeRequest,
    BestPracticeRequest,
    IssueRequest,
    KnowledgeEdgeResponse,
    KnowledgeNodeResponse,
)
from unistax.agents.intelligence import AgentKnowledgeGraph, NodeType, RelationType
from unistax.api import APIResponse
from unistax.logging import get_logger

router = APIRouter(prefix="/knowledge", tags=["Knowledge Graph"])
logger = get_logger(__name__)


def _node_to_response(node) -> KnowledgeNodeResponse:
    """Convert knowledge node to response model."""
    return KnowledgeNodeResponse(
        node_id=node.id,
        node_type=node.node_type.value,
        properties=node.properties,
        created_by=node.created_by,
        created_at=node.created_at,
        updated_at=node.updated_at,
    )


def _edge_to_response(edge) -> KnowledgeEdgeResponse:
    """Convert knowledge edge to response model."""
    return KnowledgeEdgeResponse(
        source_id=edge.source_id,
        target_id=edge.target_id,
        relation_type=edge.relation_type.value,
        properties=edge.properties,
        created_by=edge.created_by,
        created_at=edge.created_at,
    )


@router.post(
    "/nodes",
    response_model=APIResponse[KnowledgeNodeResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Add knowledge node",
    description="Add a new node to the knowledge graph",
)
async def add_node(
    request: AddNodeRequest,
    kg: Annotated[AgentKnowledgeGraph, Depends(get_knowledge_graph)],
) -> APIResponse[KnowledgeNodeResponse]:
    """Add knowledge node."""
    logger.info(f"Adding knowledge node: {request.node_id} (type={request.node_type})")

    try:
        node_type = NodeType[request.node_type.upper()]
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid node type: {request.node_type}",
        )

    node = kg.add_node(
        node_id=request.node_id,
        node_type=node_type,
        properties=request.properties,
    )

    logger.info(f"Knowledge node {request.node_id} added successfully")

    return APIResponse(
        success=True,
        data=_node_to_response(node),
        message=f"Node {request.node_id} added successfully",
    )


@router.post(
    "/edges",
    response_model=APIResponse[KnowledgeEdgeResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Add knowledge edge",
    description="Add a new edge (relationship) to the knowledge graph",
)
async def add_edge(
    request: AddEdgeRequest,
    kg: Annotated[AgentKnowledgeGraph, Depends(get_knowledge_graph)],
) -> APIResponse[KnowledgeEdgeResponse]:
    """Add knowledge edge."""
    logger.info(
        f"Adding knowledge edge: {request.source_id} -> {request.target_id} ({request.relation_type})"
    )

    try:
        relation_type = RelationType[request.relation_type.upper()]
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid relation type: {request.relation_type}",
        )

    edge = kg.add_edge(
        source_id=request.source_id,
        target_id=request.target_id,
        relation_type=relation_type,
        properties=request.properties,
    )

    logger.info(f"Knowledge edge added successfully")

    return APIResponse(
        success=True,
        data=_edge_to_response(edge),
        message="Edge added successfully",
    )


@router.post(
    "/best-practices",
    response_model=APIResponse[KnowledgeNodeResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Add best practice",
    description="Share a best practice in the knowledge graph",
)
async def add_best_practice(
    request: BestPracticeRequest,
    kg: Annotated[AgentKnowledgeGraph, Depends(get_knowledge_graph)],
) -> APIResponse[KnowledgeNodeResponse]:
    """Add best practice."""
    logger.info(f"Adding best practice: {request.practice_id}")

    node = kg.add_best_practice(
        practice_id=request.practice_id,
        topic=request.topic,
        description=request.description,
        related_nodes=request.related_nodes,
    )

    logger.info(f"Best practice {request.practice_id} added successfully")

    return APIResponse(
        success=True,
        data=_node_to_response(node),
        message=f"Best practice {request.practice_id} added successfully",
    )


@router.post(
    "/issues",
    response_model=APIResponse[KnowledgeNodeResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Record issue",
    description="Record an issue in the knowledge graph",
)
async def record_issue(
    request: IssueRequest,
    kg: Annotated[AgentKnowledgeGraph, Depends(get_knowledge_graph)],
) -> APIResponse[KnowledgeNodeResponse]:
    """Record issue."""
    logger.info(f"Recording issue: {request.issue_id}")

    node = kg.record_issue(
        issue_id=request.issue_id,
        description=request.description,
        severity=request.severity,
        affected_nodes=request.affected_nodes,
    )

    logger.info(f"Issue {request.issue_id} recorded successfully")

    return APIResponse(
        success=True,
        data=_node_to_response(node),
        message=f"Issue {request.issue_id} recorded successfully",
    )


@router.get(
    "/nodes/{node_id}",
    response_model=APIResponse[KnowledgeNodeResponse],
    summary="Get node",
    description="Get a knowledge graph node by ID",
)
async def get_node(
    node_id: str,
    kg: Annotated[AgentKnowledgeGraph, Depends(get_knowledge_graph)],
) -> APIResponse[KnowledgeNodeResponse]:
    """Get knowledge node."""
    logger.debug(f"Getting knowledge node: {node_id}")

    node = kg.get_node(node_id)
    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Node {node_id} not found",
        )

    return APIResponse(success=True, data=_node_to_response(node))


@router.get(
    "/nodes/{node_id}/dependencies",
    response_model=APIResponse[list[str]],
    summary="Get dependencies",
    description="Get transitive dependencies of a node",
)
async def get_dependencies(
    node_id: str,
    max_depth: int = Query(3, ge=1, le=10, description="Maximum traversal depth"),
    kg: Annotated[AgentKnowledgeGraph, Depends(get_knowledge_graph)],
) -> APIResponse[list[str]]:
    """Get node dependencies."""
    logger.debug(f"Getting dependencies for node: {node_id}")

    if node_id not in kg.nodes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Node {node_id} not found",
        )

    dependencies = kg.get_dependencies(node_id, max_depth=max_depth)

    return APIResponse(success=True, data=dependencies)


@router.get(
    "/nodes/{node_id}/consumers",
    response_model=APIResponse[list[str]],
    summary="Get consumers",
    description="Get nodes that consume this node",
)
async def get_consumers(
    node_id: str,
    kg: Annotated[AgentKnowledgeGraph, Depends(get_knowledge_graph)],
) -> APIResponse[list[str]]:
    """Get node consumers."""
    logger.debug(f"Getting consumers for node: {node_id}")

    if node_id not in kg.nodes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Node {node_id} not found",
        )

    consumers = kg.get_consumers(node_id)

    return APIResponse(success=True, data=consumers)


@router.get(
    "/nodes/type/{node_type}",
    response_model=APIResponse[list[KnowledgeNodeResponse]],
    summary="Query by type",
    description="Get all nodes of a specific type",
)
async def query_by_type(
    node_type: str,
    kg: Annotated[AgentKnowledgeGraph, Depends(get_knowledge_graph)],
) -> APIResponse[list[KnowledgeNodeResponse]]:
    """Query nodes by type."""
    logger.debug(f"Querying nodes by type: {node_type}")

    try:
        node_type_enum = NodeType[node_type.upper()]
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid node type: {node_type}",
        )

    nodes = kg.query_by_type(node_type_enum)

    return APIResponse(success=True, data=[_node_to_response(n) for n in nodes])


@router.get(
    "/best-practices",
    response_model=APIResponse[list[KnowledgeNodeResponse]],
    summary="Get best practices",
    description="Get best practices, optionally filtered by topic",
)
async def get_best_practices(
    topic: str | None = Query(None, description="Filter by topic"),
    kg: Annotated[AgentKnowledgeGraph, Depends(get_knowledge_graph)],
) -> APIResponse[list[KnowledgeNodeResponse]]:
    """Get best practices."""
    logger.debug(f"Getting best practices (topic={topic})")

    practices = kg.get_best_practices(topic=topic)

    return APIResponse(success=True, data=[_node_to_response(p) for p in practices])


@router.get(
    "/statistics",
    response_model=APIResponse[dict],
    summary="Get knowledge graph statistics",
    description="Get statistics about the knowledge graph",
)
async def get_statistics(
    kg: Annotated[AgentKnowledgeGraph, Depends(get_knowledge_graph)],
) -> APIResponse[dict]:
    """Get knowledge graph statistics."""
    logger.debug("Getting knowledge graph statistics")

    stats = kg.get_statistics()

    return APIResponse(success=True, data=stats)
