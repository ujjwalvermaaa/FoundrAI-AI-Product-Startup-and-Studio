"""
Integration tests for memory search API endpoint.

POST /api/v1/projects/{project_id}/memory/search

Tests verify response shape and auth behaviour.
Since the integration test uses an in-memory SQLite DB with no real FAISS index,
search results will always be empty — that is expected and asserted here.
"""

import uuid

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from unittest.mock import AsyncMock, patch

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
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
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

async def _register_and_token(client: AsyncClient, email: str = "user@test.com") -> str:
    resp = await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "Password1!", "full_name": "Test User"},
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["access_token"]


def _auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


async def _create_project(client: AsyncClient, token: str) -> str:
    resp = await client.post(
        "/api/v1/projects",
        headers=_auth_header(token),
        json={
            "name": "Memory Test Project",
            "idea_brief": "A brilliant SaaS idea for testing memory endpoints.",
        },
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


# ── Tests ─────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_memory_search_endpoint_returns_200(app_client):
    """
    POST /projects/{id}/memory/search returns 200 with the correct response shape
    (results list and total field) even when the index is empty.
    """
    token = await _register_and_token(app_client, "search@test.com")
    pid = await _create_project(app_client, token)

    resp = await app_client.post(
        f"/api/v1/projects/{pid}/memory/search",
        headers=_auth_header(token),
        json={"query": "startup target market", "top_k": 8},
    )

    assert resp.status_code == 200
    data = resp.json()
    assert "results" in data
    assert "total" in data
    assert isinstance(data["results"], list)
    assert isinstance(data["total"], int)


@pytest.mark.asyncio
async def test_memory_search_requires_auth(app_client):
    """Unauthenticated request returns 401."""
    token = await _register_and_token(app_client, "noauth@test.com")
    pid = await _create_project(app_client, token)

    resp = await app_client.post(
        f"/api/v1/projects/{pid}/memory/search",
        json={"query": "target market", "top_k": 5},
    )

    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_memory_search_wrong_project_returns_404(app_client):
    """Searching on another user's project returns 404."""
    token_a = await _register_and_token(app_client, "owner@test.com")
    token_b = await _register_and_token(app_client, "other@test.com")

    # User A creates a project
    pid = await _create_project(app_client, token_a)

    # User B tries to search it
    resp = await app_client.post(
        f"/api/v1/projects/{pid}/memory/search",
        headers=_auth_header(token_b),
        json={"query": "investors", "top_k": 5},
    )

    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_memory_search_empty_returns_empty_list(app_client):
    """
    When there are no FAISS matches for the query, the endpoint returns
    {"results": [], "total": 0}.
    We patch MemoryManager.search to return an empty list, simulating
    a project whose FAISS index has no relevant content.
    """
    token = await _register_and_token(app_client, "empty@test.com")
    pid = await _create_project(app_client, token)

    with patch(
        "ai.memory.memory_manager.MemoryManager.search",
        new_callable=AsyncMock,
        return_value=[],
    ):
        resp = await app_client.post(
            f"/api/v1/projects/{pid}/memory/search",
            headers=_auth_header(token),
            json={"query": "anything", "top_k": 8},
        )

    assert resp.status_code == 200
    data = resp.json()
    assert data["results"] == []
    assert data["total"] == 0
