"""Task management endpoints."""

import asyncio
import uuid
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from unistax.agents import AgentRegistry, Task, TaskStatus
from unistax.agents.api.dependencies import get_registry
from unistax.agents.api.schemas import (
    TaskListResponse,
    TaskRequest,
    TaskResponse,
    TaskStatusUpdate,
)
from unistax.api import APIResponse
from unistax.logging import get_logger

router = APIRouter(prefix="/tasks", tags=["Task Management"])
logger = get_logger(__name__)

# In-memory task storage (in production, use database)
_tasks: dict[str, dict] = {}


def _task_to_response(task_data: dict) -> TaskResponse:
    """Convert task data to response model.

    Args:
        task_data: Task data dictionary

    Returns:
        TaskResponse
    """
    return TaskResponse(
        task_id=task_data["id"],
        task_type=task_data["type"],
        description=task_data.get("description"),
        status=task_data["status"],
        priority=task_data["priority"],
        assigned_agent=task_data.get("assigned_agent"),
        result=task_data.get("result"),
        error=task_data.get("error"),
        created_at=task_data["created_at"],
        started_at=task_data.get("started_at"),
        completed_at=task_data.get("completed_at"),
        duration_seconds=task_data.get("duration_seconds"),
    )


@router.post(
    "",
    response_model=APIResponse[TaskResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Submit task",
    description="Submit a new task for execution by an agent",
)
async def submit_task(
    request: TaskRequest,
    registry: Annotated[AgentRegistry, Depends(get_registry)],
) -> APIResponse[TaskResponse]:
    """Submit a new task."""
    logger.info(f"Submitting task: type={request.task_type}, priority={request.priority}")

    # Generate task ID
    task_id = str(uuid.uuid4())

    # Create task
    task = Task(
        id=task_id,
        type=request.task_type,
        context=request.context,
        priority=request.priority,
        required_skills=request.required_skills or {},
    )

    # Find suitable agent
    assigned_agent_id = None

    if request.agent_id:
        # Specific agent requested
        if request.agent_id not in registry.agents:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent {request.agent_id} not found",
            )
        assigned_agent_id = request.agent_id
        agent = registry.agents[assigned_agent_id]
    else:
        # Find best agent
        suitable_agents = registry.find_agents_for_task(task)
        if not suitable_agents:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="No suitable agent available for this task",
            )
        # Pick agent with highest confidence
        agent = max(suitable_agents, key=lambda x: x[1])  # (agent, confidence)
        assigned_agent_id = agent[0].agent_id if isinstance(agent, tuple) else agent.agent_id

    # Store task
    task_data = {
        "id": task_id,
        "type": request.task_type,
        "description": request.description,
        "status": "pending",
        "priority": request.priority,
        "assigned_agent": assigned_agent_id,
        "result": None,
        "error": None,
        "created_at": datetime.now(),
        "started_at": None,
        "completed_at": None,
        "duration_seconds": None,
        "task_obj": task,
    }
    _tasks[task_id] = task_data

    # Assign task to agent (async execution)
    asyncio.create_task(_execute_task(task_id, assigned_agent_id, registry))

    logger.info(f"Task {task_id} submitted and assigned to {assigned_agent_id}")

    return APIResponse(
        success=True,
        data=_task_to_response(task_data),
        message=f"Task {task_id} submitted successfully",
    )


