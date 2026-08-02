"""
JWT access token encode / decode utilities.
Access tokens are short-lived (15 min by default).
Refresh tokens are stored hashed in the DB — not as JWTs.
"""

from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt

from app.core.config import settings
from app.core.exceptions import UnauthorizedError


def create_access_token(
    subject: str,
    extra_claims: dict[str, Any] | None = None,
    expires_delta: timedelta | None = None,
) -> str:
    """
    Encode a JWT access token.

    Args:
        subject: The user ID (UUID as string) to embed as `sub`.
        extra_claims: Optional additional claims merged into the payload.
        expires_delta: Override the default expiry window.

    Returns:
        Signed JWT string.
    """
    expire = datetime.now(timezone.utc) + (
        expires_delta
        or timedelta(minutes=settings.jwt_access_token_expire_minutes)
    )
    payload: dict[str, Any] = {
        "sub": subject,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "access",
    }
    if extra_claims:
        payload.update(extra_claims)

    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict[str, Any]:
    """
    Decode and validate a JWT access token.

    Returns:
        The decoded payload dict.

    Raises:
        UnauthorizedError: If the token is invalid, expired, or wrong type.
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
    except JWTError:
        raise UnauthorizedError("Invalid or expired access token.")

    if payload.get("type") != "access":
        raise UnauthorizedError("Token type mismatch — expected access token.")

    return payload


def get_subject(token: str) -> str:
    """
    Convenience: decode a token and return the `sub` claim (user ID).

    Raises:
        UnauthorizedError: If `sub` is missing or token is invalid.
    """
    payload = decode_access_token(token)
    sub = payload.get("sub")
    if not sub:
        raise UnauthorizedError("Token is missing subject claim.")
    return str(sub)
