"""
Integration tests for MemoryManager.

Uses an in-memory SQLite DB (via the `db_session` fixture from conftest.py)
and a fast numpy stub for embeddings to avoid loading sentence-transformers.
"""

from __future__ import annotations

import uuid

import numpy as np
import pytest
import pytest_asyncio

from ai.memory.memory_manager import MemoryManager, MemorySearchResult
from ai.rag.indexing import _cache_invalidate, delete_index


# ── Embedding stub ─────────────────────────────────────────────────────────────

def _stub_embed(texts: list[str]) -> np.ndarray:
    """
    Deterministic fast embedding stub — no model loading required.
    Returns L2-normalized random vectors of shape (N, 768).
    """
    rng = np.random.default_rng(42)
    vecs = rng.standard_normal((len(texts), 768)).astype(np.float32)
    norms = np.linalg.norm(vecs, axis=1, keepdims=True)
    norms = np.where(norms == 0, 1.0, norms)
    return vecs / norms


# ── Fixtures ───────────────────────────────────────────────────────────────────

@pytest.fixture
def manager() -> MemoryManager:
    """Return a MemoryManager configured with the fast embedding stub."""
    return MemoryManager(embed_fn=_stub_embed, embedding_model="test-stub")


@pytest.fixture
def project_id() -> str:
    """Return a fresh project UUID string per test."""
    return str(uuid.uuid4())


@pytest.fixture(autouse=True)
def cleanup_faiss(project_id):
    """Clean up FAISS index after each test to avoid cross-test pollution."""
    yield
    _cache_invalidate(project_id)
    delete_index(project_id)


# ── Tests ──────────────────────────────────────────────────────────────────────

class TestIndexBrief:
    async def test_index_brief_creates_chunks(
        self, manager: MemoryManager, db_session, project_id: str
    ):
        """Indexing a brief should create ≥1 MemoryChunk rows in DB."""
        from app.repositories.memory_repository import MemoryRepository

        brief = "This is a detailed project brief about an AI-powered startup platform."
        chunk_ids = await manager.index_brief(project_id, brief, db_session)

        assert len(chunk_ids) >= 1

        repo = MemoryRepository()
        chunks = await repo.get_chunks_by_project(db_session, uuid.UUID(project_id))
        assert len(chunks) == len(chunk_ids)

    async def test_index_brief_returns_chunk_ids(
        self, manager: MemoryManager, db_session, project_id: str
    ):
        """Returned chunk IDs should exactly match the IDs stored in DB."""
        from app.repositories.memory_repository import MemoryRepository

        brief = "A SaaS tool for startup founders to manage AI-generated content."
        chunk_ids = await manager.index_brief(project_id, brief, db_session)

        assert len(chunk_ids) >= 1

        repo = MemoryRepository()
        chunks = await repo.get_chunks_by_project(db_session, uuid.UUID(project_id))
        db_ids = {str(c.id) for c in chunks}
        assert set(chunk_ids) == db_ids


class TestIndexArtifact:
    async def test_index_artifact_creates_chunks(
        self, manager: MemoryManager, db_session, project_id: str
    ):
        """Indexing an artifact should create ≥1 MemoryChunk rows in DB."""
        from app.repositories.memory_repository import MemoryRepository

        artifact_id = str(uuid.uuid4())
        content = (
            "Executive Summary: FoundrAI is a platform that helps startup founders "
            "generate AI-powered business artifacts. The product addresses the gap in "
            "tools available for early-stage entrepreneurs."
        )
        chunk_ids = await manager.index_artifact(
            project_id=project_id,
            artifact_id=artifact_id,
            artifact_type="executive_summary",
            module_key="pitch_deck",
            content_text=content,
            session=db_session,
        )

        assert len(chunk_ids) >= 1

        repo = MemoryRepository()
        chunks = await repo.get_chunks_by_source(
            db_session, uuid.UUID(project_id), "artifact", uuid.UUID(artifact_id)
        )
        assert len(chunks) == len(chunk_ids)


class TestInvalidateArtifact:
    async def test_invalidate_artifact_removes_chunks(
        self, manager: MemoryManager, db_session, project_id: str
    ):
        """After invalidation, chunks for that artifact should be gone from DB."""
        from app.repositories.memory_repository import MemoryRepository

        artifact_id = str(uuid.uuid4())
        content = "This artifact describes the market analysis for the product."
        chunk_ids = await manager.index_artifact(
            project_id=project_id,
            artifact_id=artifact_id,
            artifact_type="market_analysis",
            module_key="research",
            content_text=content,
            session=db_session,
        )
        assert len(chunk_ids) >= 1

        count = await manager.invalidate_artifact(project_id, artifact_id, db_session)
        assert count == len(chunk_ids)

        repo = MemoryRepository()
        remaining = await repo.get_chunks_by_source(
            db_session, uuid.UUID(project_id), "artifact", uuid.UUID(artifact_id)
        )
        assert remaining == []


class TestSearch:
    async def test_search_returns_results(
        self, manager: MemoryManager, db_session, project_id: str
    ):
        """After indexing a brief, search should return MemorySearchResult objects."""
        brief = (
            "FoundrAI is a B2B SaaS platform targeting early-stage startup founders. "
            "It uses AI to generate pitch decks, market analysis, and financial models."
        )
        await manager.index_brief(project_id, brief, db_session)

        results = await manager.search(project_id, "startup AI platform", session=db_session)

        assert len(results) >= 1
        assert all(isinstance(r, MemorySearchResult) for r in results)

    async def test_search_empty_project_returns_empty(
        self, manager: MemoryManager, project_id: str
    ):
        """Searching a project with no index should return an empty list."""
        results = await manager.search(project_id, "anything")
        assert results == []

    async def test_memory_search_result_fields(
        self, manager: MemoryManager, db_session, project_id: str
    ):
        """Each MemorySearchResult must have all required fields populated."""
        brief = "We build AI tools that help founders launch faster."
        await manager.index_brief(project_id, brief, db_session)

        results = await manager.search(project_id, "founders AI tools", session=db_session)

        assert len(results) >= 1
        for r in results:
            assert isinstance(r.chunk_id, str)
            assert len(r.chunk_id) > 0
            assert isinstance(r.content_text, str)
            assert len(r.content_text) > 0
            assert isinstance(r.score, float)
            assert isinstance(r.source_type, str)
            # source_id may be None for project_field
            assert r.source_id is None or isinstance(r.source_id, str)
            assert r.module_key is None or isinstance(r.module_key, str)
            assert isinstance(r.metadata, dict)


class TestDeduplication:
    async def test_dedup_via_content_hash(
        self, manager: MemoryManager, db_session, project_id: str
    ):
        """Indexing the same text twice should produce only one set of DB rows."""
        from app.repositories.memory_repository import MemoryRepository

        brief = "Identical content should be indexed only once for efficiency."
        first_ids = await manager.index_brief(project_id, brief, db_session)
        second_ids = await manager.index_brief(project_id, brief, db_session)

        # Second call should skip all already-indexed chunks
        assert second_ids == []

        repo = MemoryRepository()
        chunks = await repo.get_chunks_by_project(db_session, uuid.UUID(project_id))
        # DB should only contain the chunks from the first indexing
        assert len(chunks) == len(first_ids)
