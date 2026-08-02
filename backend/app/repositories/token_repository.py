"""
TokenRepository — all database access for the refresh_tokens table.
Tokens are stored as SHA-256 hashes, never in plain text.
"""

import hashlib
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.refresh_token import RefreshToken


def _hash_token(plain_token: str) -> str:
    """SHA-256 hash a raw token string for safe DB storage."""
    return hashlib.sha256(plain_token.encode()).hexdigest()


class TokenRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self,
        user_id: uuid.UUID,
        plain_token: str,
        expires_delta: timedelta | None = None,
    ) -> RefreshToken:
        """
        Persist a hashed refresh token.

        Args:
            user_id: Owner of this token.
            plain_token: Raw token string (will be hashed before storage).
            expires_delta: Override default expiry.

        Returns:
            The persisted RefreshToken record.
        """
        expiry = datetime.now(timezone.utc) + (
            expires_delta or timedelta(days=settings.jwt_refresh_token_expire_days)
        )
        rt = RefreshToken(
            user_id=user_id,
            token_hash=_hash_token(plain_token),
            expires_at=expiry,
        )
        self._session.add(rt)
        await self._session.flush()
        await self._session.refresh(rt)
        return rt

    async def get_valid_by_plain_token(self, plain_token: str) -> Optional[RefreshToken]:
        """
        Look up a refresh token by its plain value.
        Returns the record only if it is not revoked and not expired.
        """
        token_hash = _hash_token(plain_token)
        result = await self._session.execute(
            select(RefreshToken).where(
                RefreshToken.token_hash == token_hash,
                RefreshToken.revoked.is_(False),
                RefreshToken.expires_at > datetime.now(timezone.utc),
            )
        )
        return result.scalar_one_or_none()

    async def revoke(self, token_id: uuid.UUID) -> None:
        """Mark a single refresh token as revoked."""
        await self._session.execute(
            update(RefreshToken)
            .where(RefreshToken.id == token_id)
            .values(revoked=True)
        )

    async def revoke_all_for_user(self, user_id: uuid.UUID) -> None:
        """Revoke ALL active refresh tokens for a user (logout-everywhere)."""
        await self._session.execute(
            update(RefreshToken)
            .where(
                RefreshToken.user_id == user_id,
                RefreshToken.revoked.is_(False),
            )
            .values(revoked=True)
        )