async def _execute_task(task_id: str, agent_id: str, registry: AgentRegistry):
    """Execute task asynchronously.

    Args:
        task_id: Task ID
        agent_id: Agent ID
        registry: Agent registry
    """
    task_data = _tasks.get(task_id)
    if not task_data:
        return

    agent = registry.agents.get(agent_id)
    if not agent:
        task_data["status"] = "failed"
        task_data["error"] = f"Agent {agent_id} not found"
        return

    try:
        # Update status
        task_data["status"] = "running"
        task_data["started_at"] = datetime.now()

        # Execute task
        result = await agent.execute_task(task_data["task_obj"])

        # Update completion
        task_data["status"] = "completed"
        task_data["result"] = result
        task_data["completed_at"] = datetime.now()

        if task_data["started_at"]:
            duration = (task_data["completed_at"] - task_data["started_at"]).total_seconds()
            task_data["duration_seconds"] = duration

        logger.info(f"Task {task_id} completed successfully")

    except Exception as e:
        logger.error(f"Task {task_id} failed: {e}")
        task_data["status"] = "failed"
        task_data["error"] = str(e)
        task_data["completed_at"] = datetime.now()


@router.get(
    "",
    response_model=APIResponse[TaskListResponse],
    summary="List tasks",
    description="Get list of all tasks with pagination and filtering",
)
async def list_tasks(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=200, description="Items per page"),
    status_filter: str | None = Query(None, alias="status", description="Filter by status"),
    agent_id: str | None = Query(None, description="Filter by agent ID"),
) -> APIResponse[TaskListResponse]:
    """List all tasks."""
    logger.debug(f"Listing tasks: page={page}, page_size={page_size}")

    # Get all tasks
    tasks = list(_tasks.values())

    # Apply filters
    if status_filter:
        tasks = [t for t in tasks if t["status"] == status_filter]

    if agent_id:
        tasks = [t for t in tasks if t.get("assigned_agent") == agent_id]

    # Sort by created_at (newest first)
    tasks.sort(key=lambda t: t["created_at"], reverse=True)

    # Pagination
    total = len(tasks)
    start = (page - 1) * page_size
    end = start + page_size
    page_tasks = tasks[start:end]

    return APIResponse(
        success=True,
        data=TaskListResponse(
            tasks=[_task_to_response(t) for t in page_tasks],
            total=total,
            page=page,
            page_size=page_size,
        ),
    )


@router.get(
    "/{task_id}",
    response_model=APIResponse[TaskResponse],
    summary="Get task",
    description="Get details of a specific task by ID",
)
async def get_task(task_id: str) -> APIResponse[TaskResponse]:
    """Get task by ID."""
    logger.debug(f"Getting task: {task_id}")

    task_data = _tasks.get(task_id)
    if not task_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found",
        )

    return APIResponse(success=True, data=_task_to_response(task_data))


@router.patch(
    "/{task_id}/status",
    response_model=APIResponse[TaskResponse],
    summary="Update task status",
    description="Update the status of a task (for manual intervention)",
)
async def update_task_status(
    task_id: str,
    update: TaskStatusUpdate,
) -> APIResponse[TaskResponse]:
    """Update task status."""
    logger.info(f"Updating task {task_id} status to {update.status}")

    task_data = _tasks.get(task_id)
    if not task_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found",
        )

    # Update status
    task_data["status"] = update.status

    if update.result is not None:
        task_data["result"] = update.result

    if update.error is not None:
        task_data["error"] = update.error

    if update.status in ["completed", "failed", "cancelled"]:
        task_data["completed_at"] = datetime.now()

        if task_data["started_at"]:
            duration = (task_data["completed_at"] - task_data["started_at"]).total_seconds()
            task_data["duration_seconds"] = duration

    return APIResponse(
        success=True,
        data=_task_to_response(task_data),
        message=f"Task {task_id} status updated to {update.status}",
    )


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Cancel task",
    description="Cancel a pending or running task",
)
async def cancel_task(task_id: str) -> None:
    """Cancel a task."""
    logger.info(f"Cancelling task: {task_id}")

    task_data = _tasks.get(task_id)
    if not task_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found",
        )

    if task_data["status"] in ["completed", "failed", "cancelled"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel task in {task_data['status']} state",
        )

    # Update status
    task_data["status"] = "cancelled"
    task_data["completed_at"] = datetime.now()

    logger.info(f"Task {task_id} cancelled successfully")
