"""
Integration tests for artifact API endpoints.
Tests full stack: HTTP → router → service → repository → DB.
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database.base import Base
from app.database.session import get_db
from app.main import app

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture(scope="function")
async def app_client():
    engine = create_async_engine(
        TEST_DB_URL, connect_args={"check_same_thread": False}
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(
        bind=engine, class_=AsyncSession,
        expire_on_commit=False, autocommit=False, autoflush=False,
    )

    async def override_get_db():
        async with session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client

    app.dependency_overrides.clear()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


# ── Helpers ───────────────────────────────────────────────────────────────────

async def _register_and_token(client: AsyncClient, email="user@test.com") -> str:
    resp = await client.post("/api/v1/auth/register", json={
        "email": email, "password": "Password1!", "full_name": "Test User"
    })
    return resp.json()["access_token"]


async def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


async def _create_project(client, token):
    resp = await client.post(
        "/api/v1/projects",
        headers=await _auth(token),
        json={
            "name": "My Startup",
            "idea_brief": "A brilliant idea for testing artifact endpoints in the API.",
        },
    )
    return resp.json()["id"]


async def _seed_artifact(client, token, project_id, artifact_type="validation_report"):
    """Seed an artifact via the ArtifactService directly (bypass — uses upsert)."""
    from app.services.artifact_service import ArtifactService
    # We'll use the PATCH endpoint after we have an artifact
    # But first we need to create via upsert — expose a test helper
    # For simplicity: we'll test that list is empty first, then create via service in conftest
    return None


# ── GET /projects/{pid}/artifacts ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_list_artifacts_empty(app_client):
    token = await _register_and_token(app_client)
    pid = await _create_project(app_client, token)
    resp = await app_client.get(
        f"/api/v1/projects/{pid}/artifacts",
        headers=await _auth(token),
    )
    assert resp.status_code == 200
    assert resp.json()["total"] == 0
    assert resp.json()["items"] == []


@pytest.mark.asyncio
async def test_list_artifacts_project_not_found(app_client):
    import uuid
    token = await _register_and_token(app_client)
    resp = await app_client.get(
        f"/api/v1/projects/{uuid.uuid4()}/artifacts",
        headers=await _auth(token),
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_list_artifacts_requires_auth(app_client):
    import uuid
    resp = await app_client.get(f"/api/v1/projects/{uuid.uuid4()}/artifacts")
    assert resp.status_code == 401


# ── GET /projects/{pid}/artifacts/{aid} ───────────────────────────────────────

@pytest.mark.asyncio
async def test_get_artifact_not_found(app_client):
    import uuid
    token = await _register_and_token(app_client)
    pid = await _create_project(app_client, token)
    resp = await app_client.get(
        f"/api/v1/projects/{pid}/artifacts/{uuid.uuid4()}",
        headers=await _auth(token),
    )
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "ARTIFACT_NOT_FOUND"


# ── Full CRUD flow via upsert + PATCH ─────────────────────────────────────────

@pytest.mark.asyncio
async def test_full_artifact_flow(app_client):
    """
    Full flow: upsert via service → list (1 item) → get → PATCH (new version)
    → list versions (2) → get version by number.
    Uses a separate in-memory DB session to seed the artifact before HTTP calls.
    """
    import uuid
    from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
    from app.database.session import get_db as _get_db
    from app.services.artifact_service import ArtifactService

    token = await _register_and_token(app_client, "flow@test.com")
    pid = await _create_project(app_client, token)
    project_id = uuid.UUID(pid)

    # Seed artifact via the same DB the app uses (get it from the override closure)
    # We create a fresh session on the same in-memory engine by calling the override
    override_gen = app.dependency_overrides[_get_db]
    async for session in override_gen():
        svc = ArtifactService(session)
        await svc.upsert_artifact(
            project_id=project_id,
            module_key="idea_validation",
            artifact_type="validation_report",
            title="Validation Report v1",
            content_json={"score": 75, "summary": "Good idea"},
            source="ai",
        )
        await session.commit()
        break

    # List — should have 1
    resp = await app_client.get(
        f"/api/v1/projects/{pid}/artifacts",
        headers=await _auth(token),
    )
    assert resp.status_code == 200
    assert resp.json()["total"] == 1
    artifact_id = resp.json()["items"][0]["id"]

    # Get single
    resp = await app_client.get(
        f"/api/v1/projects/{pid}/artifacts/{artifact_id}",
        headers=await _auth(token),
    )
    assert resp.status_code == 200
    assert resp.json()["artifact_type"] == "validation_report"
    assert resp.json()["source"] == "ai"

    # PATCH — user edit
    resp = await app_client.patch(
        f"/api/v1/projects/{pid}/artifacts/{artifact_id}",
        headers=await _auth(token),
        json={
            "content_json": {"score": 90, "summary": "Excellent idea"},
            "change_summary": "User improved score",
        },
    )
    assert resp.status_code == 200
    assert resp.json()["source"] == "user"
    assert resp.json()["content_json"]["score"] == 90

    # List versions — should have 2 (v1=AI, v2=user)
    resp = await app_client.get(
        f"/api/v1/projects/{pid}/artifacts/{artifact_id}/versions",
        headers=await _auth(token),
    )
    assert resp.status_code == 200
    versions = resp.json()
    assert len(versions) == 2
    assert versions[0]["version_number"] == 2
    assert versions[1]["version_number"] == 1

    # Get version 1 snapshot
    resp = await app_client.get(
        f"/api/v1/projects/{pid}/artifacts/{artifact_id}/versions/1",
        headers=await _auth(token),
    )
    assert resp.status_code == 200
    assert resp.json()["version_number"] == 1
    assert resp.json()["content_json"]["score"] == 75

    # Get version 2 snapshot
    resp = await app_client.get(
        f"/api/v1/projects/{pid}/artifacts/{artifact_id}/versions/2",
        headers=await _auth(token),
    )
    assert resp.status_code == 200
    assert resp.json()["version_number"] == 2
    assert resp.json()["content_json"]["score"] == 90


@pytest.mark.asyncio
async def test_patch_artifact_wrong_user(app_client):
    """User B cannot edit User A's artifact."""
    import uuid
    from app.database.session import get_db as _get_db
    from app.services.artifact_service import ArtifactService

    token_a = await _register_and_token(app_client, "a@test.com")
    token_b = await _register_and_token(app_client, "b@test.com")
    pid = await _create_project(app_client, token_a)
    project_id = uuid.UUID(pid)

    override_gen = app.dependency_overrides[_get_db]
    artifact_id = None
    async for session in override_gen():
        svc = ArtifactService(session)
        result = await svc.upsert_artifact(
            project_id=project_id,
            module_key="idea_validation",
            artifact_type="validation_report",
            title="Report",
            content_json={"score": 70},
        )
        await session.commit()
        artifact_id = result.id
        break

    resp = await app_client.patch(
        f"/api/v1/projects/{pid}/artifacts/{artifact_id}",
        headers=await _auth(token_b),
        json={"content_json": {"score": 99}},
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_list_versions_artifact_not_found(app_client):
    import uuid
    token = await _register_and_token(app_client)
    pid = await _create_project(app_client, token)
    resp = await app_client.get(
        f"/api/v1/projects/{pid}/artifacts/{uuid.uuid4()}/versions",
        headers=await _auth(token),
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_get_version_not_found(app_client):
    import uuid
    token = await _register_and_token(app_client)
    pid = await _create_project(app_client, token)
    resp = await app_client.get(
        f"/api/v1/projects/{pid}/artifacts/{uuid.uuid4()}/versions/99",
        headers=await _auth(token),
    )
    assert resp.status_code == 404
