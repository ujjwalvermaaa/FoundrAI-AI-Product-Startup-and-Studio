"""
WorkflowService — business logic for triggering, cancelling, and tracking
workflow runs.

Key responsibilities:
- Validate module dependencies before triggering
- Enforce one-active-run-per-module constraint
- Manage state transitions: pending → running → completed | failed | cancelled
- Provide an `persist_artifact` callback for AI layer to save artifacts
"""

import uuid
from typing import Any, Callable, Coroutine

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import (
    MODULE_DEPENDENCIES,
    MODULE_STATUS_AVAILABLE,
    MODULE_STATUS_COMPLETED,
    MODULE_STATUS_FAILED,
    MODULE_STATUS_IN_PROGRESS,
    WORKFLOW_STATUS_CANCELLED,
    WORKFLOW_STATUS_COMPLETED,
    WORKFLOW_STATUS_FAILED,
    WORKFLOW_STATUS_PENDING,
    WORKFLOW_STATUS_RUNNING,
)
from app.core.exceptions import (
    ModuleDependencyNotMetError,
    ModuleNotFoundError,
    ProjectNotFoundError,
    WorkflowAlreadyRunningError,
    WorkflowNotCancellableError,
)
from app.repositories.artifact_repository import ArtifactRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.workflow_repository import WorkflowRepository
from app.schemas.workflow import (
    TriggerWorkflowResponse,
    WorkflowRunDetailResponse,
    WorkflowRunListResponse,
    WorkflowRunResponse,
)


