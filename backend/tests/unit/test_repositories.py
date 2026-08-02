"""
Unit tests for UserRepository and TokenRepository.
Uses in-memory SQLite via the db_session fixture (no real PostgreSQL needed).
"""

import secrets
import uuid
from datetime import timedelta

import pytest
import pytest_asyncio

from app.repositories.user_repository import UserRepository
from app.repositories.token_repository import TokenRepository


# ── UserRepository tests ──────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_user(db_session):
    repo = UserRepository(db_session)
    user = await repo.create(
        email="alice@example.com",
        password_hash="hashed_pw",
        full_name="Alice Smith",
    )
    assert user.id is not None
    assert user.email == "alice@example.com"
    assert user.full_name == "Alice Smith"
    assert user.is_active is True


@pytest.mark.asyncio
async def test_create_user_lowercases_email(db_session):
    repo = UserRepository(db_session)
    user = await repo.create(
        email="ALICE@Example.COM",
        password_hash="h",
        full_name="Alice",
    )
    assert user.email == "alice@example.com"


@pytest.mark.asyncio
async def test_get_by_id_found(db_session):
    repo = UserRepository(db_session)
    created = await repo.create("bob@example.com", "pw", "Bob")
    fetched = await repo.get_by_id(created.id)
    assert fetched is not None
    assert fetched.id == created.id


@pytest.mark.asyncio
async def test_get_by_id_not_found(db_session):
    repo = UserRepository(db_session)
    result = await repo.get_by_id(uuid.uuid4())
    assert result is None


@pytest.mark.asyncio
async def test_get_by_email_found(db_session):
    repo = UserRepository(db_session)
    await repo.create("carol@example.com", "pw", "Carol")
    user = await repo.get_by_email("carol@example.com")
    assert user is not None
    assert user.email == "carol@example.com"


@pytest.mark.asyncio
async def test_get_by_email_case_insensitive(db_session):
    repo = UserRepository(db_session)
    await repo.create("carol@example.com", "pw", "Carol")
    user = await repo.get_by_email("CAROL@Example.COM")
    assert user is not None


@pytest.mark.asyncio
async def test_get_by_email_not_found(db_session):
    repo = UserRepository(db_session)
    result = await repo.get_by_email("nobody@example.com")
    assert result is None


@pytest.mark.asyncio
async def test_email_exists_true(db_session):
    repo = UserRepository(db_session)
    await repo.create("dave@example.com", "pw", "Dave")
    assert await repo.email_exists("dave@example.com") is True


@pytest.mark.asyncio
async def test_email_exists_false(db_session):
    repo = UserRepository(db_session)
    assert await repo.email_exists("ghost@example.com") is False


# ── TokenRepository tests ─────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_and_retrieve_token(db_session):
    user_repo = UserRepository(db_session)
    user = await user_repo.create("eve@example.com", "pw", "Eve")

    token_repo = TokenRepository(db_session)
    plain = secrets.token_urlsafe(64)
    rt = await token_repo.create(user_id=user.id, plain_token=plain)

    assert rt.id is not None
    assert rt.revoked is False
    assert rt.user_id == user.id


@pytest.mark.asyncio
async def test_get_valid_token_by_plain(db_session):
    user_repo = UserRepository(db_session)
    user = await user_repo.create("frank@example.com", "pw", "Frank")

    token_repo = TokenRepository(db_session)
    plain = secrets.token_urlsafe(64)
    await token_repo.create(user_id=user.id, plain_token=plain)

    found = await token_repo.get_valid_by_plain_token(plain)
    assert found is not None
    assert found.user_id == user.id


@pytest.mark.asyncio
async def test_revoke_token(db_session):
    user_repo = UserRepository(db_session)
    user = await user_repo.create("grace@example.com", "pw", "Grace")

    token_repo = TokenRepository(db_session)
    plain = secrets.token_urlsafe(64)
    rt = await token_repo.create(user_id=user.id, plain_token=plain)

    await token_repo.revoke(rt.id)
    await db_session.commit()

    found = await token_repo.get_valid_by_plain_token(plain)
    assert found is None  # revoked — should not be returned


@pytest.mark.asyncio
async def test_expired_token_not_returned(db_session):
    user_repo = UserRepository(db_session)
    user = await user_repo.create("henry@example.com", "pw", "Henry")

    token_repo = TokenRepository(db_session)
    plain = secrets.token_urlsafe(64)
    # Create token that expired 1 second ago
    await token_repo.create(
        user_id=user.id,
        plain_token=plain,
        expires_delta=timedelta(seconds=-1),
    )

    found = await token_repo.get_valid_by_plain_token(plain)
    assert found is None


@pytest.mark.asyncio
async def test_revoke_all_for_user(db_session):
    user_repo = UserRepository(db_session)
    user = await user_repo.create("iris@example.com", "pw", "Iris")

    token_repo = TokenRepository(db_session)
    t1 = secrets.token_urlsafe(64)
    t2 = secrets.token_urlsafe(64)
    await token_repo.create(user_id=user.id, plain_token=t1)
    await token_repo.create(user_id=user.id, plain_token=t2)

    await token_repo.revoke_all_for_user(user.id)
    await db_session.commit()

    assert await token_repo.get_valid_by_plain_token(t1) is None
    assert await token_repo.get_valid_by_plain_token(t2) is None
