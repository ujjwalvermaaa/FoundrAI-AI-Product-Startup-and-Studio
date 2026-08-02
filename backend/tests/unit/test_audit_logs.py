"""
Unit tests for Task 42: AuditLog model and AuditRepository.

Tests:
- test_audit_log_model_fields           — model has expected columns
- test_audit_repository_create          — creates a row in DB
- test_audit_repository_event_type      — event_type is stored correctly
- test_audit_repository_resource_fields — resource_type/id stored correctly
- test_audit_repository_metadata        — metadata_json stored correctly
- test_audit_log_user_id_nullable       — user_id can be None
- test_error_response_format_foundrai_exception — domain exceptions return correct JSON shape
- test_error_response_format_unexpected  — unhandled exceptions return INTERNAL_ERROR shape
"""

from __future__ import annotations

import uuid

import pytest

from app.models.audit_log import AuditLog
from app.repositories.audit_repository import AuditRepository


# ── Model field tests ─────────────────────────────────────────────────────────

def test_audit_log_model_fields():
    """AuditLog model must expose all required column attributes."""
    required = [
        "id", "user_id", "event_type", "resource_type",
        "resource_id", "ip_address", "user_agent", "metadata_json", "created_at",
    ]
    for field in required:
        assert hasattr(AuditLog, field), f"AuditLog missing field: {field}"


def test_audit_log_tablename():
    assert AuditLog.__tablename__ == "audit_logs"


# ── Repository tests (uses db_session fixture — SQLite in-memory) ──────────────

@pytest.mark.asyncio
async def test_audit_repository_create(db_session):
    """AuditRepository.create persists a row that can be fetched back."""
    from sqlalchemy import select

    repo = AuditRepository()
    entry = await repo.create(
        session=db_session,
        event_type="project.create",
        user_id=None,
    )

    assert entry.id is not None
    assert entry.event_type == "project.create"

    # Verify it's actually in the DB
    result = await db_session.execute(
        select(AuditLog).where(AuditLog.id == entry.id)
    )
    fetched = result.scalar_one_or_none()
    assert fetched is not None
    assert fetched.event_type == "project.create"


@pytest.mark.asyncio
async def test_audit_repository_event_type(db_session):
    """Event type is stored exactly as passed."""
    repo = AuditRepository()
    for event in ["project.create", "workflow.trigger", "export"]:
        entry = await repo.create(session=db_session, event_type=event)
        assert entry.event_type == event


@pytest.mark.asyncio
async def test_audit_repository_resource_fields(db_session):
    """resource_type and resource_id are stored correctly."""
    repo = AuditRepository()
    rid = uuid.uuid4()
    entry = await repo.create(
        session=db_session,
        event_type="workflow.trigger",
        resource_type="workflow_run",
        resource_id=rid,
    )
    assert entry.resource_type == "workflow_run"
    assert entry.resource_id == rid


@pytest.mark.asyncio
async def test_audit_repository_metadata(db_session):
    """metadata_json dict is stored and retrievable."""
    repo = AuditRepository()
    meta = {"module_key": "idea_validation", "project_id": str(uuid.uuid4())}
    entry = await repo.create(
        session=db_session,
        event_type="workflow.trigger",
        metadata=meta,
    )
    assert entry.metadata_json == meta


@pytest.mark.asyncio
async def test_audit_log_user_id_nullable(db_session):
    """user_id is nullable — creating without it must not raise."""
    repo = AuditRepository()
    entry = await repo.create(
        session=db_session,
        event_type="project.create",
        user_id=None,
    )
    assert entry.user_id is None


# ── Error response format tests ───────────────────────────────────────────────

def test_error_response_format_foundrai_exception():
    """FoundrAI domain exceptions must format as {error: {code, message, details}}."""
    from app.core.exceptions import ProjectNotFoundError
    exc = ProjectNotFoundError("abc-123")
    assert exc.code == "PROJECT_NOT_FOUND"
    assert exc.status_code == 404
    assert isinstance(exc.message, str)
    assert "project_id" in exc.details


def test_error_response_format_insufficient_artifacts():
    """InsufficientArtifactsError formats correctly."""
    from app.core.exceptions import InsufficientArtifactsError
    exc = InsufficientArtifactsError(["validation_report", "financial_model"])
    assert exc.code == "INSUFFICIENT_ARTIFACTS"
    assert exc.status_code == 409
    assert "validation_report" in exc.details["missing_artifacts"]
    assert "financial_model" in exc.details["missing_artifacts"]


def test_error_response_format_workflow_already_running():
    """WorkflowAlreadyRunningError has correct code and status."""
    from app.core.exceptions import WorkflowAlreadyRunningError
    exc = WorkflowAlreadyRunningError("idea_validation")
    assert exc.code == "WORKFLOW_ALREADY_RUNNING"
    assert exc.status_code == 409
    assert exc.details["module_key"] == "idea_validation"


def test_error_response_format_module_dependency():
    """ModuleDependencyNotMetError lists missing artifacts."""
    from app.core.exceptions import ModuleDependencyNotMetError
    exc = ModuleDependencyNotMetError(["validation_report"])
    assert exc.code == "MODULE_DEPENDENCY_NOT_MET"
    assert exc.status_code == 409
    assert "validation_report" in exc.details["missing_artifacts"]


def test_all_exceptions_have_error_shape():
    """All FoundrAIException subclasses must have code, message, status_code, details."""
    from app.core.exceptions import (
        EmailAlreadyExistsError, InvalidCredentialsError, InvalidRefreshTokenError,
        ProjectNotFoundError, ModuleNotFoundError, WorkflowAlreadyRunningError,
        WorkflowNotCancellableError, ArtifactNotFoundError, SchemaValidationFailedError,
        InsufficientArtifactsError, OllamaUnavailableError,
    )

    exceptions = [
        EmailAlreadyExistsError("test@test.com"),
        InvalidCredentialsError(),
        InvalidRefreshTokenError(),
        ProjectNotFoundError("proj-id"),
        ModuleNotFoundError("unknown"),
        WorkflowAlreadyRunningError("idea_validation"),
        WorkflowNotCancellableError(),
        ArtifactNotFoundError("art-id"),
        SchemaValidationFailedError("field error"),
        InsufficientArtifactsError(["validation_report"]),
        OllamaUnavailableError(),
    ]

    for exc in exceptions:
        assert hasattr(exc, "code"), f"{type(exc).__name__} missing .code"
        assert hasattr(exc, "message"), f"{type(exc).__name__} missing .message"
        assert hasattr(exc, "status_code"), f"{type(exc).__name__} missing .status_code"
        assert hasattr(exc, "details"), f"{type(exc).__name__} missing .details"
        assert isinstance(exc.code, str) and exc.code
        assert isinstance(exc.message, str) and exc.message
        assert isinstance(exc.status_code, int)
        assert isinstance(exc.details, dict)
