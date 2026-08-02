"""
AuthService — business logic for register, login, refresh, and logout.
All DB access goes through repositories; no direct ORM calls here.
"""

import secrets
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt import create_access_token
from app.auth.password import hash_password, verify_password
from app.core.exceptions import (
    AccountDisabledError,
    EmailAlreadyExistsError,
    InvalidCredentialsError,
    InvalidRefreshTokenError,
)
from app.models.user import User
from app.repositories.token_repository import TokenRepository
from app.repositories.user_repository import UserRepository
from app.schemas.auth import AccessTokenResponse, AuthResponse, UserResponse


def _make_user_response(user: User) -> UserResponse:
    return UserResponse.model_validate(user)


def _generate_refresh_token() -> str:
    """Generate a cryptographically secure random refresh token string."""
    return secrets.token_urlsafe(64)


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._users = UserRepository(session)
        self._tokens = TokenRepository(session)

    async def register(
        self,
        email: str,
        password: str,
        full_name: str,
    ) -> AuthResponse:
        """
        Register a new user and return token pair.

        Raises:
            EmailAlreadyExistsError: If the email is taken.
        """
        if await self._users.email_exists(email):
            raise EmailAlreadyExistsError(email)

        user = await self._users.create(
            email=email,
            password_hash=hash_password(password),
            full_name=full_name,
        )

        access_token = create_access_token(subject=str(user.id))
        plain_refresh = _generate_refresh_token()
        await self._tokens.create(user_id=user.id, plain_token=plain_refresh)

        return AuthResponse(
            user=_make_user_response(user),
            access_token=access_token,
            refresh_token=plain_refresh,
        )

    async def login(self, email: str, password: str) -> AuthResponse:
        """
        Authenticate a user and return a fresh token pair.

        Raises:
            InvalidCredentialsError: If email not found or password wrong.
            AccountDisabledError: If the user account is inactive.
        """
        user = await self._users.get_by_email(email)
        if not user or not verify_password(password, user.password_hash):
            raise InvalidCredentialsError()

        if not user.is_active:
            raise AccountDisabledError()

        access_token = create_access_token(subject=str(user.id))
        plain_refresh = _generate_refresh_token()
        await self._tokens.create(user_id=user.id, plain_token=plain_refresh)

        return AuthResponse(
            user=_make_user_response(user),
            access_token=access_token,
            refresh_token=plain_refresh,
        )

    async def refresh(self, plain_refresh_token: str) -> AccessTokenResponse:
        """
        Rotate a refresh token and issue a new access token.

        Raises:
            InvalidRefreshTokenError: If the token is invalid, expired, or revoked.
        """
        rt = await self._tokens.get_valid_by_plain_token(plain_refresh_token)
        if not rt:
            raise InvalidRefreshTokenError()

        # Revoke old token (rotation)
        await self._tokens.revoke(rt.id)

        # Issue new refresh token
        plain_new = _generate_refresh_token()
        await self._tokens.create(user_id=rt.user_id, plain_token=plain_new)

        access_token = create_access_token(subject=str(rt.user_id))

        return AccessTokenResponse(access_token=access_token)

    async def logout(self, user_id: uuid.UUID) -> None:
        """Revoke all refresh tokens for the user (full logout)."""
        await self._tokens.revoke_all_for_user(user_id)

    async def get_current_user(self, user_id: uuid.UUID) -> User:
        """
        Load a user by ID for the get_current_user dependency.

        Raises:
            InvalidCredentialsError: If user not found.
            AccountDisabledError: If user is inactive.
        """
        user = await self._users.get_by_id(user_id)
        if not user:
            raise InvalidCredentialsError()
        if not user.is_active:
            raise AccountDisabledError()
        return user
