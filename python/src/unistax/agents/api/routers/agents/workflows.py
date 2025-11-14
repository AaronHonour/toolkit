"""Workflow orchestration endpoints."""

from datetime import datetime
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status

from unistax.agents import Task
from unistax.agents.api.dependencies import get_orchestrator
from unistax.agents.api.schemas import (
    WorkflowRequest,
    WorkflowResponse,
    WorkflowStatusResponse,
    WorkflowStepResponse,
)
from unistax.agents.orchestrator import AgentOrchestrator, Workflow, WorkflowStep
from unistax.api import APIResponse
from unistax.logging import get_logger

router = APIRouter(prefix="/workflows", tags=["Workflow Orchestration"])
logger = get_logger(__name__)

# In-memory workflow storage
_workflows: dict[str, Workflow] = {}


def _workflow_to_response(workflow: Workflow, orch: AgentOrchestrator) -> WorkflowResponse:
    """Convert workflow to response model.

    Args:
        workflow: Workflow instance
        orch: Orchestrator instance

    Returns:
        WorkflowResponse
    """
    steps = []
    for step in workflow.steps:
        step_resp = WorkflowStepResponse(
            step_id=step.id,
            task_type=step.task.type,
            status=step.status.value,
            assigned_agent=step.assigned_agent,
            result=step.result,
            error=step.error,
            started_at=None,  # Would need to track
            completed_at=None,
        )
        steps.append(step_resp)

    # Calculate duration
    duration = None
    if workflow.status.value == "completed" and workflow.steps:
        # Simple duration calculation
        duration = 0.0

    return WorkflowResponse(
        workflow_id=workflow.id,
        name=workflow.id,  # Using ID as name for now
        description=None,
        status=workflow.status.value,
        steps=steps,
        created_at=datetime.now(),
        started_at=datetime.now() if workflow.status.value != "pending" else None,
        completed_at=datetime.now() if workflow.status.value == "completed" else None,
        duration_seconds=duration,
    )


@router.post(
    "",
    response_model=APIResponse[WorkflowResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create workflow",
    description="Create and execute a multi-agent workflow",
)
async def create_workflow(
    request: WorkflowRequest,
    orchestrator: Annotated[AgentOrchestrator, Depends(get_orchestrator)],
) -> APIResponse[WorkflowResponse]:
    """Create and execute workflow."""
    logger.info(f"Creating workflow: {request.workflow_id}")

    # Check if workflow exists
    if request.workflow_id in _workflows:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Workflow {request.workflow_id} already exists",
        )

    # Create workflow
    workflow = Workflow(id=request.workflow_id)

    # Add steps
    for step_req in request.steps:
        task = Task(
            id=step_req.step_id,
            type=step_req.task_type,
            context=step_req.context,
            required_skills=step_req.required_skills or {},
        )

        step = WorkflowStep(
            id=step_req.step_id,
            task=task,
            dependencies=step_req.dependencies,
            agent_persona=step_req.agent_persona,
            required_skills=step_req.required_skills,
        )

        workflow.add_step(step)

    # Store workflow
    _workflows[workflow.id] = workflow

    # Execute workflow asynchronously (in production, use background task)
    # For now, just store it
    # await orchestrator.execute_workflow(workflow)

    logger.info(f"Workflow {workflow.id} created successfully")

    return APIResponse(
        success=True,
        data=_workflow_to_response(workflow, orchestrator),
        message=f"Workflow {workflow.id} created successfully",
    )


@router.get(
    "/{workflow_id}",
    response_model=APIResponse[WorkflowResponse],
    summary="Get workflow",
    description="Get details of a specific workflow",
)
async def get_workflow(
    workflow_id: str,
    orchestrator: Annotated[AgentOrchestrator, Depends(get_orchestrator)],
) -> APIResponse[WorkflowResponse]:
    """Get workflow by ID."""
    logger.debug(f"Getting workflow: {workflow_id}")

    workflow = _workflows.get(workflow_id)
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow {workflow_id} not found",
        )

    return APIResponse(success=True, data=_workflow_to_response(workflow, orchestrator))


@router.get(
    "/{workflow_id}/status",
    response_model=APIResponse[WorkflowStatusResponse],
    summary="Get workflow status",
    description="Get current status and progress of a workflow",
)
async def get_workflow_status(workflow_id: str) -> APIResponse[WorkflowStatusResponse]:
    """Get workflow status."""
    logger.debug(f"Getting workflow status: {workflow_id}")

    workflow = _workflows.get(workflow_id)
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow {workflow_id} not found",
        )

    # Count completed steps
    completed = sum(1 for step in workflow.steps if step.status.value == "completed")
    total = len(workflow.steps)

    # Get current steps
    current_steps = [
        step.id for step in workflow.steps if step.status.value in ["ready", "running"]
    ]

    status_response = WorkflowStatusResponse(
        workflow_id=workflow.id,
        status=workflow.status.value,
        completed_steps=completed,
        total_steps=total,
        progress_percent=(completed / total * 100) if total > 0 else 0.0,
        current_steps=current_steps,
    )

    return APIResponse(success=True, data=status_response)


@router.post(
    "/{workflow_id}/execute",
    response_model=APIResponse[WorkflowResponse],
    summary="Execute workflow",
    description="Start execution of a created workflow",
)
async def execute_workflow(
    workflow_id: str,
    orchestrator: Annotated[AgentOrchestrator, Depends(get_orchestrator)],
) -> APIResponse[WorkflowResponse]:
    """Execute workflow."""
    logger.info(f"Executing workflow: {workflow_id}")

    workflow = _workflows.get(workflow_id)
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow {workflow_id} not found",
        )

    # Execute workflow (async)
    try:
        await orchestrator.execute_workflow(workflow)
        logger.info(f"Workflow {workflow_id} execution started")
    except Exception as e:
        logger.error(f"Failed to execute workflow {workflow_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to execute workflow: {str(e)}",
        )

    return APIResponse(
        success=True,
        data=_workflow_to_response(workflow, orchestrator),
        message=f"Workflow {workflow_id} executed successfully",
    )


@router.delete(
    "/{workflow_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete workflow",
    description="Delete a workflow",
)
async def delete_workflow(workflow_id: str) -> None:
    """Delete workflow."""
    logger.info(f"Deleting workflow: {workflow_id}")

    if workflow_id not in _workflows:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow {workflow_id} not found",
        )

    del _workflows[workflow_id]

    logger.info(f"Workflow {workflow_id} deleted successfully")
