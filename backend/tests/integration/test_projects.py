"""
Integration tests for projects and modules API endpoints.
Tests the full stack: HTTP → router → service → repository → DB.
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
    """Register a user and return its access token."""
    resp = await client.post("/api/v1/auth/register", json={
        "email": email, "password": "Password1!", "full_name": "Test User"
    })
    return resp.json()["access_token"]


async def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


async def _create_project(client, token, name="My Startup"):
    return await client.post(
        "/api/v1/projects",
        headers=await _auth(token),
        json={
            "name": name,
            "idea_brief": "A platform connecting coffee lovers with local roasters.",
            "tagline": "Find your perfect cup.",
            "industry": "Food & Beverage",
        },
    )


# ── POST /projects ────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_project_returns_201(app_client):
    token = await _register_and_token(app_client)
    resp = await _create_project(app_client, token)
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "My Startup"
    assert "id" in data


@pytest.mark.asyncio
async def test_create_project_seeds_8_modules(app_client):
    token = await _register_and_token(app_client)
    resp = await _create_project(app_client, token)
    modules = resp.json()["modules"]
    assert len(modules) == 8


@pytest.mark.asyncio
async def test_create_project_first_module_available(app_client):
    token = await _register_and_token(app_client)
    resp = await _create_project(app_client, token)
    first = resp.json()["modules"][0]
    assert first["module_key"] == "idea_validation"
    assert first["status"] == "available"


@pytest.mark.asyncio
async def test_create_project_remaining_modules_locked(app_client):
    token = await _register_and_token(app_client)
    resp = await _create_project(app_client, token)
    for mod in resp.json()["modules"][1:]:
        assert mod["status"] == "locked"


@pytest.mark.asyncio
async def test_create_project_requires_auth(app_client):
    resp = await app_client.post("/api/v1/projects", json={
        "name": "x", "idea_brief": "some brief here long enough"
    })
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_create_project_missing_brief(app_client):
    token = await _register_and_token(app_client)
    resp = await app_client.post(
        "/api/v1/projects",
        headers=await _auth(token),
        json={"name": "x"},
    )
    assert resp.status_code == 422


# ── GET /projects ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_list_projects_empty(app_client):
    token = await _register_and_token(app_client)
    resp = await app_client.get("/api/v1/projects", headers=await _auth(token))
    assert resp.status_code == 200
    assert resp.json()["total"] == 0
    assert resp.json()["items"] == []


@pytest.mark.asyncio
async def test_list_projects_returns_owned(app_client):
    token = await _register_and_token(app_client)
    await _create_project(app_client, token, "P1")
    await _create_project(app_client, token, "P2")
    resp = await app_client.get("/api/v1/projects", headers=await _auth(token))
    assert resp.json()["total"] == 2
    assert len(resp.json()["items"]) == 2


@pytest.mark.asyncio
async def test_list_projects_isolates_users(app_client):
    token_a = await _register_and_token(app_client, "a@test.com")
    token_b = await _register_and_token(app_client, "b@test.com")
    await _create_project(app_client, token_a)
    resp = await app_client.get("/api/v1/projects", headers=await _auth(token_b))
    assert resp.json()["total"] == 0


@pytest.mark.asyncio
async def test_list_projects_pagination(app_client):
    token = await _register_and_token(app_client)
    for i in range(5):
        await _create_project(app_client, token, f"P{i}")
    resp = await app_client.get(
        "/api/v1/projects?skip=0&limit=3", headers=await _auth(token)
    )
    assert resp.json()["total"] == 5
    assert len(resp.json()["items"]) == 3


# ── GET /projects/{id} ────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_project_found(app_client):
    token = await _register_and_token(app_client)
    created = (await _create_project(app_client, token)).json()
    resp = await app_client.get(
        f"/api/v1/projects/{created['id']}", headers=await _auth(token)
    )
    assert resp.status_code == 200
    assert resp.json()["id"] == created["id"]
    assert len(resp.json()["modules"]) == 8


@pytest.mark.asyncio
async def test_get_project_not_found(app_client):
    import uuid
    token = await _register_and_token(app_client)
    resp = await app_client.get(
        f"/api/v1/projects/{uuid.uuid4()}", headers=await _auth(token)
    )
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "PROJECT_NOT_FOUND"


@pytest.mark.asyncio
async def test_get_project_wrong_user_returns_404(app_client):
    token_a = await _register_and_token(app_client, "a@test.com")
    token_b = await _register_and_token(app_client, "b@test.com")
    created = (await _create_project(app_client, token_a)).json()
    resp = await app_client.get(
        f"/api/v1/projects/{created['id']}", headers=await _auth(token_b)
    )
    assert resp.status_code == 404


# ── PATCH /projects/{id} ──────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_update_project_name(app_client):
    token = await _register_and_token(app_client)
    created = (await _create_project(app_client, token)).json()
    resp = await app_client.patch(
        f"/api/v1/projects/{created['id']}",
        headers=await _auth(token),
        json={"name": "Updated Name"},
    )
    assert resp.status_code == 200
    assert resp.json()["name"] == "Updated Name"


@pytest.mark.asyncio
async def test_update_project_not_found(app_client):
    import uuid
    token = await _register_and_token(app_client)
    resp = await app_client.patch(
        f"/api/v1/projects/{uuid.uuid4()}",
        headers=await _auth(token),
        json={"name": "x"},
    )
    assert resp.status_code == 404


# ── DELETE /projects/{id} ─────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_delete_project_returns_204(app_client):
    token = await _register_and_token(app_client)
    created = (await _create_project(app_client, token)).json()
    resp = await app_client.delete(
        f"/api/v1/projects/{created['id']}", headers=await _auth(token)
    )
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_delete_project_then_not_found(app_client):
    token = await _register_and_token(app_client)
    created = (await _create_project(app_client, token)).json()
    await app_client.delete(
        f"/api/v1/projects/{created['id']}", headers=await _auth(token)
    )
    resp = await app_client.get(
        f"/api/v1/projects/{created['id']}", headers=await _auth(token)
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_project_not_found(app_client):
    import uuid
    token = await _register_and_token(app_client)
    resp = await app_client.delete(
        f"/api/v1/projects/{uuid.uuid4()}", headers=await _auth(token)
    )
    assert resp.status_code == 404


# ── GET /projects/{id}/modules ────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_list_modules_returns_8(app_client):
    token = await _register_and_token(app_client)
    created = (await _create_project(app_client, token)).json()
    resp = await app_client.get(
        f"/api/v1/projects/{created['id']}/modules",
        headers=await _auth(token),
    )
    assert resp.status_code == 200
    assert len(resp.json()) == 8


@pytest.mark.asyncio
async def test_list_modules_sorted_by_sort_order(app_client):
    token = await _register_and_token(app_client)
    created = (await _create_project(app_client, token)).json()
    resp = await app_client.get(
        f"/api/v1/projects/{created['id']}/modules",
        headers=await _auth(token),
    )
    orders = [m["sort_order"] for m in resp.json()]
    assert orders == sorted(orders)


@pytest.mark.asyncio
async def test_list_modules_project_not_found(app_client):
    import uuid
    token = await _register_and_token(app_client)
    resp = await app_client.get(
        f"/api/v1/projects/{uuid.uuid4()}/modules",
        headers=await _auth(token),
    )
    assert resp.status_code == 404


# ── GET /projects/{id}/modules/{module_key} ───────────────────────────────────

@pytest.mark.asyncio
async def test_get_module_found(app_client):
    token = await _register_and_token(app_client)
    created = (await _create_project(app_client, token)).json()
    resp = await app_client.get(
        f"/api/v1/projects/{created['id']}/modules/idea_validation",
        headers=await _auth(token),
    )
    assert resp.status_code == 200
    assert resp.json()["module_key"] == "idea_validation"
    assert resp.json()["status"] == "available"


@pytest.mark.asyncio
async def test_get_module_invalid_key(app_client):
    token = await _register_and_token(app_client)
    created = (await _create_project(app_client, token)).json()
    resp = await app_client.get(
        f"/api/v1/projects/{created['id']}/modules/nonexistent_module",
        headers=await _auth(token),
    )
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "MODULE_NOT_FOUND"


# ── Full CRUD flow ────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_full_project_crud_flow(app_client):
    """Create → list → get → update → delete → verify gone."""
    token = await _register_and_token(app_client)

    # Create
    created = (await _create_project(app_client, token, "My App")).json()
    pid = created["id"]
    assert created["stage"] == "draft"

    # List
    lst = (await app_client.get("/api/v1/projects", headers=await _auth(token))).json()
    assert lst["total"] == 1

    # Get
    got = (await app_client.get(f"/api/v1/projects/{pid}", headers=await _auth(token))).json()
    assert got["name"] == "My App"

    # Update
    updated = (await app_client.patch(
        f"/api/v1/projects/{pid}",
        headers=await _auth(token),
        json={"name": "My App v2", "stage": "active"},
    )).json()
    assert updated["name"] == "My App v2"
    assert updated["stage"] == "active"

    # Modules
    modules = (await app_client.get(
        f"/api/v1/projects/{pid}/modules", headers=await _auth(token)
    )).json()
    assert len(modules) == 8

    # Delete
    del_resp = await app_client.delete(f"/api/v1/projects/{pid}", headers=await _auth(token))
    assert del_resp.status_code == 204

    # Verify gone
    gone = await app_client.get(f"/api/v1/projects/{pid}", headers=await _auth(token))
    assert gone.status_code == 404
