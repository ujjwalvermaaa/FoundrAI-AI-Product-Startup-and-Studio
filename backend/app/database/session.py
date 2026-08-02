"""
Async database session factory and dependency.
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.database.base import engine

# Session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that yields a database session.
    Automatically commits on success or rolls back on error.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def check_db_connection() -> None:
    """
    Verify the database is reachable.
    Raises an exception if connection fails (used by health/ready endpoint).
    """
    from sqlalchemy import text
    async with AsyncSessionLocal() as session:
        await session.execute(text("SELECT 1"))


def get_session_factory() -> async_sessionmaker:
    """
    Return the session factory for use in background tasks.
    Background tasks need their own session — never share the request session.
    """
    return AsyncSessionLocal
