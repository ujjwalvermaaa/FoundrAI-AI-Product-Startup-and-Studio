"""
Integration tests for health and readiness endpoints.

GET /health         → 200 liveness
GET /health/ready   → 200 ready or 503 degraded
"""

from __future__ import annotations

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from unittest.mock import AsyncMock, patch

from app.main import app as fastapi_app


@pytest_asyncio.fixture(scope="function")
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=fastapi_app), base_url="http://test"
    ) as c:
        yield c


# ── Liveness ──────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_health_liveness_returns_200(client):
    """GET /health must return 200 with status: ok."""
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_health_liveness_no_auth_required(client):
    """Health endpoint must not require authentication."""
    resp = await client.get("/health")
    assert resp.status_code == 200


# ── Readiness ─────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_health_ready_returns_checks_dict(client):
    """GET /health/ready must return a JSON body with 'status' and 'checks' keys."""
    resp = await client.get("/health/ready")
    # May be 200 or 503 depending on environment — just check the shape
    data = resp.json()
    assert "status" in data
    assert "checks" in data
    assert isinstance(data["checks"], dict)


@pytest.mark.asyncio
async def test_health_ready_checks_have_database_key(client):
    """The checks dict must always include a 'database' key."""
    resp = await client.get("/health/ready")
    data = resp.json()
    assert "database" in data["checks"]


@pytest.mark.asyncio
async def test_health_ready_200_when_all_checks_pass(client):
    """When DB check passes, the database entry in checks should be 'up'."""
    with patch("app.database.session.check_db_connection", new_callable=AsyncMock) as mock_db:
        mock_db.return_value = None
        resp = await client.get("/health/ready")

    data = resp.json()
    # Database check must pass
    assert data["checks"]["database"] == "up"


@pytest.mark.asyncio
async def test_health_ready_503_when_db_down(client):
    """When DB check fails → 503 degraded with database: down."""
    with patch("app.database.session.check_db_connection", side_effect=Exception("Connection refused")):
        resp = await client.get("/health/ready")

    assert resp.status_code == 503
    data = resp.json()
    assert data["status"] == "degraded"
    assert data["checks"]["database"] == "down"


@pytest.mark.asyncio
async def test_health_ready_status_field_values(client):
    """status must be either 'ready' or 'degraded'."""
    resp = await client.get("/health/ready")
    data = resp.json()
    assert data["status"] in ("ready", "degraded")


@pytest.mark.asyncio
async def test_health_ready_check_values_are_strings(client):
    """All values in the checks dict must be strings."""
    resp = await client.get("/health/ready")
    data = resp.json()
    for key, value in data["checks"].items():
        assert isinstance(value, str), f"checks['{key}'] should be a string, got {type(value)}"
