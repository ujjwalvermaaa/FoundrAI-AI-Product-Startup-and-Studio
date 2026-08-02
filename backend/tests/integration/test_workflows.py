"""
Integration tests for workflow API endpoints.
Tests: trigger, list, get, cancel, SSE stream header/content.
"""

import asyncio
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

async def _register_and_token(client, email="user@test.com"):
    resp = await client.post("/api/v1/auth/register", json={
        "email": email, "password": "Password1!", "full_name": "Test User"
    })
    return resp.json()["access_token"]


async def _auth(token):
    return {"Authorization": f"Bearer {token}"}


async def _create_project(client, token):
    resp = await client.post(
        "/api/v1/projects",
        headers=await _auth(token),
        json={
            "name": "WF Project",
            "idea_brief": "Testing workflow API endpoints for FoundrAI platform.",
        },
    )
    return resp.json()["id"]


async def _seed_artifact(client, token, project_id, artifact_type, content):
    """Seed an artifact via the service layer to satisfy dependencies."""
    import uuid
    from app.database.session import get_db as _get_db
    from app.services.artifact_service import ArtifactService

    override_gen = app.dependency_overrides[_get_db]
    async for session in override_gen():
        svc = ArtifactService(session)
        await svc.upsert_artifact(
            project_id=uuid.UUID(project_id),
            module_key="idea_validation",
            artifact_type=artifact_type,
            title=artifact_type,
            content_json=content,
        )
        await session.commit()
        break


# ── POST /workflows/{module_key}/run ──────────────────────────────────────────

@pytest.mark.asyncio
async def test_trigger_idea_validation_returns_202(app_client):
    token = await _register_and_token(app_client)
    pid = await _create_project(app_client, token)
    resp = await app_client.post(
        f"/api/v1/projects/{pid}/workflows/idea_validation/run",
        headers=await _auth(token),
    )
    assert resp.status_code == 202
    data = resp.json()
    assert "run_id" in data
    assert data["status"] == "pending"
    assert "stream_url" in data


@pytest.mark.asyncio
async def test_trigger_returns_stream_url(app_client):
    token = await _register_and_token(app_client)
    pid = await _create_project(app_client, token)
    resp = await app_client.post(
        f"/api/v1/projects/{pid}/workflows/idea_validation/run",
        headers=await _auth(token),
    )
    assert resp.status_code == 202
    assert resp.json()["stream_url"].endswith("/stream")


@pytest.mark.asyncio
async def test_trigger_missing_dependency_returns_409(app_client):
    token = await _register_and_token(app_client)
    pid = await _create_project(app_client, token)
    resp = await app_client.post(
        f"/api/v1/projects/{pid}/workflows/market_research/run",
        headers=await _auth(token),
    )
    assert resp.status_code == 409
    assert resp.json()["error"]["code"] == "MODULE_DEPENDENCY_NOT_MET"


