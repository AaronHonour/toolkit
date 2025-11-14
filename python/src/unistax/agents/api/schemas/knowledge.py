"""Knowledge graph API schemas."""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class AddNodeRequest(BaseModel):
    """Request to add knowledge graph node."""

    node_id: str = Field(..., description="Unique node identifier")
    node_type: str = Field(
        ...,
        description="Node type (dataset, pipeline, model, agent, task, insight, best_practice, issue)",
    )
    properties: dict[str, Any] = Field(default_factory=dict, description="Node properties")

    class Config:
        json_schema_extra = {
            "example": {
                "node_id": "customers_table",
                "node_type": "dataset",
                "properties": {
                    "table": "dim_customers",
                    "size_mb": 450,
                    "quality_score": 0.95,
                },
            }
        }


class AddEdgeRequest(BaseModel):
    """Request to add knowledge graph edge."""

    source_id: str = Field(..., description="Source node ID")
    target_id: str = Field(..., description="Target node ID")
    relation_type: str = Field(
        ...,
        description="Relation type (depends_on, produces, consumes, trained_by, executed_by, etc.)",
    )
    properties: dict[str, Any] = Field(default_factory=dict, description="Edge properties")

    class Config:
        json_schema_extra = {
            "example": {
                "source_id": "etl_pipeline_001",
                "target_id": "customers_table",
                "relation_type": "produces",
                "properties": {"frequency": "hourly"},
            }
        }


class BestPracticeRequest(BaseModel):
    """Request to add best practice."""

    practice_id: str = Field(..., description="Best practice identifier")
    topic: str = Field(..., description="Practice topic/category")
    description: str = Field(..., description="Practice description")
    related_nodes: list[str] = Field(
        default_factory=list, description="Related node IDs"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "practice_id": "bp_data_quality",
                "topic": "data_quality",
                "description": "Always validate foreign keys before loading dimension tables",
                "related_nodes": ["customers_table"],
            }
        }


class IssueRequest(BaseModel):
    """Request to record issue."""

    issue_id: str = Field(..., description="Issue identifier")
    description: str = Field(..., description="Issue description")
    severity: str = Field(..., description="Issue severity (low, medium, high, critical)")
    affected_nodes: list[str] = Field(
        default_factory=list, description="Affected node IDs"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "issue_id": "issue_001",
                "description": "Data quality degradation in customer table",
                "severity": "high",
                "affected_nodes": ["customers_table", "etl_pipeline_001"],
            }
        }


class KnowledgeNodeResponse(BaseModel):
    """Knowledge node response."""

    node_id: str
    node_type: str
    properties: dict[str, Any]
    created_by: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "node_id": "customers_table",
                "node_type": "dataset",
                "properties": {"table": "dim_customers", "size_mb": 450},
                "created_by": "steward_001",
                "created_at": "2024-11-14T08:00:00Z",
                "updated_at": "2024-11-14T10:30:00Z",
            }
        }


class KnowledgeEdgeResponse(BaseModel):
    """Knowledge edge response."""

    source_id: str
    target_id: str
    relation_type: str
    properties: dict[str, Any]
    created_by: Optional[str]
    created_at: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "source_id": "etl_pipeline_001",
                "target_id": "customers_table",
                "relation_type": "produces",
                "properties": {"frequency": "hourly"},
                "created_by": "engineer_001",
                "created_at": "2024-11-14T08:00:00Z",
            }
        }
