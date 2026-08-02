"""
Unit tests for WorkflowService — trigger, cancel, state transitions,
dependency gates.
"""

import uuid

import pytest

from app.core.constants import (
    MODULE_STATUS_AVAILABLE,
    MODULE_STATUS_COMPLETED,
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
from app.repositories.user_repository import UserRepository
from app.schemas.project import CreateProjectRequest
from app.services.artifact_service import ArtifactService
from app.services.project_service import ProjectService
from app.services.workflow_service import WorkflowService


async def _setup(db_session):
    """Create a user + project and return (user_id, project_id)."""
    user_repo = UserRepository(db_session)
    user = await user_repo.create("wf@test.com", "hash", "WF User")
    svc = ProjectService(db_session)
    project = await svc.create_project(
        user_id=user.id,
        data=CreateProjectRequest(
            name="WF Test",
            idea_brief="Testing workflow state transitions and dependency gates.",
        ),
    )
    return user.id, project.id


# ── Trigger ───────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_trigger_first_module_succeeds(db_session):
    """idea_validation has no deps — should trigger immediately."""
    user_id, project_id = await _setup(db_session)
    svc = WorkflowService(db_session)
    result = await svc.trigger(
        project_id=project_id,
        module_key="idea_validation",
        user_id=user_id,
    )
    assert result.run_id is not None
    assert result.status == WORKFLOW_STATUS_PENDING


@pytest.mark.asyncio
async def test_trigger_sets_module_in_progress(db_session):
    user_id, project_id = await _setup(db_session)
    wf_svc = WorkflowService(db_session)
    await wf_svc.trigger(project_id=project_id, module_key="idea_validation", user_id=user_id)

    from app.repositories.project_repository import ProjectRepository
    repo = ProjectRepository(db_session)
    module = await repo.get_module(project_id, "idea_validation")
    assert module is not None
    assert module.status == MODULE_STATUS_IN_PROGRESS


@pytest.mark.asyncio
async def test_trigger_invalid_module_raises(db_session):
    user_id, project_id = await _setup(db_session)
    svc = WorkflowService(db_session)
    with pytest.raises(ModuleNotFoundError):
        await svc.trigger(
            project_id=project_id,
            module_key="nonexistent_module",
            user_id=user_id,
        )


@pytest.mark.asyncio
async def test_trigger_wrong_user_raises(db_session):
    _, project_id = await _setup(db_session)
    svc = WorkflowService(db_session)
    with pytest.raises(ProjectNotFoundError):
        await svc.trigger(
            project_id=project_id,
            module_key="idea_validation",
            user_id=uuid.uuid4(),
        )


# ── Dependency gate ───────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_trigger_missing_dependency_raises(db_session):
    """market_research requires validation_report — should fail without it."""
    user_id, project_id = await _setup(db_session)
    svc = WorkflowService(db_session)
    with pytest.raises(ModuleDependencyNotMetError) as exc_info:
        await svc.trigger(
            project_id=project_id,
            module_key="market_research",
            user_id=user_id,
        )
    assert "validation_report" in exc_info.value.details["missing_artifacts"]


@pytest.mark.asyncio
async def test_trigger_with_dependency_satisfied(db_session):
    """market_research should trigger once validation_report exists."""
    user_id, project_id = await _setup(db_session)

    # Seed the required artifact
    art_svc = ArtifactService(db_session)
    await art_svc.upsert_artifact(
        project_id=project_id,
        module_key="idea_validation",
        artifact_type="validation_report",
        title="v1",
        content_json={"score": 80},
    )

    wf_svc = WorkflowService(db_session)
    result = await wf_svc.trigger(
        project_id=project_id,
        module_key="market_research",
        user_id=user_id,
    )
    assert result.run_id is not None


# ── Duplicate run prevention ──────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_trigger_duplicate_raises(db_session):
    user_id, project_id = await _setup(db_session)
    svc = WorkflowService(db_session)
    await svc.trigger(project_id=project_id, module_key="idea_validation", user_id=user_id)
    with pytest.raises(WorkflowAlreadyRunningError):
        await svc.trigger(project_id=project_id, module_key="idea_validation", user_id=user_id)


# ── Cancel ────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_cancel_pending_run(db_session):
    user_id, project_id = await _setup(db_session)
    svc = WorkflowService(db_session)
    triggered = await svc.trigger(project_id=project_id, module_key="idea_validation", user_id=user_id)
    result = await svc.cancel(project_id=project_id, run_id=triggered.run_id, user_id=user_id)
    assert result.status == WORKFLOW_STATUS_CANCELLED


@pytest.mark.asyncio
async def test_cancel_resets_module_status(db_session):
    user_id, project_id = await _setup(db_session)
    svc = WorkflowService(db_session)
    triggered = await svc.trigger(project_id=project_id, module_key="idea_validation", user_id=user_id)
    await svc.cancel(project_id=project_id, run_id=triggered.run_id, user_id=user_id)

    from app.repositories.project_repository import ProjectRepository
    repo = ProjectRepository(db_session)
    module = await repo.get_module(project_id, "idea_validation")
    assert module is not None
    assert module.status == MODULE_STATUS_AVAILABLE


@pytest.mark.asyncio
async def test_cancel_completed_run_raises(db_session):
    user_id, project_id = await _setup(db_session)
    svc = WorkflowService(db_session)
    triggered = await svc.trigger(project_id=project_id, module_key="idea_validation", user_id=user_id)
    # Complete the run first
    await svc.update_status(triggered.run_id, project_id, WORKFLOW_STATUS_COMPLETED)
    with pytest.raises(WorkflowNotCancellableError):
        await svc.cancel(project_id=project_id, run_id=triggered.run_id, user_id=user_id)


# ── State transitions ─────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_status_transition_pending_to_running(db_session):
    user_id, project_id = await _setup(db_session)
    svc = WorkflowService(db_session)
    triggered = await svc.trigger(project_id=project_id, module_key="idea_validation", user_id=user_id)
    result = await svc.update_status(triggered.run_id, project_id, WORKFLOW_STATUS_RUNNING)
    assert result.status == WORKFLOW_STATUS_RUNNING
    assert result.started_at is not None


@pytest.mark.asyncio
async def test_status_transition_running_to_completed(db_session):
    user_id, project_id = await _setup(db_session)
    svc = WorkflowService(db_session)
    triggered = await svc.trigger(project_id=project_id, module_key="idea_validation", user_id=user_id)
    await svc.update_status(triggered.run_id, project_id, WORKFLOW_STATUS_RUNNING)
    result = await svc.update_status(triggered.run_id, project_id, WORKFLOW_STATUS_COMPLETED)
    assert result.status == WORKFLOW_STATUS_COMPLETED
    assert result.completed_at is not None


@pytest.mark.asyncio
async def test_completed_sets_module_completed(db_session):
    user_id, project_id = await _setup(db_session)
    svc = WorkflowService(db_session)
    triggered = await svc.trigger(project_id=project_id, module_key="idea_validation", user_id=user_id)
    await svc.update_status(triggered.run_id, project_id, WORKFLOW_STATUS_COMPLETED)

    from app.repositories.project_repository import ProjectRepository
    repo = ProjectRepository(db_session)
    module = await repo.get_module(project_id, "idea_validation")
    assert module is not None
    assert module.status == MODULE_STATUS_COMPLETED


@pytest.mark.asyncio
async def test_failed_sets_module_failed(db_session):
    user_id, project_id = await _setup(db_session)
    svc = WorkflowService(db_session)
    triggered = await svc.trigger(project_id=project_id, module_key="idea_validation", user_id=user_id)
    await svc.update_status(
        triggered.run_id, project_id, WORKFLOW_STATUS_FAILED,
        error_code="OLLAMA_UNAVAILABLE",
        error_message="Ollama is down",
    )

    run = await svc.get_run(project_id, triggered.run_id, user_id)
    assert run.status == WORKFLOW_STATUS_FAILED
    assert run.error_code == "OLLAMA_UNAVAILABLE"


# ── persist_artifact ──────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_persist_artifact_saves_via_upsert(db_session):
    user_id, project_id = await _setup(db_session)
    svc = WorkflowService(db_session)
    triggered = await svc.trigger(project_id=project_id, module_key="idea_validation", user_id=user_id)

    await svc.persist_artifact(
        project_id=project_id,
        module_key="idea_validation",
        artifact_type="validation_report",
        title="AI Generated Report",
        content_json={"score": 85},
        content_markdown=None,
        workflow_run_id=triggered.run_id,
    )

    from app.repositories.artifact_repository import ArtifactRepository
    repo = ArtifactRepository(db_session)
    artifact = await repo.get_by_project_and_type(project_id, "validation_report")
    assert artifact is not None
    assert artifact.content_json["score"] == 85
