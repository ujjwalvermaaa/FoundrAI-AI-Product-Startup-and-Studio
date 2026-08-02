"""
Integration tests for FAISS index management (Task 23).

These tests exercise the full ai.rag.indexing and ai.rag.retrieval modules
against real FAISS operations.  Each test uses a unique project ID (uuid4) and
cleans up the on-disk index in teardown so nothing is left in data/faiss/.

For tests that call search() we patch embed_single with a fast numpy stub that
produces real L2-normalised float32 vectors without loading the sentence-
transformers model (which requires torch and may crash on some platforms).

Run:
    cd /Users/ujjwal/Desktop/FoundrAI/backend
    poetry run pytest tests/integration/test_faiss_index.py -v
"""

from __future__ import annotations

import uuid

import numpy as np
import pytest

from ai.rag.indexing import (
    IndexNotFoundError,
    add_vectors,
    create_index,
    delete_index,
    get_or_create_index,
    index_exists,
    load_index,
    save_index,
    _cache_invalidate,
)
from ai.rag.retrieval import SearchResult, search


# ── Helpers ───────────────────────────────────────────────────────────────────

def _fresh_project_id() -> str:
    """Return a unique project ID that won't collide with anything."""
    return f"test-project-{uuid.uuid4()}"


def _random_unit_vectors(n: int, dim: int = 768) -> np.ndarray:
    """Return *n* random L2-normalized float32 vectors."""
    rng = np.random.default_rng(42)
    vecs = rng.standard_normal((n, dim)).astype(np.float32)
    norms = np.linalg.norm(vecs, axis=1, keepdims=True)
    return vecs / norms


def _random_chunk_ids(n: int) -> list[str]:
    return [str(uuid.uuid4()) for _ in range(n)]


def _cleanup(project_id: str) -> None:
    """Remove the on-disk index and in-memory cache entry."""
    _cache_invalidate(project_id)
    delete_index(project_id)


def _stub_embed_single(text: str) -> np.ndarray:
    """
    Lightweight stand-in for embed_single that produces a deterministic
    L2-normalised float32 vector from the text's hash.

    This avoids loading the sentence-transformers / torch stack during tests.
    The vector is real and suitable for FAISS inner-product search.
    """
    seed = hash(text) % (2 ** 31)
    rng = np.random.default_rng(seed)
    vec = rng.standard_normal(768).astype(np.float32)
    vec /= np.linalg.norm(vec)
    return vec


@pytest.fixture(autouse=False)
def stub_embed() -> None:
    """
    Override the embed_single used by search() with a fast numpy stub
    so tests don't need torch / sentence-transformers to be loaded.
    The stub produces real L2-normalised float32 vectors.
    """
    from ai.rag.retrieval import _set_embed_single
    _set_embed_single(_stub_embed_single)
    yield
    _set_embed_single(None)  # reset so the real impl is used in production


# ── Tests ─────────────────────────────────────────────────────────────────────

class TestCreateIndex:
    """create_index returns a valid FAISS index with ntotal == 0."""

    def test_create_index(self) -> None:
        import faiss

        pid = _fresh_project_id()
        try:
            idx = create_index(pid)
            assert isinstance(idx, faiss.IndexFlatIP), (
                "Expected faiss.IndexFlatIP, got %s" % type(idx)
            )
            assert idx.ntotal == 0, "New index should be empty (ntotal=0)"
            assert idx.d == 768, "Index dimension should be 768"
        finally:
            _cleanup(pid)


class TestAddVectors:
    """add_vectors increases index.ntotal and returns correct FAISS IDs."""

    def test_add_vectors(self) -> None:
        pid = _fresh_project_id()
        try:
            idx = create_index(pid)
            assert idx.ntotal == 0

            n = 5
            vecs = _random_unit_vectors(n)
            ids_list = _random_chunk_ids(n)
            returned_ids = add_vectors(pid, vecs, ids_list)

            assert idx.ntotal == n, f"Expected ntotal={n}, got {idx.ntotal}"
            assert returned_ids == list(range(n)), (
                f"Expected IDs 0..{n-1}, got {returned_ids}"
            )
        finally:
            _cleanup(pid)

    def test_add_vectors_incremental(self) -> None:
        pid = _fresh_project_id()
        try:
            create_index(pid)
            ids_batch1 = add_vectors(pid, _random_unit_vectors(3), _random_chunk_ids(3))
            ids_batch2 = add_vectors(pid, _random_unit_vectors(4), _random_chunk_ids(4))

            assert ids_batch1 == [0, 1, 2]
            assert ids_batch2 == [3, 4, 5, 6]

            idx = load_index(pid) if index_exists(pid) else get_or_create_index(pid)
            # Index is in-memory at this point (not saved), so use get_or_create
            from ai.rag.indexing import _cache_get
            cached = _cache_get(pid)
            assert cached is not None
            assert cached[0].ntotal == 7
        finally:
            _cleanup(pid)


class TestSaveAndLoadIndex:
    """save_index + load_index round-trip preserves ntotal and search results."""

    def test_save_and_load_index(self) -> None:
        pid = _fresh_project_id()
        try:
            # Build an index with known vectors
            n = 10
            vecs = _random_unit_vectors(n)
            chunk_ids = _random_chunk_ids(n)
            create_index(pid)
            add_vectors(pid, vecs, chunk_ids)

            # Search before save (in-memory)
            query = _random_unit_vectors(1)
            from ai.rag.indexing import _cache_get
            pre_save_index = _cache_get(pid)[0]
            scores_before, ids_before = pre_save_index.search(query, 3)

            # Save to disk
            saved_dir = save_index(pid)
            assert saved_dir.exists(), "Save directory should exist"
            assert (saved_dir / "index.faiss").exists()
            assert (saved_dir / "chunk_ids.json").exists()

            # Load back
            loaded = load_index(pid)
            assert loaded.ntotal == n, (
                f"Loaded index ntotal={loaded.ntotal}, expected {n}"
            )

            # Search after load — results should match
            scores_after, ids_after = loaded.search(query, 3)
            np.testing.assert_array_equal(
                ids_before, ids_after,
                err_msg="Search result IDs should be identical after round-trip",
            )
            np.testing.assert_allclose(
                scores_before, scores_after, rtol=1e-5,
                err_msg="Search scores should be identical after round-trip",
            )
        finally:
            _cleanup(pid)


