"""Task API schemas."""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class TaskRequest(BaseModel):
    """Request to create/assign a task."""

    task_type: str = Field(..., description="Type of task to perform")
    description: Optional[str] = Field(None, description="Task description")
    context: dict[str, Any] = Field(default_factory=dict, description="Task context/parameters")
    priority: int = Field(5, ge=1, le=10, description="Task priority (1-10)")
    required_skills: Optional[dict[str, float]] = Field(
        None, description="Required skills with minimum proficiency"
    )
    agent_id: Optional[str] = Field(
        None, description="Specific agent ID (if not provided, auto-assigned)"
    )
    timeout_seconds: Optional[int] = Field(None, description="Task timeout in seconds")

    class Config:
        json_schema_extra = {
            "example": {
                "task_type": "build_pipeline",
                "description": "Create customer analytics ETL pipeline",
                "context": {
                    "source": "customers_db",
                    "target": "warehouse",
                    "transformations": ["clean", "dedupe", "enrich"],
                },
                "priority": 8,
                "required_skills": {"sql": 0.7, "etl": 0.8},
                "timeout_seconds": 3600,
            }
        }


class TaskResponse(BaseModel):
    """Task response."""

    task_id: str
    task_type: str
    description: Optional[str]
    status: str
    priority: int
    assigned_agent: Optional[str]
    result: Optional[Any]
    error: Optional[str]
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    duration_seconds: Optional[float]

    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "task_abc123",
                "task_type": "build_pipeline",
                "description": "Create customer analytics ETL pipeline",
                "status": "completed",
                "priority": 8,
                "assigned_agent": "engineer_001",
                "result": {
                    "pipeline_id": "customer_etl_v1",
                    "status": "deployed",
                    "endpoint": "/pipelines/customer_etl_v1",
                },
                "error": None,
                "created_at": "2024-11-14T08:00:00Z",
                "started_at": "2024-11-14T08:00:05Z",
                "completed_at": "2024-11-14T08:15:30Z",
                "duration_seconds": 925.0,
            }
        }


class TaskListResponse(BaseModel):
    """List of tasks response."""

    tasks: list[TaskResponse]
    total: int
    page: int = 1
    page_size: int = 50

    class Config:
        json_schema_extra = {
            "example": {
                "tasks": [
                    {
                        "task_id": "task_abc123",
                        "task_type": "build_pipeline",
                        "status": "completed",
                        "priority": 8,
                        "assigned_agent": "engineer_001",
                        "created_at": "2024-11-14T08:00:00Z",
                    }
                ],
                "total": 1,
                "page": 1,
                "page_size": 50,
            }
        }


class TaskStatusUpdate(BaseModel):
    """Task status update."""

    status: str = Field(..., description="New task status")
    result: Optional[Any] = Field(None, description="Task result")
    error: Optional[str] = Field(None, description="Error message if failed")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "completed",
                "result": {"pipeline_id": "customer_etl_v1", "status": "deployed"},
            }
        }
