"""Metrics API schemas."""

from typing import Any, Optional

from pydantic import BaseModel, Field


class AgentMetricsResponse(BaseModel):
    """Agent-specific metrics."""

    agent_id: str
    uptime_seconds: float
    total_tasks: int
    completed_tasks: int
    failed_tasks: int
    success_rate: float
    avg_task_duration: Optional[float]
    current_task_count: int
    messages_sent: int
    messages_received: int
    collaboration_count: int
    last_active_timestamp: Optional[float]

    class Config:
        json_schema_extra = {
            "example": {
                "agent_id": "engineer_001",
                "uptime_seconds": 86400.0,
                "total_tasks": 50,
                "completed_tasks": 47,
                "failed_tasks": 2,
                "success_rate": 0.94,
                "avg_task_duration": 12.5,
                "current_task_count": 1,
                "messages_sent": 120,
                "messages_received": 95,
                "collaboration_count": 15,
                "last_active_timestamp": 1699958400.0,
            }
        }


class SystemMetricsResponse(BaseModel):
    """System-wide metrics."""

    total_agents: int
    active_agents: int
    idle_agents: int
    busy_agents: int
    total_teams: int
    total_tasks: int
    pending_tasks: int
    running_tasks: int
    completed_tasks: int
    failed_tasks: int
    total_workflows: int
    running_workflows: int
    knowledge_nodes: int
    knowledge_edges: int
    system_uptime: float
    avg_task_duration: Optional[float]
    overall_success_rate: float
    messages_per_second: float

    class Config:
        json_schema_extra = {
            "example": {
                "total_agents": 10,
                "active_agents": 8,
                "idle_agents": 2,
                "busy_agents": 6,
                "total_teams": 3,
                "total_tasks": 500,
                "pending_tasks": 5,
                "running_tasks": 8,
                "completed_tasks": 470,
                "failed_tasks": 17,
                "total_workflows": 25,
                "running_workflows": 3,
                "knowledge_nodes": 250,
                "knowledge_edges": 480,
                "system_uptime": 604800.0,
                "avg_task_duration": 15.3,
                "overall_success_rate": 0.966,
                "messages_per_second": 2.5,
            }
        }


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(..., description="Health status (healthy, degraded, unhealthy)")
    timestamp: float
    version: str
    agents_healthy: int
    agents_total: int
    details: Optional[dict[str, Any]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "timestamp": 1699958400.0,
                "version": "1.0.0",
                "agents_healthy": 10,
                "agents_total": 10,
                "details": {"registry": "connected", "event_bus": "active"},
            }
        }
