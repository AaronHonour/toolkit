"""Agent API schemas."""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class CreateAgentRequest(BaseModel):
    """Request to create a new agent."""

    agent_id: str = Field(..., description="Unique agent identifier")
    persona: str = Field(..., description="Agent persona (engineer, analyst, scientist, steward)")
    team_id: Optional[str] = Field(None, description="Team ID to assign agent to")
    skills: Optional[dict[str, float]] = Field(
        None, description="Agent skills with proficiency levels (0-1)"
    )
    config: Optional[dict[str, Any]] = Field(None, description="Additional agent configuration")

    class Config:
        json_schema_extra = {
            "example": {
                "agent_id": "engineer_001",
                "persona": "engineer",
                "team_id": "data_platform",
                "skills": {"python": 0.95, "sql": 0.90, "etl": 0.85},
                "config": {"max_concurrent_tasks": 5},
            }
        }


class UpdateAgentRequest(BaseModel):
    """Request to update agent."""

    team_id: Optional[str] = Field(None, description="New team assignment")
    skills: Optional[dict[str, float]] = Field(None, description="Updated skills")
    config: Optional[dict[str, Any]] = Field(None, description="Updated configuration")

    class Config:
        json_schema_extra = {
            "example": {
                "team_id": "analytics_team",
                "skills": {"python": 0.98, "ml": 0.85},
            }
        }


class AgentResponse(BaseModel):
    """Agent response."""

    agent_id: str
    persona: str
    state: str
    team_id: Optional[str]
    skills: dict[str, float]
    current_tasks: list[str]
    completed_tasks: int
    failed_tasks: int
    messages_sent: int
    messages_received: int
    created_at: Optional[datetime] = None
    last_active: Optional[datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "agent_id": "engineer_001",
                "persona": "engineer",
                "state": "ACTIVE",
                "team_id": "data_platform",
                "skills": {"python": 0.95, "sql": 0.90},
                "current_tasks": ["task_123", "task_456"],
                "completed_tasks": 47,
                "failed_tasks": 2,
                "messages_sent": 120,
                "messages_received": 95,
                "created_at": "2024-11-14T08:00:00Z",
                "last_active": "2024-11-14T10:30:00Z",
            }
        }


class AgentListResponse(BaseModel):
    """List of agents response."""

    agents: list[AgentResponse]
    total: int
    page: int = 1
    page_size: int = 50

    class Config:
        json_schema_extra = {
            "example": {
                "agents": [
                    {
                        "agent_id": "engineer_001",
                        "persona": "engineer",
                        "state": "ACTIVE",
                        "team_id": "data_platform",
                        "skills": {"python": 0.95},
                        "current_tasks": [],
                        "completed_tasks": 47,
                        "failed_tasks": 2,
                        "messages_sent": 120,
                        "messages_received": 95,
                    }
                ],
                "total": 1,
                "page": 1,
                "page_size": 50,
            }
        }


class AgentStatsResponse(BaseModel):
    """Agent statistics response."""

    agent_id: str
    total_tasks: int
    completed_tasks: int
    failed_tasks: int
    success_rate: float
    avg_task_duration: Optional[float]
    messages_sent: int
    messages_received: int
    uptime_seconds: float
    last_active: Optional[datetime]

    class Config:
        json_schema_extra = {
            "example": {
                "agent_id": "engineer_001",
                "total_tasks": 50,
                "completed_tasks": 47,
                "failed_tasks": 2,
                "success_rate": 0.94,
                "avg_task_duration": 12.5,
                "messages_sent": 120,
                "messages_received": 95,
                "uptime_seconds": 86400.0,
                "last_active": "2024-11-14T10:30:00Z",
            }
        }