@pytest.mark.asyncio
async def test_trigger_invalid_module_returns_404(app_client):
    token = await _register_and_token(app_client)
    pid = await _create_project(app_client, token)
    resp = await app_client.post(
        f"/api/v1/projects/{pid}/workflows/nonexistent_module/run",
        headers=await _auth(token),
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_trigger_duplicate_returns_409(app_client):
    token = await _register_and_token(app_client)
    pid = await _create_project(app_client, token)
    await app_client.post(
        f"/api/v1/projects/{pid}/workflows/idea_validation/run",
        headers=await _auth(token),
    )
    resp = await app_client.post(
        f"/api/v1/projects/{pid}/workflows/idea_validation/run",
        headers=await _auth(token),
    )
    assert resp.status_code == 409
    assert resp.json()["error"]["code"] == "WORKFLOW_ALREADY_RUNNING"


@pytest.mark.asyncio
async def test_trigger_requires_auth(app_client):
    import uuid
    resp = await app_client.post(
        f"/api/v1/projects/{uuid.uuid4()}/workflows/idea_validation/run"
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_trigger_with_dependency_satisfied(app_client):
    token = await _register_and_token(app_client)
    pid = await _create_project(app_client, token)
    await _seed_artifact(app_client, token, pid, "validation_report", {"score": 80})
    resp = await app_client.post(
        f"/api/v1/projects/{pid}/workflows/market_research/run",
        headers=await _auth(token),
    )
    assert resp.status_code == 202


# ── GET /workflows/runs ────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_list_runs_empty(app_client):
    token = await _register_and_token(app_client)
    pid = await _create_project(app_client, token)
    resp = await app_client.get(
        f"/api/v1/projects/{pid}/workflows/runs",
        headers=await _auth(token),
    )
    assert resp.status_code == 200
    assert resp.json()["total"] == 0


@pytest.mark.asyncio
async def test_list_runs_after_trigger(app_client):
    token = await _register_and_token(app_client)
    pid = await _create_project(app_client, token)
    await app_client.post(
        f"/api/v1/projects/{pid}/workflows/idea_validation/run",
        headers=await _auth(token),
    )
    resp = await app_client.get(
        f"/api/v1/projects/{pid}/workflows/runs",
        headers=await _auth(token),
    )
    assert resp.json()["total"] == 1
    assert resp.json()["items"][0]["module_key"] == "idea_validation"


@pytest.mark.asyncio
async def test_list_runs_filter_by_module(app_client):
    token = await _register_and_token(app_client)
    pid = await _create_project(app_client, token)
    await app_client.post(
        f"/api/v1/projects/{pid}/workflows/idea_validation/run",
        headers=await _auth(token),
    )
    resp = await app_client.get(
        f"/api/v1/projects/{pid}/workflows/runs?module_key=idea_validation",
        headers=await _auth(token),
    )
    assert resp.json()["total"] == 1

    resp2 = await app_client.get(
        f"/api/v1/projects/{pid}/workflows/runs?module_key=market_research",
        headers=await _auth(token),
    )
    assert resp2.json()["total"] == 0


# ── GET /workflows/runs/{run_id} ───────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_run_found(app_client):
    token = await _register_and_token(app_client)
    pid = await _create_project(app_client, token)
    trigger = (await app_client.post(
        f"/api/v1/projects/{pid}/workflows/idea_validation/run",
        headers=await _auth(token),
    )).json()
    run_id = trigger["run_id"]

    resp = await app_client.get(
        f"/api/v1/projects/{pid}/workflows/runs/{run_id}",
        headers=await _auth(token),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == run_id
    assert data["module_key"] == "idea_validation"
    assert data["status"] == "pending"
    assert "steps" in data


@pytest.mark.asyncio
async def test_get_run_not_found(app_client):
    import uuid
    token = await _register_and_token(app_client)
    pid = await _create_project(app_client, token)
    resp = await app_client.get(
        f"/api/v1/projects/{pid}/workflows/runs/{uuid.uuid4()}",
        headers=await _auth(token),
    )
    assert resp.status_code == 404


# ── POST /workflows/runs/{run_id}/cancel ──────────────────────────────────────

@pytest.mark.asyncio
async def test_cancel_pending_run(app_client):
    token = await _register_and_token(app_client)
    pid = await _create_project(app_client, token)
    trigger = (await app_client.post(
        f"/api/v1/projects/{pid}/workflows/idea_validation/run",
        headers=await _auth(token),
    )).json()
    run_id = trigger["run_id"]

    resp = await app_client.post(
        f"/api/v1/projects/{pid}/workflows/runs/{run_id}/cancel",
        headers=await _auth(token),
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "cancelled"


@pytest.mark.asyncio
async def test_cancel_after_cancel_returns_409(app_client):
    token = await _register_and_token(app_client)
    pid = await _create_project(app_client, token)
    trigger = (await app_client.post(
        f"/api/v1/projects/{pid}/workflows/idea_validation/run",
        headers=await _auth(token),
    )).json()
    run_id = trigger["run_id"]

    await app_client.post(
        f"/api/v1/projects/{pid}/workflows/runs/{run_id}/cancel",
        headers=await _auth(token),
    )
    resp = await app_client.post(
        f"/api/v1/projects/{pid}/workflows/runs/{run_id}/cancel",
        headers=await _auth(token),
    )
    assert resp.status_code == 409
    assert resp.json()["error"]["code"] == "WORKFLOW_NOT_CANCELLABLE"


# ── SSE stream ─────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_sse_stream_unauthorized_returns_401(app_client):
    """Unauthenticated SSE request returns 401."""
    import uuid
    pid = str(uuid.uuid4())
    run_id = str(uuid.uuid4())
    resp = await app_client.get(
        f"/api/v1/projects/{pid}/workflows/runs/{run_id}/stream"
    )
    assert resp.status_code == 401


def test_sse_event_format():
    """Unit test: _sse_event produces correct SSE wire format."""
    from app.api.v1.workflows import _sse_event
    import json as _json

    result = _sse_event("run_completed", {"run_id": "abc-123"})
    assert result.startswith("event: run_completed\n")
    assert "data: " in result
    payload = _json.loads(result.split("data: ")[1].split("\n")[0])
    assert payload["run_id"] == "abc-123"
    assert result.endswith("\n\n")


@pytest.mark.asyncio
async def test_sse_stream_unauthorized(app_client):
    import uuid
    pid = str(uuid.uuid4())
    run_id = str(uuid.uuid4())
    resp = await app_client.get(
        f"/api/v1/projects/{pid}/workflows/runs/{run_id}/stream"
    )
    assert resp.status_code == 401
