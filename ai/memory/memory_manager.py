"""
MemoryManager — core orchestrator for FoundrAI's project memory system.

Handles indexing text content (artifacts, project briefs) into FAISS and the
memory_chunks DB table, plus retrieval (semantic search) and invalidation.

Usage:
    from ai.memory.memory_manager import MemoryManager, MemorySearchResult

    manager = MemoryManager()
    chunk_ids = await manager.index_brief(project_id, brief_text, session)
    results   = await manager.search(project_id, "What is the target market?")
"""

from __future__ import annotations

import hashlib
import logging
import uuid
from dataclasses import dataclass, field
from typing import Callable, Optional

import numpy as np

logger = logging.getLogger(__name__)

# ── Data model ────────────────────────────────────────────────────────────────

@dataclass
class MemorySearchResult:
    """A single result from a semantic memory search."""

    chunk_id: str
    content_text: str
    score: float
    source_type: str
    source_id: Optional[str]
    module_key: Optional[str]
    metadata: dict = field(default_factory=dict)


# ── Manager ───────────────────────────────────────────────────────────────────

class MemoryManager:
    """
    Orchestrates chunking, embedding, FAISS indexing, and DB persistence
    for project memory chunks.

    Args:
        embed_fn:  Optional callable ``(texts: list[str]) -> np.ndarray`` that
                   returns an (N, 768) float32 array of L2-normalized embeddings.
                   Defaults to the production ``ai.rag.embeddings.embed`` function.
                   Pass a stub in tests to avoid loading sentence-transformers.
        embedding_model: Name recorded in MemoryChunk.embedding_model.
    """

    def __init__(
        self,
        embed_fn: Optional[Callable[[list[str]], np.ndarray]] = None,
        embedding_model: str = "BAAI/bge-base-en-v1.5",
    ) -> None:
        self._embed_fn = embed_fn
        self._embedding_model = embedding_model

    # ── Private helpers ────────────────────────────────────────────────────

    def _embed(self, texts: list[str]) -> np.ndarray:
        """Call the configured embed function (lazy-load real one if needed)."""
        if self._embed_fn is not None:
            return self._embed_fn(texts)
        from ai.rag.embeddings import embed
        return embed(texts)

    @staticmethod
    def _content_hash(text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    # ── Indexing ───────────────────────────────────────────────────────────

    async def _index_chunks(
        self,
        project_id: str,
        texts: list[str],
        source_type: str,
        source_id: Optional[str],
        module_key: Optional[str],
        session,
    ) -> list[str]:
        """
        Core indexing logic shared by index_artifact and index_brief.

        For each text chunk:
        1. Compute content_hash; skip if already in DB (dedup).
        2. Embed all new chunks in one batch.
        3. Add vectors to FAISS + save index.
        4. Bulk-insert MemoryChunk rows to DB.

        Returns list of chunk UUIDs that were newly indexed.
        """
        from ai.rag.chunking import chunk_text
        from ai.rag.indexing import add_vectors, save_index
        from app.models.memory_chunk import MemoryChunk
        from app.repositories.memory_repository import MemoryRepository

        repo = MemoryRepository()
        proj_uuid = uuid.UUID(project_id)
        src_uuid = uuid.UUID(source_id) if source_id else None

        # Chunk each text
        all_chunks: list[tuple[int, str]] = []  # (global_index, chunk_text)
        global_idx = 0
        for text in texts:
            for chunk in chunk_text(text):
                all_chunks.append((global_idx, chunk))
                global_idx += 1

        if not all_chunks:
            return []

        # Dedup: skip chunks already in DB by content_hash
        new_chunks: list[tuple[int, str]] = []
        for idx, chunk_txt in all_chunks:
            h = self._content_hash(chunk_txt)
            existing = await repo.get_chunk_by_hash(session, proj_uuid, h)
            if existing is not None:
                logger.debug("Skipping duplicate chunk (hash=%s)", h)
            else:
                new_chunks.append((idx, chunk_txt))

        if not new_chunks:
            return []

        # Embed all new chunks in one batch
        texts_to_embed = [c for _, c in new_chunks]
        vectors = self._embed(texts_to_embed)

        # Add to FAISS and get assigned IDs
        chunk_tmp_ids = [str(uuid.uuid4()) for _ in new_chunks]
        faiss_ids = add_vectors(project_id, vectors, chunk_tmp_ids)
        save_index(project_id)

        # Build ORM rows
        orm_chunks: list[MemoryChunk] = []
        for (chunk_idx, chunk_txt), faiss_id in zip(new_chunks, faiss_ids):
            orm_chunks.append(
                MemoryChunk(
                    project_id=proj_uuid,
                    source_type=source_type,
                    source_id=src_uuid,
                    module_key=module_key,
                    chunk_index=chunk_idx,
                    content_text=chunk_txt,
                    content_hash=self._content_hash(chunk_txt),
                    embedding_model=self._embedding_model,
                    faiss_vector_id=faiss_id,
                    metadata_json=None,
                )
            )

        persisted = await repo.bulk_create_chunks(session, orm_chunks)
        return [str(c.id) for c in persisted]

    # ── Public API ─────────────────────────────────────────────────────────

    async def index_artifact(
        self,
        project_id: str,
        artifact_id: str,
        artifact_type: str,
        module_key: str,
        content_text: str,
        session,
    ) -> list[str]:
        """
        Chunk, embed, and index an artifact's content into FAISS + DB.

        Args:
            project_id:   UUID string of the project.
            artifact_id:  UUID string of the artifact (used as source_id).
            artifact_type: The artifact type label (for logging / metadata).
            module_key:   Module key the artifact belongs to.
            content_text: Full text content to index.
            session:      AsyncSession to use for DB writes.

        Returns:
            List of newly created chunk UUID strings.
        """
        logger.info(
            "Indexing artifact %s (%s) for project %s",
            artifact_id, artifact_type, project_id,
        )
        return await self._index_chunks(
            project_id=project_id,
            texts=[content_text],
            source_type="artifact",
            source_id=artifact_id,
            module_key=module_key,
            session=session,
        )

    async def index_brief(
        self,
        project_id: str,
        brief_text: str,
        session,
    ) -> list[str]:
        """
        Chunk, embed, and index a project brief into FAISS + DB.

        Args:
            project_id: UUID string of the project.
            brief_text: Full brief / description text.
            session:    AsyncSession to use for DB writes.

        Returns:
            List of newly created chunk UUID strings.
        """
        logger.info("Indexing brief for project %s", project_id)
        return await self._index_chunks(
            project_id=project_id,
            texts=[brief_text],
            source_type="project_field",
            source_id=None,
            module_key=None,
            session=session,
        )

    async def invalidate_artifact(
        self,
        project_id: str,
        artifact_id: str,
        session,
    ) -> int:
        """
        Remove all memory chunks for the given artifact from the DB.

        Note: FAISS vectors are orphaned (not rebuilt) — acceptable for v1.

        Args:
            project_id:  UUID string of the project.
            artifact_id: UUID string of the artifact whose chunks to remove.
            session:     AsyncSession for DB deletes.

        Returns:
            Number of chunks deleted.
        """
        from app.repositories.memory_repository import MemoryRepository

        repo = MemoryRepository()
        proj_uuid = uuid.UUID(project_id)
        src_uuid = uuid.UUID(artifact_id)
        count = await repo.delete_chunks_by_source(
            session, proj_uuid, "artifact", src_uuid
        )
        logger.info(
            "Invalidated %d chunks for artifact %s (project %s)",
            count, artifact_id, project_id,
        )
        return count

    async def search(
        self,
        project_id: str,
        query: str,
        top_k: int = 8,
        session=None,
    ) -> list[MemorySearchResult]:
        """
        Semantically search indexed memory chunks for the given project.

        Args:
            project_id: UUID string of the project to search.
            query:      Natural-language query string.
            top_k:      Maximum number of results.
            session:    AsyncSession for DB lookups. Required for enriched results.

        Returns:
            List of MemorySearchResult ordered by relevance score (descending).
            Returns [] if no index exists or the index is empty.
        """
        from ai.rag.retrieval import SearchResult, _set_embed_single, search as faiss_search

        # Inject our embed function into retrieval module if using a custom one
        if self._embed_fn is not None:
            def _single(text: str) -> np.ndarray:
                return self._embed_fn([text])[0]  # type: ignore[index]
            _set_embed_single(_single)

        try:
            raw_results: list[SearchResult] = faiss_search(project_id, query, top_k)
        finally:
            # Restore default embed_single if we overrode it
            if self._embed_fn is not None:
                _set_embed_single(None)

        if not raw_results:
            return []

        if session is None:
            # No DB session — return partial results without content enrichment
            return [
                MemorySearchResult(
                    chunk_id=r.chunk_id,
                    content_text="",
                    score=r.score,
                    source_type="",
                    source_id=None,
                    module_key=None,
                    metadata={},
                )
                for r in raw_results
            ]

        from app.repositories.memory_repository import MemoryRepository

        repo = MemoryRepository()
        proj_uuid = uuid.UUID(project_id)
        enriched: list[MemorySearchResult] = []

        for r in raw_results:
            chunk = await repo.get_chunk_by_faiss_id(
                session, proj_uuid, r.faiss_id
            )
            if chunk is None:
                # Orphaned FAISS vector (e.g., after invalidate) — skip
                continue
            enriched.append(
                MemorySearchResult(
                    chunk_id=str(chunk.id),
                    content_text=chunk.content_text,
                    score=r.score,
                    source_type=chunk.source_type,
                    source_id=str(chunk.source_id) if chunk.source_id else None,
                    module_key=chunk.module_key,
                    metadata=chunk.metadata_json or {},
                )
            )

        return enriched
