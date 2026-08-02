"""
workflow_runner — async background task for executing FoundrAI module workflows.

Each workflow run is executed in a background FastAPI task with its own DB
session (never sharing the request-scoped session).

Public API
----------
execute_workflow(project_id, module_key, run_id, user_id, session_factory)
    The main background coroutine invoked by the trigger endpoint.

get_or_create_sse_queue(run_id)  →  asyncio.Queue
publish_sse_event(run_id, event)
    Lightweight in-memory SSE event bus keyed by run_id string.
"""

from __future__ import annotations

import asyncio
import logging
import uuid
from typing import Any

from ai.graphs.graph_factory import GraphFactory

logger = logging.getLogger(__name__)

# ── SSE queue registry ────────────────────────────────────────────────────────

_sse_queues: dict[str, asyncio.Queue] = {}


def get_or_create_sse_queue(run_id: str) -> asyncio.Queue:
    """Return (or create) the asyncio.Queue for *run_id*."""
    if run_id not in _sse_queues:
        _sse_queues[run_id] = asyncio.Queue()
    return _sse_queues[run_id]


def publish_sse_event(run_id: str, event: dict) -> None:
    """Non-blocking publish to the SSE queue for *run_id*. Silently drops if full."""
    q = _sse_queues.get(run_id)
    if q:
        try:
            q.put_nowait(event)
        except asyncio.QueueFull:
            logger.warning(
                "SSE queue full for run_id=%s — dropping event %s",
                run_id,
                event.get("event"),
            )


# ── Main background coroutine ─────────────────────────────────────────────────

async def execute_workflow(
    project_id: uuid.UUID,
    module_key: str,
    run_id: uuid.UUID,
    user_id: uuid.UUID,
    session_factory: Any,  # async_sessionmaker
) -> None:
    """
    Execute a FoundrAI AI workflow in the background.

    Steps:
    1. Open a fresh DB session (background tasks must not share the request session).
    2. Load project and upstream artifacts.
    3. Build WorkflowState via make_initial_state().
    4. Run the compiled LangGraph graph via ainvoke().
    5. Persist final status (completed / failed).
    6. Emit SSE events at key lifecycle points.

    Args:
        project_id:      UUID of the owning project.
        module_key:      One of the 8 FoundrAI module keys.
        run_id:          UUID of the workflow_run row (already created as "pending").
        user_id:         UUID of the triggering user.
        session_factory: async_sessionmaker — used to open a new session.
    """
    run_id_str = str(run_id)

    # Ensure SSE queue exists before we start so callers can subscribe early.
    get_or_create_sse_queue(run_id_str)

    async with session_factory() as session:
        try:
            # ── 1. Import service / state helpers ────────────────────────
            from app.services.workflow_service import WorkflowService
            from app.repositories.project_repository import ProjectRepository
            from app.repositories.artifact_repository import ArtifactRepository
            from app.core.constants import MODULE_DEPENDENCIES
            from ai.graphs.state import make_initial_state

            svc = WorkflowService(session)
            project_repo = ProjectRepository(session)
            artifact_repo = ArtifactRepository(session)

            # ── 2. Load project ──────────────────────────────────────────
            project = await project_repo.get_by_id(
                project_id=project_id,
                user_id=user_id,
            )
            if project is None:
                logger.error(
                    "execute_workflow: project %s not found for user %s",
                    project_id,
                    user_id,
                )
                await svc.update_status(
                    run_id=run_id,
                    project_id=project_id,
                    status="failed",
                    error_code="PROJECT_NOT_FOUND",
                    error_message=f"Project {project_id} not found",
                )
                publish_sse_event(run_id_str, {
                    "event": "run_failed",
                    "run_id": run_id_str,
                    "error": "Project not found",
                })
                return

            # ── 3. Load upstream artifacts ───────────────────────────────
            required_artifact_types = MODULE_DEPENDENCIES.get(module_key, [])
            required_artifacts: dict[str, Any] = {}
            for artifact_type in required_artifact_types:
                artifact = await artifact_repo.get_by_project_and_type(
                    project_id, artifact_type
                )
                if artifact is not None:
                    required_artifacts[artifact_type] = artifact.content_json

            # ── 4. Build initial state ───────────────────────────────────
            agent_id = GraphFactory.get_agent_id(module_key)

            state = make_initial_state(
                project_id=str(project_id),
                module_key=module_key,
                run_id=run_id_str,
                agent_id=agent_id,
                inputs={
                    "project_name": project.name,
                    "idea_brief": project.idea_brief,
                    "industry": project.industry or "",
                    "tagline": project.tagline or "",
                },
                required_artifacts=required_artifacts,
                session=session,
            )

            # ── 5. Wire persist_callback ─────────────────────────────────
            async def _persist_callback(
                artifact_type: str,
                content_json: dict,
                content_markdown: str | None = None,
                title: str | None = None,
            ) -> None:
                await svc.persist_artifact(
                    project_id=project_id,
                    module_key=module_key,
                    artifact_type=artifact_type,
                    title=title or artifact_type,
                    content_json=content_json,
                    content_markdown=content_markdown,
                    workflow_run_id=run_id,
                )

            state["persist_callback"] = _persist_callback

            # ── 6. Emit run_started SSE ──────────────────────────────────
            publish_sse_event(run_id_str, {
                "event": "run_started",
                "run_id": run_id_str,
            })

            # Mark run as running in DB
            await svc.update_status(
                run_id=run_id,
                project_id=project_id,
                status="running",
            )
            await session.commit()

            # ── 7. Execute the graph ─────────────────────────────────────
            compiled = GraphFactory.get_graph(module_key)
            result_state = await compiled.ainvoke(state)

            # ── 8. Evaluate outcome ──────────────────────────────────────
            parsed_output = result_state.get("parsed_output")
            errors: list[str] = result_state.get("errors") or []

            if parsed_output is not None:
                # Success (errors may be present from prior retries — still ok)
                await svc.update_status(
                    run_id=run_id,
                    project_id=project_id,
                    status="completed",
                )
                await session.commit()
                publish_sse_event(run_id_str, {
                    "event": "run_completed",
                    "run_id": run_id_str,
                })
                logger.info(
                    "execute_workflow: run %s completed successfully",
                    run_id_str,
                )
            else:
                # No parsed output → failed
                error_message = errors[-1] if errors else "Workflow produced no output"
                await svc.update_status(
                    run_id=run_id,
                    project_id=project_id,
                    status="failed",
                    error_code="NO_OUTPUT",
                    error_message=error_message,
                )
                await session.commit()
                publish_sse_event(run_id_str, {
                    "event": "run_failed",
                    "run_id": run_id_str,
                    "error": error_message,
                })
                logger.warning(
                    "execute_workflow: run %s failed — no parsed_output. errors=%s",
                    run_id_str,
                    errors,
                )

        except Exception as exc:  # noqa: BLE001
            logger.exception(
                "execute_workflow: unexpected error for run %s: %s",
                run_id_str,
                exc,
            )
            try:
                async with session_factory() as error_session:
                    error_svc = WorkflowService(error_session)
                    await error_svc.update_status(
                        run_id=run_id,
                        project_id=project_id,
                        status="failed",
                        error_code="UNEXPECTED_ERROR",
                        error_message=str(exc),
                    )
                    await error_session.commit()
            except Exception:  # noqa: BLE001
                logger.exception(
                    "execute_workflow: also failed to update run %s to failed",
                    run_id_str,
                )
            publish_sse_event(run_id_str, {
                "event": "run_failed",
                "run_id": run_id_str,
                "error": str(exc),
            })
