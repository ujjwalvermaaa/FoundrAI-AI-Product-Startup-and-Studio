"""
FastAPI dependency injection helpers.
Used with Depends() in route handlers.
"""

import uuid

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.auth.jwt import get_subject
from app.core.exceptions import UnauthorizedError
from app.database.session import get_db
from app.models.user import User
from app.services.auth_service import AuthService
from sqlalchemy.ext.asyncio import AsyncSession

# Require a Bearer token in the Authorization header
_bearer = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    session: AsyncSession = Depends(get_db),
) -> User:
    """
    Extract and validate the Bearer token, then return the authenticated User.

    Raises:
        UnauthorizedError: If no token is present or it is invalid.
    """
    if credentials is None:
        raise UnauthorizedError("Authorization header is missing.")

    user_id_str = get_subject(credentials.credentials)

    try:
        user_id = uuid.UUID(user_id_str)
    except ValueError:
        raise UnauthorizedError("Token subject is not a valid UUID.")

    service = AuthService(session)
    return await service.get_current_user(user_id)


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Alias that makes it explicit only active users pass through."""
    return current_user
