"""
MemoryRepository — all database access for memory_chunks.
"""

import uuid
from typing import Optional

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.memory_chunk import MemoryChunk


class MemoryRepository:
    """Async repository for MemoryChunk CRUD operations."""

    # ── Create ─────────────────────────────────────────────────────────────

    async def create_chunk(
        self, session: AsyncSession, chunk: MemoryChunk
    ) -> MemoryChunk:
        """Persist a single MemoryChunk and return it (with id populated)."""
        session.add(chunk)
        await session.flush()
        await session.refresh(chunk)
        return chunk

    async def bulk_create_chunks(
        self, session: AsyncSession, chunks: list[MemoryChunk]
    ) -> list[MemoryChunk]:
        """Persist a list of MemoryChunk rows in a single flush and return them."""
        for chunk in chunks:
            session.add(chunk)
        await session.flush()
        for chunk in chunks:
            await session.refresh(chunk)
        return chunks

    # ── Read ───────────────────────────────────────────────────────────────

    async def get_chunks_by_project(
        self, session: AsyncSession, project_id: uuid.UUID
    ) -> list[MemoryChunk]:
        """Return all chunks for a project ordered by chunk_index."""
        result = await session.execute(
            select(MemoryChunk)
            .where(MemoryChunk.project_id == project_id)
            .order_by(MemoryChunk.chunk_index)
        )
        return list(result.scalars().all())

    async def get_chunks_by_source(
        self,
        session: AsyncSession,
        project_id: uuid.UUID,
        source_type: str,
        source_id: Optional[uuid.UUID],
    ) -> list[MemoryChunk]:
        """Return all chunks for a specific source (artifact / project_field / knowledge)."""
        stmt = (
            select(MemoryChunk)
            .where(
                MemoryChunk.project_id == project_id,
                MemoryChunk.source_type == source_type,
            )
            .order_by(MemoryChunk.chunk_index)
        )
        if source_id is not None:
            stmt = stmt.where(MemoryChunk.source_id == source_id)
        else:
            stmt = stmt.where(MemoryChunk.source_id.is_(None))
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def get_chunk_by_hash(
        self,
        session: AsyncSession,
        project_id: uuid.UUID,
        content_hash: str,
    ) -> Optional[MemoryChunk]:
        """Return the first chunk with the given content hash in a project, or None."""
        result = await session.execute(
            select(MemoryChunk).where(
                MemoryChunk.project_id == project_id,
                MemoryChunk.content_hash == content_hash,
            )
        )
        return result.scalar_one_or_none()

    async def get_chunk_by_faiss_id(
        self,
        session: AsyncSession,
        project_id: uuid.UUID,
        faiss_vector_id: int,
    ) -> Optional[MemoryChunk]:
        """Return the chunk with the given FAISS vector ID in a project, or None."""
        result = await session.execute(
            select(MemoryChunk).where(
                MemoryChunk.project_id == project_id,
                MemoryChunk.faiss_vector_id == faiss_vector_id,
            )
        )
        return result.scalar_one_or_none()

    # ── Delete ─────────────────────────────────────────────────────────────

    async def delete_chunks_by_source(
        self,
        session: AsyncSession,
        project_id: uuid.UUID,
        source_type: str,
        source_id: Optional[uuid.UUID],
    ) -> int:
        """
        Delete all chunks for a given source and return the count deleted.
        """
        stmt = delete(MemoryChunk).where(
            MemoryChunk.project_id == project_id,
            MemoryChunk.source_type == source_type,
        )
        if source_id is not None:
            stmt = stmt.where(MemoryChunk.source_id == source_id)
        else:
            stmt = stmt.where(MemoryChunk.source_id.is_(None))
        result = await session.execute(stmt)
        await session.flush()
        return result.rowcount