class TestSearch:
    """search() returns correctly typed, sorted, bounded results."""

    def test_search_returns_results(self, stub_embed: None) -> None:
        pid = _fresh_project_id()
        try:
            n = 20
            vecs = _random_unit_vectors(n)
            chunk_ids = _random_chunk_ids(n)
            create_index(pid)
            add_vectors(pid, vecs, chunk_ids)
            save_index(pid)

            results = search(pid, "startup product market fit", top_k=3)

            assert len(results) <= 3, f"Expected ≤3 results, got {len(results)}"
            assert len(results) > 0, "Expected at least 1 result"
            for r in results:
                assert isinstance(r, SearchResult)
                assert r.score > 0, "Cosine scores should be positive for unit vecs"
                assert isinstance(r.chunk_id, str)
                assert isinstance(r.faiss_id, int)
        finally:
            _cleanup(pid)

    def test_search_empty_index(self, stub_embed: None) -> None:
        """Searching a non-existent project returns []."""
        pid = _fresh_project_id()
        try:
            results = search(pid, "any query")
            assert results == [], f"Expected [], got {results}"
        finally:
            _cleanup(pid)

    def test_search_sorted_descending(self, stub_embed: None) -> None:
        """Results must be sorted by score descending."""
        pid = _fresh_project_id()
        try:
            n = 15
            vecs = _random_unit_vectors(n)
            chunk_ids = _random_chunk_ids(n)
            create_index(pid)
            add_vectors(pid, vecs, chunk_ids)
            save_index(pid)

            results = search(pid, "test query text", top_k=10)
            scores = [r.score for r in results]
            assert scores == sorted(scores, reverse=True), (
                f"Results should be sorted descending by score, got {scores}"
            )
        finally:
            _cleanup(pid)

    def test_search_top_k_respected(self, stub_embed: None) -> None:
        """Results never exceed top_k."""
        pid = _fresh_project_id()
        try:
            n = 50
            vecs = _random_unit_vectors(n)
            chunk_ids = _random_chunk_ids(n)
            create_index(pid)
            add_vectors(pid, vecs, chunk_ids)
            save_index(pid)

            for top_k in (1, 3, 5, 10):
                results = search(pid, "market size analysis", top_k=top_k)
                assert len(results) <= top_k, (
                    f"Expected ≤{top_k} results, got {len(results)}"
                )
        finally:
            _cleanup(pid)


class TestIndexExists:
    """index_exists reflects on-disk state."""

    def test_index_exists(self) -> None:
        pid = _fresh_project_id()
        try:
            assert not index_exists(pid), "index_exists should be False before save"

            create_index(pid)
            assert not index_exists(pid), (
                "index_exists should still be False after create (not yet saved)"
            )

            add_vectors(pid, _random_unit_vectors(3), _random_chunk_ids(3))
            save_index(pid)

            assert index_exists(pid), "index_exists should be True after save"
        finally:
            _cleanup(pid)


class TestDeleteIndex:
    """delete_index removes the on-disk directory."""

    def test_delete_index(self) -> None:
        pid = _fresh_project_id()
        try:
            create_index(pid)
            add_vectors(pid, _random_unit_vectors(3), _random_chunk_ids(3))
            save_index(pid)

            assert index_exists(pid), "Pre-condition: index should exist"

            delete_index(pid)

            assert not index_exists(pid), (
                "index_exists should be False after delete_index"
            )
        finally:
            _cleanup(pid)  # idempotent — already deleted


class TestGetOrCreate:
    """get_or_create_index is idempotent and consistent."""

    def test_get_or_create_returns_same_index(self) -> None:
        """Two calls without any save should return the same in-memory object."""
        pid = _fresh_project_id()
        try:
            idx1 = get_or_create_index(pid)
            idx2 = get_or_create_index(pid)
            assert idx1 is idx2, (
                "get_or_create_index should return the same object on repeated calls"
            )
        finally:
            _cleanup(pid)

    def test_get_or_create_loads_existing(self) -> None:
        """After save + cache eviction, get_or_create loads from disk."""
        pid = _fresh_project_id()
        try:
            n = 5
            create_index(pid)
            add_vectors(pid, _random_unit_vectors(n), _random_chunk_ids(n))
            save_index(pid)  # also evicts cache

            # Cache is now empty; get_or_create should load from disk
            loaded = get_or_create_index(pid)
            assert loaded.ntotal == n, (
                f"Expected ntotal={n} after loading from disk, got {loaded.ntotal}"
            )
        finally:
            _cleanup(pid)

    def test_get_or_create_creates_if_missing(self) -> None:
        """For a brand-new project_id, get_or_create creates an empty index."""
        pid = _fresh_project_id()
        try:
            idx = get_or_create_index(pid)
            assert idx.ntotal == 0, "New index should be empty"
        finally:
            _cleanup(pid)


class TestIndexNotFoundError:
    """load_index raises IndexNotFoundError for unknown project IDs."""

    def test_load_raises_if_missing(self) -> None:
        pid = _fresh_project_id()
        with pytest.raises(IndexNotFoundError):
            load_index(pid)