class WorkflowService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._repo = WorkflowRepository(session)
        self._project_repo = ProjectRepository(session)
        self._artifact_repo = ArtifactRepository(session)

    async def _assert_project_owned(
        self, project_id: uuid.UUID, user_id: uuid.UUID
    ) -> None:
        project = await self._project_repo.get_by_id(
            project_id=project_id, user_id=user_id
        )
        if not project:
            raise ProjectNotFoundError(str(project_id))

    async def _check_dependencies(
        self, project_id: uuid.UUID, module_key: str
    ) -> None:
        """
        Verify all required upstream artifacts exist.
        Raises ModuleDependencyNotMetError with the list of missing types.
        """
        required_types = MODULE_DEPENDENCIES.get(module_key, [])
        if not required_types:
            return  # No dependencies

        missing: list[str] = []
        for artifact_type in required_types:
            artifact = await self._artifact_repo.get_by_project_and_type(
                project_id, artifact_type
            )
            if artifact is None:
                missing.append(artifact_type)

        if missing:
            raise ModuleDependencyNotMetError(missing)

    # ── Trigger ────────────────────────────────────────────────────────────

    async def trigger(
        self,
        project_id: uuid.UUID,
        module_key: str,
        user_id: uuid.UUID,
        input_snapshot: dict | None = None,
    ) -> TriggerWorkflowResponse:
        """
        Validate and create a new workflow run (status=pending).
        The actual execution is handled by the background task layer (Task 38).

        Raises:
            ProjectNotFoundError: Project not found or not owned.
            ModuleNotFoundError: Invalid module_key.
            ModuleDependencyNotMetError: Required upstream artifacts missing.
            WorkflowAlreadyRunningError: A run is already pending/running.
        """
        await self._assert_project_owned(project_id, user_id)

        # Validate module_key
        from app.core.constants import MODULE_KEYS
        if module_key not in MODULE_KEYS:
            raise ModuleNotFoundError(module_key)

        # Check dependencies
        await self._check_dependencies(project_id, module_key)

        # Check for active run
        active = await self._repo.get_active_run(project_id, module_key)
        if active:
            raise WorkflowAlreadyRunningError(module_key)

        # Create the run
        run = await self._repo.create_run(
            project_id=project_id,
            module_key=module_key,
            triggered_by=user_id,
            input_snapshot=input_snapshot or {},
        )

        # Update module status → in_progress
        module = await self._project_repo.get_module(project_id, module_key)
        if module:
            module.status = MODULE_STATUS_IN_PROGRESS
            module.last_run_id = run.id
            await self._session.flush()

        # Fire-and-continue: write audit log
        try:
            from app.repositories.audit_repository import AuditRepository
            audit_repo = AuditRepository()
            await audit_repo.create(
                session=self._session,
                event_type="workflow.trigger",
                user_id=user_id,
                resource_type="workflow_run",
                resource_id=run.id,
                metadata={"module_key": module_key, "project_id": str(project_id)},
            )
        except Exception as exc:
            import logging
            logging.getLogger(__name__).warning("Audit log failed for workflow.trigger: %s", exc)

        return TriggerWorkflowResponse(
            run_id=run.id,
            status=run.status,
            stream_url=f"/api/v1/projects/{project_id}/workflows/runs/{run.id}/stream",
        )

    # ── Cancel ─────────────────────────────────────────────────────────────

    async def cancel(
        self,
        project_id: uuid.UUID,
        run_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> WorkflowRunResponse:
        """
        Cancel a pending or running workflow run.

        Raises:
            WorkflowNotCancellableError: If run is already terminal.
        """
        await self._assert_project_owned(project_id, user_id)

        run = await self._repo.get_run_by_id(run_id, project_id)
        if not run:
            raise ProjectNotFoundError(str(run_id))

        if run.status not in (WORKFLOW_STATUS_PENDING, WORKFLOW_STATUS_RUNNING):
            raise WorkflowNotCancellableError()

        updated = await self._repo.update_status(run, WORKFLOW_STATUS_CANCELLED)

        # Reset module status back to available
        module = await self._project_repo.get_module(project_id, run.module_key)
        if module and module.status == MODULE_STATUS_IN_PROGRESS:
            module.status = MODULE_STATUS_AVAILABLE
            await self._session.flush()

        return WorkflowRunResponse.model_validate(updated)

    # ── Status updates (called by AI execution layer) ─────────────────────

    async def update_status(
        self,
        run_id: uuid.UUID,
        project_id: uuid.UUID,
        status: str,
        error_code: str | None = None,
        error_message: str | None = None,
    ) -> WorkflowRunResponse:
        """Internal: update run status and sync module status."""
        run = await self._repo.get_run_by_id(run_id, project_id)
        if not run:
            raise ProjectNotFoundError(str(run_id))

        updated = await self._repo.update_status(
            run, status,
            error_code=error_code,
            error_message=error_message,
        )

        # Sync module status
        module = await self._project_repo.get_module(project_id, run.module_key)
        if module:
            if status == WORKFLOW_STATUS_COMPLETED:
                from datetime import datetime, timezone
                module.status = MODULE_STATUS_COMPLETED
                module.completed_at = datetime.now(timezone.utc)
            elif status == WORKFLOW_STATUS_FAILED:
                module.status = MODULE_STATUS_FAILED
            await self._session.flush()

        return WorkflowRunResponse.model_validate(updated)

    async def persist_artifact(
        self,
        project_id: uuid.UUID,
        module_key: str,
        artifact_type: str,
        title: str,
        content_json: dict,
        content_markdown: str | None,
        workflow_run_id: uuid.UUID,
    ) -> None:
        """
        Callback used by AI execution layer to save an artifact after generation.
        Calls ArtifactService.upsert_artifact internally.
        """
        from app.services.artifact_service import ArtifactService
        artifact_svc = ArtifactService(self._session)
        await artifact_svc.upsert_artifact(
            project_id=project_id,
            module_key=module_key,
            artifact_type=artifact_type,
            title=title,
            content_json=content_json,
            content_markdown=content_markdown,
            source="ai",
            workflow_run_id=workflow_run_id,
        )

    # ── Read ──────────────────────────────────────────────────────────────

    async def list_runs(
        self,
        project_id: uuid.UUID,
        user_id: uuid.UUID,
        module_key: str | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> WorkflowRunListResponse:
        await self._assert_project_owned(project_id, user_id)
        runs = await self._repo.list_runs(
            project_id=project_id,
            module_key=module_key,
            skip=skip,
            limit=limit,
        )
        from sqlalchemy import select, func
        from app.models.workflow_run import WorkflowRun as WR
        stmt = select(func.count(WR.id)).where(WR.project_id == project_id)
        if module_key:
            stmt = stmt.where(WR.module_key == module_key)
        result = await self._session.execute(stmt)
        total = result.scalar_one()
        return WorkflowRunListResponse(
            items=[WorkflowRunResponse.model_validate(r) for r in runs],
            total=total,
            skip=skip,
            limit=limit,
        )

    async def get_run(
        self,
        project_id: uuid.UUID,
        run_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> WorkflowRunDetailResponse:
        await self._assert_project_owned(project_id, user_id)
        run = await self._repo.get_run_by_id(
            run_id, project_id, include_steps=True
        )
        if not run:
            raise ProjectNotFoundError(str(run_id))
        return WorkflowRunDetailResponse.model_validate(run)
