"""
Integration tests for authentication endpoints.
Tests the full stack: HTTP → router → service → repository → DB.
Uses in-memory SQLite via the app_client fixture.
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
    """
    Yield an AsyncClient wired to the FastAPI app with a fresh in-memory DB.
    Overrides the get_db dependency for the duration of the test.
    """
    engine = create_async_engine(
        TEST_DB_URL,
        connect_args={"check_same_thread": False},
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

async def _register(client: AsyncClient, email="user@test.com", password="Password1!", name="Test User"):
    return await client.post("/api/v1/auth/register", json={
        "email": email, "password": password, "full_name": name
    })


# ── Register ──────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_register_success(app_client):
    resp = await _register(app_client)
    assert resp.status_code == 201
    data = resp.json()
    assert data["user"]["email"] == "user@test.com"
    assert data["user"]["full_name"] == "Test User"
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_register_duplicate_email(app_client):
    await _register(app_client)
    resp = await _register(app_client)
    assert resp.status_code == 409
    assert resp.json()["error"]["code"] == "EMAIL_ALREADY_EXISTS"


@pytest.mark.asyncio
async def test_register_password_too_short(app_client):
    resp = await app_client.post("/api/v1/auth/register", json={
        "email": "x@test.com", "password": "short", "full_name": "X"
    })
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_register_invalid_email(app_client):
    resp = await app_client.post("/api/v1/auth/register", json={
        "email": "not-an-email", "password": "Password1!", "full_name": "X"
    })
    assert resp.status_code == 422


# ── Login ─────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_login_success(app_client):
    await _register(app_client)
    resp = await app_client.post("/api/v1/auth/login", json={
        "email": "user@test.com", "password": "Password1!"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_login_wrong_password(app_client):
    await _register(app_client)
    resp = await app_client.post("/api/v1/auth/login", json={
        "email": "user@test.com", "password": "WrongPassword!"
    })
    assert resp.status_code == 401
    assert resp.json()["error"]["code"] == "INVALID_CREDENTIALS"


@pytest.mark.asyncio
async def test_login_unknown_email(app_client):
    resp = await app_client.post("/api/v1/auth/login", json={
        "email": "nobody@test.com", "password": "Password1!"
    })
    assert resp.status_code == 401


# ── Refresh ───────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_refresh_success(app_client):
    reg = await _register(app_client)
    refresh_token = reg.json()["refresh_token"]

    resp = await app_client.post("/api/v1/auth/refresh", json={
        "refresh_token": refresh_token
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_refresh_token_rotated(app_client):
    """Old refresh token cannot be reused after rotation."""
    reg = await _register(app_client)
    old_refresh = reg.json()["refresh_token"]

    # First use — succeeds
    await app_client.post("/api/v1/auth/refresh", json={"refresh_token": old_refresh})

    # Reuse — should fail (token revoked)
    resp = await app_client.post("/api/v1/auth/refresh", json={"refresh_token": old_refresh})
    assert resp.status_code == 401
    assert resp.json()["error"]["code"] == "INVALID_REFRESH_TOKEN"


@pytest.mark.asyncio
async def test_refresh_invalid_token(app_client):
    resp = await app_client.post("/api/v1/auth/refresh", json={
        "refresh_token": "not-a-real-token"
    })
    assert resp.status_code == 401


# ── Logout ────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_logout_success(app_client):
    reg = await _register(app_client)
    access_token = reg.json()["access_token"]

    resp = await app_client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_logout_revokes_refresh_token(app_client):
    """After logout, the old refresh token should no longer work."""
    reg = await _register(app_client)
    access_token = reg.json()["access_token"]
    refresh_token = reg.json()["refresh_token"]

    await app_client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    resp = await app_client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_logout_requires_auth(app_client):
    resp = await app_client.post("/api/v1/auth/logout")
    assert resp.status_code == 401


# ── /me ───────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_me_success(app_client):
    reg = await _register(app_client)
    access_token = reg.json()["access_token"]

    resp = await app_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == "user@test.com"
    assert data["full_name"] == "Test User"
    assert "id" in data


@pytest.mark.asyncio
async def test_me_requires_auth(app_client):
    resp = await app_client.get("/api/v1/auth/me")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_me_invalid_token(app_client):
    resp = await app_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid.token.here"},
    )
    assert resp.status_code == 401


# ── Full flow ─────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_full_auth_flow(app_client):
    """Register → login → get /me → refresh → logout → refresh fails."""
    # 1. Register
    reg = await _register(app_client, email="flow@test.com")
    assert reg.status_code == 201

    # 2. Login
    login = await app_client.post("/api/v1/auth/login", json={
        "email": "flow@test.com", "password": "Password1!"
    })
    assert login.status_code == 200
    access = login.json()["access_token"]
    refresh = login.json()["refresh_token"]

    # 3. /me
    me = await app_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {access}"},
    )
    assert me.status_code == 200
    assert me.json()["email"] == "flow@test.com"

    # 4. Refresh
    new_tokens = await app_client.post("/api/v1/auth/refresh", json={"refresh_token": refresh})
    assert new_tokens.status_code == 200
    new_access = new_tokens.json()["access_token"]

    # 5. New access token works
    me2 = await app_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {new_access}"},
    )
    assert me2.status_code == 200

    # 6. Logout
    logout = await app_client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {new_access}"},
    )
    assert logout.status_code == 204

    # 7. Old refresh token no longer works
    reuse = await app_client.post("/api/v1/auth/refresh", json={"refresh_token": refresh})
    assert reuse.status_code == 401
