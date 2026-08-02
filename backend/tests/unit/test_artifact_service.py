"""
Unit tests for ArtifactService — upsert, versioning monotonicity, user edits.
Uses in-memory SQLite via db_session fixture.
"""

import uuid

import pytest

from app.core.exceptions import ArtifactNotFoundError, ProjectNotFoundError
from app.repositories.user_repository import UserRepository
from app.repositories.project_repository import ProjectRepository
from app.schemas.artifact import UpdateArtifactRequest
from app.schemas.project import CreateProjectRequest
from app.services.artifact_service import ArtifactService
from app.services.project_service import ProjectService


async def _make_user_and_project(db_session):
    """Helper: create a user + project and return (user_id, project_id)."""
    user_repo = UserRepository(db_session)
    user = await user_repo.create("art@test.com", "hash", "Art User")

    project_svc = ProjectService(db_session)
    project = await project_svc.create_project(
        user_id=user.id,
        data=CreateProjectRequest(
            name="TestProject",
            idea_brief="A great idea for testing artifact versioning functionality.",
        ),
    )
    return user.id, project.id


# ── Upsert (create) ───────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_upsert_creates_artifact(db_session):
    user_id, project_id = await _make_user_and_project(db_session)
    svc = ArtifactService(db_session)

    result = await svc.upsert_artifact(
        project_id=project_id,
        module_key="idea_validation",
        artifact_type="validation_report",
        title="Validation Report",
        content_json={"score": 85, "summary": "Strong idea"},
    )
    assert result.id is not None
    assert result.artifact_type == "validation_report"
    assert result.source == "ai"
    assert result.current_version_id is not None


@pytest.mark.asyncio
async def test_upsert_creates_version_1(db_session):
    user_id, project_id = await _make_user_and_project(db_session)
    svc = ArtifactService(db_session)
    from app.repositories.artifact_repository import ArtifactRepository

    await svc.upsert_artifact(
        project_id=project_id,
        module_key="idea_validation",
        artifact_type="validation_report",
        title="Report",
        content_json={"v": 1},
    )

    repo = ArtifactRepository(db_session)
    artifact = await repo.get_by_project_and_type(project_id, "validation_report")
    assert artifact is not None
    versions = await repo.get_versions(artifact.id)
    assert len(versions) == 1
    assert versions[0].version_number == 1


# ── Upsert (update) — versioning monotonicity ─────────────────────────────────

@pytest.mark.asyncio
async def test_upsert_twice_creates_version_2(db_session):
    user_id, project_id = await _make_user_and_project(db_session)
    svc = ArtifactService(db_session)
    from app.repositories.artifact_repository import ArtifactRepository

    await svc.upsert_artifact(
        project_id=project_id,
        module_key="idea_validation",
        artifact_type="validation_report",
        title="v1",
        content_json={"score": 70},
    )
    await svc.upsert_artifact(
        project_id=project_id,
        module_key="idea_validation",
        artifact_type="validation_report",
        title="v2",
        content_json={"score": 85},
    )

    repo = ArtifactRepository(db_session)
    artifact = await repo.get_by_project_and_type(project_id, "validation_report")
    assert artifact is not None
    versions = await repo.get_versions(artifact.id)
    assert len(versions) == 2
    # Newest first
    assert versions[0].version_number == 2
    assert versions[1].version_number == 1


@pytest.mark.asyncio
async def test_version_numbers_strictly_increment(db_session):
    """Property: N upserts produce versions 1..N in order."""
    user_id, project_id = await _make_user_and_project(db_session)
    svc = ArtifactService(db_session)
    from app.repositories.artifact_repository import ArtifactRepository

    n = 5
    for i in range(1, n + 1):
        await svc.upsert_artifact(
            project_id=project_id,
            module_key="idea_validation",
            artifact_type="validation_report",
            title=f"v{i}",
            content_json={"iteration": i},
        )

    repo = ArtifactRepository(db_session)
    artifact = await repo.get_by_project_and_type(project_id, "validation_report")
    assert artifact is not None
    versions = await repo.get_versions(artifact.id)
    assert len(versions) == n
    numbers = sorted(v.version_number for v in versions)
    assert numbers == list(range(1, n + 1))


