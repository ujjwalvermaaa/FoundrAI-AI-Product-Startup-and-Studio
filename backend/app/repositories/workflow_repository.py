"""
WorkflowRepository — all database access for workflow_runs, workflow_steps,
and agent_executions tables.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.workflow_run import WorkflowRun
from app.models.workflow_step import WorkflowStep
from app.models.agent_execution import AgentExecution


class WorkflowRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # ── WorkflowRun ────────────────────────────────────────────────────────

    async def create_run(
        self,
        project_id: uuid.UUID,
        module_key: str,
        triggered_by: uuid.UUID | None,
        input_snapshot: dict,
    ) -> WorkflowRun:
        run = WorkflowRun(
            project_id=project_id,
            module_key=module_key,
            triggered_by=triggered_by,
            input_snapshot=input_snapshot,
        )
        self._session.add(run)
        await self._session.flush()
        await self._session.refresh(run)
        return run

    async def get_run_by_id(
        self,
        run_id: uuid.UUID,
        project_id: uuid.UUID,
        include_steps: bool = False,
    ) -> Optional[WorkflowRun]:
        stmt = select(WorkflowRun).where(
            WorkflowRun.id == run_id,
            WorkflowRun.project_id == project_id,
        )
        if include_steps:
            stmt = stmt.options(selectinload(WorkflowRun.steps))
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_runs(
        self,
        project_id: uuid.UUID,
        module_key: str | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> list[WorkflowRun]:
        stmt = (
            select(WorkflowRun)
            .where(WorkflowRun.project_id == project_id)
            .order_by(WorkflowRun.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        if module_key:
            stmt = stmt.where(WorkflowRun.module_key == module_key)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_active_run(
        self,
        project_id: uuid.UUID,
        module_key: str,
    ) -> Optional[WorkflowRun]:
        """Return any pending/running run for this module (for duplicate-check)."""
        result = await self._session.execute(
            select(WorkflowRun).where(
                WorkflowRun.project_id == project_id,
                WorkflowRun.module_key == module_key,
                WorkflowRun.status.in_(["pending", "running"]),
            )
        )
        return result.scalar_one_or_none()

    async def update_status(
        self,
        run: WorkflowRun,
        status: str,
        error_code: str | None = None,
        error_message: str | None = None,
    ) -> WorkflowRun:
        run.status = status
        now = datetime.now(timezone.utc)
        if status == "running" and run.started_at is None:
            run.started_at = now
        if status in ("completed", "failed", "cancelled"):
            run.completed_at = now
        if error_code:
            run.error_code = error_code
        if error_message:
            run.error_message = error_message
        await self._session.flush()
        await self._session.refresh(run)
        return run

    # ── WorkflowStep ───────────────────────────────────────────────────────

    async def create_step(
        self,
        workflow_run_id: uuid.UUID,
        step_key: str,
        sequence: int,
        status: str = "pending",
        metadata_json: dict | None = None,
    ) -> WorkflowStep:
        step = WorkflowStep(
            workflow_run_id=workflow_run_id,
            step_key=step_key,
            sequence=sequence,
            status=status,
            metadata_json=metadata_json,
        )
        self._session.add(step)
        await self._session.flush()
        await self._session.refresh(step)
        return step

    async def update_step_status(
        self,
        step: WorkflowStep,
        status: str,
        metadata_json: dict | None = None,
    ) -> WorkflowStep:
        step.status = status
        now = datetime.now(timezone.utc)
        if status == "running" and step.started_at is None:
            step.started_at = now
        if status in ("completed", "failed"):
            step.completed_at = now
        if metadata_json is not None:
            step.metadata_json = metadata_json
        await self._session.flush()
        return step

    # ── AgentExecution ─────────────────────────────────────────────────────

    async def create_agent_execution(
        self,
        workflow_run_id: uuid.UUID,
        agent_id: str,
        model_name: str,
        status: str = "running",
        workflow_step_id: uuid.UUID | None = None,
    ) -> AgentExecution:
        execution = AgentExecution(
            workflow_run_id=workflow_run_id,
            workflow_step_id=workflow_step_id,
            agent_id=agent_id,
            model_name=model_name,
            status=status,
        )
        self._session.add(execution)
        await self._session.flush()
        await self._session.refresh(execution)
        return execution

    async def update_agent_execution(
        self,
        execution: AgentExecution,
        status: str,
        prompt_tokens: int | None = None,
        completion_tokens: int | None = None,
        latency_ms: int | None = None,
        raw_output: str | None = None,
        parsed_output_json: dict | None = None,
        error_message: str | None = None,
    ) -> AgentExecution:
        execution.status = status
        if prompt_tokens is not None:
            execution.prompt_tokens = prompt_tokens
        if completion_tokens is not None:
            execution.completion_tokens = completion_tokens
        if latency_ms is not None:
            execution.latency_ms = latency_ms
        if raw_output is not None:
            execution.raw_output = raw_output
        if parsed_output_json is not None:
            execution.parsed_output_json = parsed_output_json
        if error_message is not None:
            execution.error_message = error_message
        await self._session.flush()
        return execution
