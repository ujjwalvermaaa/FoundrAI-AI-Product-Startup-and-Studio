"""
Workflow API endpoints — /api/v1/projects/{project_id}/workflows/*

POST /projects/{pid}/workflows/{module_key}/run          → 202  Trigger workflow
GET  /projects/{pid}/workflows/runs                      → 200  Paginated run list
GET  /projects/{pid}/workflows/runs/{run_id}             → 200  Run detail with steps
POST /projects/{pid}/workflows/runs/{run_id}/cancel      → 200  Cancel run
GET  /projects/{pid}/workflows/runs/{run_id}/stream      → SSE  Live event stream
"""

import asyncio
import json
import uuid
from typing import AsyncGenerator

from fastapi import APIRouter, BackgroundTasks, Depends, Query, Request, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.database.session import get_db, get_session_factory
from app.models.user import User
from app.schemas.workflow import (
    TriggerWorkflowResponse,
    WorkflowRunDetailResponse,
    WorkflowRunListResponse,
    WorkflowRunResponse,
)
from app.services.workflow_service import WorkflowService

router = APIRouter(
    prefix="/projects/{project_id}/workflows",
    tags=["Workflows"],
)


# ── Trigger ────────────────────────────────────────────────────────────────────

@router.post(
    "/{module_key}/run",
    response_model=TriggerWorkflowResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Trigger a workflow for a module",
)
async def trigger_workflow(
    project_id: uuid.UUID,
    module_key: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db),
) -> TriggerWorkflowResponse:
    """
    Trigger the AI workflow for a module.

    - Returns 202 immediately with run_id and SSE stream_url.
    - Returns 409 if a run is already pending/running.
    - Returns 409 if required upstream artifacts are missing.
    - Returns 404 if module_key is invalid.
    """
    svc = WorkflowService(session)
    response = await svc.trigger(
        project_id=project_id,
        module_key=module_key,
        user_id=current_user.id,
    )

    # Launch background execution with its own DB session
    from app.background.workflow_runner import execute_workflow
    background_tasks.add_task(
        execute_workflow,
        project_id=project_id,
        module_key=module_key,
        run_id=response.run_id,
        user_id=current_user.id,
        session_factory=get_session_factory(),
    )

    return response


# ── List runs ──────────────────────────────────────────────────────────────────

@router.get(
    "/runs",
    response_model=WorkflowRunListResponse,
    status_code=status.HTTP_200_OK,
    summary="List workflow runs for a project",
)
async def list_runs(
    project_id: uuid.UUID,
    module_key: str | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db),
) -> WorkflowRunListResponse:
    """Return paginated workflow runs. Optionally filter by module_key."""
    svc = WorkflowService(session)
    return await svc.list_runs(
        project_id=project_id,
        user_id=current_user.id,
        module_key=module_key,
        skip=skip,
        limit=limit,
    )


# ── Get run detail ─────────────────────────────────────────────────────────────

@router.get(
    "/runs/{run_id}",
    response_model=WorkflowRunDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Get workflow run detail with steps",
)
async def get_run(
    project_id: uuid.UUID,
    run_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db),
) -> WorkflowRunDetailResponse:
    """Return full run detail including all workflow steps."""
    svc = WorkflowService(session)
    return await svc.get_run(
        project_id=project_id,
        run_id=run_id,
        user_id=current_user.id,
    )


# ── Cancel ─────────────────────────────────────────────────────────────────────

@router.post(
    "/runs/{run_id}/cancel",
    response_model=WorkflowRunResponse,
    status_code=status.HTTP_200_OK,
    summary="Cancel a workflow run",
)
async def cancel_run(
    project_id: uuid.UUID,
    run_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db),
) -> WorkflowRunResponse:
    """
    Cancel a pending or running workflow.
    Returns 409 if the run is already in a terminal state.
    """
    svc = WorkflowService(session)
    return await svc.cancel(
        project_id=project_id,
        run_id=run_id,
        user_id=current_user.id,
    )


# ── SSE stream ─────────────────────────────────────────────────────────────────

def _sse_event(event: str, data: dict) -> str:
    """Format a single SSE message."""
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


async def _workflow_event_stream(
    project_id: uuid.UUID,
    run_id: uuid.UUID,
    session: AsyncSession,
) -> AsyncGenerator[str, None]:
    """
    Stream workflow run status events.

    Polls the run status every 0.5 seconds and emits:
    - step_started   when a step transitions to running
    - step_completed when a step transitions to completed/failed
    - run_completed  when the run reaches completed
    - run_failed     when the run reaches failed or cancelled

    The stream closes when the run reaches a terminal state or
    after a 10-minute timeout.
    """
    from app.repositories.workflow_repository import WorkflowRepository

    repo = WorkflowRepository(session)
    seen_step_statuses: dict[str, str] = {}
    timeout_seconds = 600  # 10 minutes max
    elapsed = 0.0
    poll_interval = 0.5

    # Send initial connection event
    yield _sse_event("connected", {"run_id": str(run_id)})

    while elapsed < timeout_seconds:
        await asyncio.sleep(poll_interval)
        elapsed += poll_interval

        run = await repo.get_run_by_id(run_id, project_id, include_steps=True)
        if run is None:
            yield _sse_event("error", {"message": "Run not found"})
            return

        # Emit step events for status changes
        for step in run.steps:
            prev = seen_step_statuses.get(str(step.id))
            if step.status != prev:
                seen_step_statuses[str(step.id)] = step.status
                if step.status == "running":
                    yield _sse_event("step_started", {
                        "step_id": str(step.id),
                        "step_key": step.step_key,
                        "sequence": step.sequence,
                    })
                elif step.status in ("completed", "failed"):
                    yield _sse_event("step_completed", {
                        "step_id": str(step.id),
                        "step_key": step.step_key,
                        "status": step.status,
                        "sequence": step.sequence,
                    })

        # Terminal states — emit final event and close
        if run.status == "completed":
            yield _sse_event("run_completed", {
                "run_id": str(run.id),
                "module_key": run.module_key,
                "completed_at": run.completed_at.isoformat() if run.completed_at else None,
            })
            return

        if run.status in ("failed", "cancelled"):
            yield _sse_event("run_failed", {
                "run_id": str(run.id),
                "module_key": run.module_key,
                "status": run.status,
                "error_code": run.error_code,
                "error_message": run.error_message,
            })
            return

    # Timeout
    yield _sse_event("timeout", {"message": "Stream timed out after 10 minutes"})


@router.get(
    "/runs/{run_id}/stream",
    summary="SSE stream for live workflow progress",
    response_class=StreamingResponse,
)
async def stream_run(
    project_id: uuid.UUID,
    run_id: uuid.UUID,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db),
) -> StreamingResponse:
    """
    Server-Sent Events stream for a workflow run.

    Events emitted:
    - `connected`      — stream opened
    - `step_started`   — a step began execution
    - `step_completed` — a step finished (with status)
    - `run_completed`  — workflow succeeded
    - `run_failed`     — workflow failed or was cancelled
    - `timeout`        — stream closed after 10 min inactivity
    - `error`          — run not found

    Connect with: `EventSource('/api/v1/projects/{id}/workflows/runs/{run_id}/stream')`
    """
    # Verify ownership before opening stream
    svc = WorkflowService(session)
    await svc.get_run(
        project_id=project_id,
        run_id=run_id,
        user_id=current_user.id,
    )

    return StreamingResponse(
        _workflow_event_stream(project_id, run_id, session),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
