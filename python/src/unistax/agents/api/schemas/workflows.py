"""Workflow API schemas."""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class WorkflowStepRequest(BaseModel):
    """Workflow step definition."""

    step_id: str = Field(..., description="Unique step identifier")
    task_type: str = Field(..., description="Task type to execute")
    context: dict[str, Any] = Field(default_factory=dict, description="Step context")
    dependencies: list[str] = Field(default_factory=list, description="Step IDs this depends on")
    agent_persona: Optional[str] = Field(None, description="Required agent persona")
    required_skills: Optional[dict[str, float]] = Field(None, description="Required skills")

    class Config:
        json_schema_extra = {
            "example": {
                "step_id": "fetch_data",
                "task_type": "fetch_data",
                "context": {"source": "customers_db"},
                "dependencies": [],
                "agent_persona": "engineer",
            }
        }


class WorkflowRequest(BaseModel):
    """Request to create workflow."""

    workflow_id: str = Field(..., description="Unique workflow identifier")
    name: str = Field(..., description="Workflow name")
    description: Optional[str] = Field(None, description="Workflow description")
    steps: list[WorkflowStepRequest] = Field(..., description="Workflow steps")

    class Config:
        json_schema_extra = {
            "example": {
                "workflow_id": "customer_analytics",
                "name": "Customer Analytics Pipeline",
                "description": "End-to-end customer data processing",
                "steps": [
                    {
                        "step_id": "fetch",
                        "task_type": "fetch_data",
                        "context": {"source": "customers_db"},
                        "dependencies": [],
                    },
                    {
                        "step_id": "clean",
                        "task_type": "clean_data",
                        "context": {},
                        "dependencies": ["fetch"],
                    },
                ],
            }
        }


class WorkflowStepResponse(BaseModel):
    """Workflow step response."""

    step_id: str
    task_type: str
    status: str
    assigned_agent: Optional[str]
    result: Optional[Any]
    error: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]

    class Config:
        json_schema_extra = {
            "example": {
                "step_id": "fetch_data",
                "task_type": "fetch_data",
                "status": "completed",
                "assigned_agent": "engineer_001",
                "result": {"rows": 10000, "status": "success"},
                "error": None,
                "started_at": "2024-11-14T08:00:00Z",
                "completed_at": "2024-11-14T08:01:30Z",
            }
        }


class WorkflowResponse(BaseModel):
    """Workflow response."""

    workflow_id: str
    name: str
    description: Optional[str]
    status: str
    steps: list[WorkflowStepResponse]
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    duration_seconds: Optional[float]

    class Config:
        json_schema_extra = {
            "example": {
                "workflow_id": "customer_analytics",
                "name": "Customer Analytics Pipeline",
                "status": "running",
                "steps": [
                    {
                        "step_id": "fetch",
                        "task_type": "fetch_data",
                        "status": "completed",
                        "assigned_agent": "engineer_001",
                    }
                ],
                "created_at": "2024-11-14T08:00:00Z",
                "started_at": "2024-11-14T08:00:05Z",
                "completed_at": None,
                "duration_seconds": None,
            }
        }


class WorkflowStatusResponse(BaseModel):
    """Workflow status response."""

    workflow_id: str
    status: str
    completed_steps: int
    total_steps: int
    progress_percent: float
    current_steps: list[str]

    class Config:
        json_schema_extra = {
            "example": {
                "workflow_id": "customer_analytics",
                "status": "running",
                "completed_steps": 2,
                "total_steps": 5,
                "progress_percent": 40.0,
                "current_steps": ["clean_data", "transform_data"],
            }
        }
