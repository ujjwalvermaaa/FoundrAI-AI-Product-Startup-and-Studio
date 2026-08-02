"""
UserRepository — all database access for the users table.
Never call ORM directly from services; always go through here.
"""

import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self,
        email: str,
        password_hash: str,
        full_name: str,
    ) -> User:
        """Persist a new user and return the created instance."""
        user = User(
            email=email.lower().strip(),
            password_hash=password_hash,
            full_name=full_name,
        )
        self._session.add(user)
        await self._session.flush()  # assign PK without committing
        await self._session.refresh(user)
        return user

    async def get_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        """Return the user with the given ID, or None."""
        result = await self._session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        """Return the user with the given email (case-insensitive), or None."""
        result = await self._session.execute(
            select(User).where(User.email == email.lower().strip())
        )
        return result.scalar_one_or_none()

    async def email_exists(self, email: str) -> bool:
        """Return True if any user has this email."""
        result = await self._session.execute(
            select(User.id).where(User.email == email.lower().strip())
        )
        return result.scalar_one_or_none() is not None
