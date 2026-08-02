"""
Unit tests for JWT encode / decode round-trip.
No DB, no async.
"""

import time
import uuid
from datetime import timedelta

import pytest

from app.auth.jwt import create_access_token, decode_access_token, get_subject
from app.core.exceptions import UnauthorizedError


def test_encode_decode_round_trip():
    user_id = str(uuid.uuid4())
    token = create_access_token(subject=user_id)
    payload = decode_access_token(token)
    assert payload["sub"] == user_id
    assert payload["type"] == "access"


def test_get_subject_returns_user_id():
    user_id = str(uuid.uuid4())
    token = create_access_token(subject=user_id)
    assert get_subject(token) == user_id


def test_expired_token_raises():
    token = create_access_token(
        subject=str(uuid.uuid4()),
        expires_delta=timedelta(seconds=-1),  # already expired
    )
    with pytest.raises(UnauthorizedError):
        decode_access_token(token)


def test_tampered_token_raises():
    token = create_access_token(subject=str(uuid.uuid4()))
    tampered = token[:-4] + "XXXX"
    with pytest.raises(UnauthorizedError):
        decode_access_token(tampered)


def test_wrong_type_raises():
    """A token with type != 'access' should be rejected."""
    from datetime import datetime, timezone
    from jose import jwt as _jwt
    from app.core.config import settings

    payload = {
        "sub": str(uuid.uuid4()),
        "type": "refresh",  # wrong type
        "exp": datetime.now(timezone.utc) + timedelta(hours=1),
    }
    bad_token = _jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    with pytest.raises(UnauthorizedError):
        decode_access_token(bad_token)


def test_extra_claims_preserved():
    token = create_access_token(
        subject="user-123",
        extra_claims={"role": "admin"},
    )
    payload = decode_access_token(token)
    assert payload["role"] == "admin"