@pytest.mark.asyncio
async def test_current_version_points_to_latest(db_session):
    user_id, project_id = await _make_user_and_project(db_session)
    svc = ArtifactService(db_session)
    from app.repositories.artifact_repository import ArtifactRepository

    await svc.upsert_artifact(
        project_id=project_id, module_key="idea_validation",
        artifact_type="validation_report", title="v1", content_json={"a": 1},
    )
    result = await svc.upsert_artifact(
        project_id=project_id, module_key="idea_validation",
        artifact_type="validation_report", title="v2", content_json={"a": 2},
    )

    repo = ArtifactRepository(db_session)
    versions = await repo.get_versions(result.id)
    latest = next(v for v in versions if v.version_number == 2)
    assert result.current_version_id == latest.id


# ── User edit ─────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_user_edit_increments_version(db_session):
    user_id, project_id = await _make_user_and_project(db_session)
    svc = ArtifactService(db_session)
    from app.repositories.artifact_repository import ArtifactRepository

    created = await svc.upsert_artifact(
        project_id=project_id, module_key="idea_validation",
        artifact_type="validation_report", title="AI v1", content_json={"score": 70},
    )

    updated = await svc.edit_artifact(
        project_id=project_id,
        artifact_id=created.id,
        user_id=user_id,
        data=UpdateArtifactRequest(
            content_json={"score": 90},
            change_summary="User improved score",
        ),
    )

    assert updated.source == "user"
    repo = ArtifactRepository(db_session)
    versions = await repo.get_versions(created.id)
    assert len(versions) == 2
    user_version = next(v for v in versions if v.version_number == 2)
    assert user_version.created_by == "user"
    assert user_version.change_summary == "User improved score"


# ── Access control ────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_list_artifacts_wrong_user_raises(db_session):
    user_id, project_id = await _make_user_and_project(db_session)
    svc = ArtifactService(db_session)
    wrong_user = uuid.uuid4()
    with pytest.raises(ProjectNotFoundError):
        await svc.list_artifacts(project_id, wrong_user)


@pytest.mark.asyncio
async def test_get_artifact_not_found_raises(db_session):
    user_id, project_id = await _make_user_and_project(db_session)
    svc = ArtifactService(db_session)
    with pytest.raises(ArtifactNotFoundError):
        await svc.get_artifact(project_id, uuid.uuid4(), user_id)


# ── Version retrieval ─────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_list_versions_returns_all(db_session):
    user_id, project_id = await _make_user_and_project(db_session)
    svc = ArtifactService(db_session)

    for i in range(3):
        await svc.upsert_artifact(
            project_id=project_id, module_key="idea_validation",
            artifact_type="validation_report", title=f"v{i}",
            content_json={"n": i},
        )

    from app.repositories.artifact_repository import ArtifactRepository
    repo = ArtifactRepository(db_session)
    artifact = await repo.get_by_project_and_type(project_id, "validation_report")
    assert artifact is not None

    versions = await svc.list_versions(project_id, artifact.id, user_id)
    assert len(versions) == 3


@pytest.mark.asyncio
async def test_get_version_by_number(db_session):
    user_id, project_id = await _make_user_and_project(db_session)
    svc = ArtifactService(db_session)

    await svc.upsert_artifact(
        project_id=project_id, module_key="idea_validation",
        artifact_type="validation_report", title="v1",
        content_json={"generation": 1},
    )
    await svc.upsert_artifact(
        project_id=project_id, module_key="idea_validation",
        artifact_type="validation_report", title="v2",
        content_json={"generation": 2},
    )

    from app.repositories.artifact_repository import ArtifactRepository
    repo = ArtifactRepository(db_session)
    artifact = await repo.get_by_project_and_type(project_id, "validation_report")
    assert artifact is not None

    v1 = await svc.get_version(project_id, artifact.id, 1, user_id)
    assert v1.version_number == 1
    assert v1.content_json == {"generation": 1}

    v2 = await svc.get_version(project_id, artifact.id, 2, user_id)
    assert v2.version_number == 2
    assert v2.content_json == {"generation": 2}
