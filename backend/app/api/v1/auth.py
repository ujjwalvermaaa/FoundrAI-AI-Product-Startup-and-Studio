"""
Authentication API endpoints — /api/v1/auth/*

POST /auth/register  → 201  Register new user, return tokens
POST /auth/login     → 200  Authenticate, return tokens
POST /auth/refresh   → 200  Rotate refresh token, return new access token
POST /auth/logout    → 204  Revoke all refresh tokens for user
GET  /auth/me        → 200  Return current user profile
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.auth import (
    AccessTokenResponse,
    AuthResponse,
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    UserResponse,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
async def register(
    body: RegisterRequest,
    session: AsyncSession = Depends(get_db),
) -> AuthResponse:
    """
    Create a new user account and return a token pair.

    - **email**: Must be unique
    - **password**: Minimum 8 characters
    - **full_name**: Display name
    """
    service = AuthService(session)
    return await service.register(
        email=body.email,
        password=body.password,
        full_name=body.full_name,
    )


@router.post(
    "/login",
    response_model=AuthResponse,
    status_code=status.HTTP_200_OK,
    summary="Login with email and password",
)
async def login(
    body: LoginRequest,
    session: AsyncSession = Depends(get_db),
) -> AuthResponse:
    """
    Authenticate and return a fresh token pair.
    Returns `INVALID_CREDENTIALS` (401) on wrong email or password.
    """
    service = AuthService(session)
    return await service.login(email=body.email, password=body.password)


@router.post(
    "/refresh",
    response_model=AccessTokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh access token",
)
async def refresh(
    body: RefreshRequest,
    session: AsyncSession = Depends(get_db),
) -> AccessTokenResponse:
    """
    Exchange a valid refresh token for a new access token.
    The old refresh token is **rotated** (revoked and replaced).
    Returns `INVALID_REFRESH_TOKEN` (401) if token is invalid or expired.
    """
    service = AuthService(session)
    return await service.refresh(plain_refresh_token=body.refresh_token)


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Logout — revoke all refresh tokens",
)
async def logout(
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db),
) -> None:
    """
    Revoke all refresh tokens for the authenticated user.
    Effectively logs out all sessions.
    """
    service = AuthService(session)
    await service.logout(user_id=current_user.id)


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current user profile",
)
async def me(
    current_user: User = Depends(get_current_active_user),
) -> UserResponse:
    """Return the authenticated user's profile."""
    return UserResponse.model_validate(current_user)
