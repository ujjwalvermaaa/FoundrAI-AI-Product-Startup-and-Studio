"""
FAISS index management for the FoundrAI RAG pipeline.

Each project gets its own FAISS IndexFlatIP (inner-product / cosine similarity
on L2-normalized vectors).  Indexes are persisted to disk and cached in memory
for the lifetime of the process so repeated loads are cheap.

Disk layout (one directory per project):
  {FAISS_DATA_DIR}/{project_id}/index.faiss   — FAISS binary
  {FAISS_DATA_DIR}/{project_id}/chunk_ids.json — JSON array of chunk ID strings

Usage:
    from ai.rag.indexing import (
        create_index, add_vectors, save_index, load_index,
        get_or_create_index, delete_index, index_exists,
        IndexNotFoundError,
    )
"""

from __future__ import annotations

import json
import logging
import shutil
from pathlib import Path
from typing import Any

import faiss
import numpy as np

logger = logging.getLogger(__name__)

# ── Constants ─────────────────────────────────────────────────────────────────

_EMBEDDING_DIM = 768
_INDEX_FILENAME = "index.faiss"
_CHUNK_IDS_FILENAME = "chunk_ids.json"


# ── Config helpers ────────────────────────────────────────────────────────────

def _get_faiss_data_dir() -> Path:
    """
    Resolve the FAISS data root directory from app settings (faiss_index_path),
    falling back to the project-level default.
    """
    try:
        from app.core.config import settings
        return Path(settings.faiss_index_path)
    except Exception:
        return Path("/Users/ujjwal/Desktop/FoundrAI/data/faiss")


def _project_dir(project_id: str) -> Path:
    """Return the on-disk directory for a project's index."""
    return _get_faiss_data_dir() / project_id


# ── Exceptions ────────────────────────────────────────────────────────────────

class IndexNotFoundError(FileNotFoundError):
    """Raised when a FAISS index is requested but does not exist on disk."""

    def __init__(self, project_id: str) -> None:
        super().__init__(
            f"No FAISS index found for project '{project_id}'. "
            "Call save_index() first or use get_or_create_index()."
        )
        self.project_id = project_id


# ── In-memory cache ───────────────────────────────────────────────────────────

# { project_id: (index, chunk_ids) }
_cache: dict[str, tuple[faiss.IndexFlatIP, list[str]]] = {}


def _cache_put(project_id: str, index: faiss.IndexFlatIP, chunk_ids: list[str]) -> None:
    _cache[project_id] = (index, chunk_ids)


def _cache_get(project_id: str) -> tuple[faiss.IndexFlatIP, list[str]] | None:
    return _cache.get(project_id)


def _cache_invalidate(project_id: str) -> None:
    _cache.pop(project_id, None)


# ── Public API ────────────────────────────────────────────────────────────────

def create_index(project_id: str) -> faiss.IndexFlatIP:
    """
    Create a new, empty FAISS IndexFlatIP for the given project and cache it.

    Args:
        project_id: Unique string identifier for the project.

    Returns:
        A fresh faiss.IndexFlatIP with ntotal == 0.
    """
    index = faiss.IndexFlatIP(_EMBEDDING_DIM)
    chunk_ids: list[str] = []
    _cache_put(project_id, index, chunk_ids)
    logger.debug("Created new FAISS index for project '%s'.", project_id)
    return index


def add_vectors(
    project_id: str,
    vectors: np.ndarray,
    chunk_ids: list[str],
) -> list[int]:
    """
    Add L2-normalized vectors to the in-memory index for *project_id*.

    The chunk_ids list is kept in parallel with FAISS integer IDs; each new
    vector is appended so FAISS ID ``i`` maps to ``chunk_ids_list[i]``.

    Args:
        project_id: Project whose index to update.
        vectors:    Float32 array of shape (N, 768).  Should already be
                    L2-normalized (as produced by embed() / embed_single()).
        chunk_ids:  List of N string UUIDs identifying each vector's chunk.

    Returns:
        List of integer FAISS IDs assigned to the newly added vectors.

    Raises:
        ValueError: If vectors and chunk_ids lengths don't match, or the
                    embedding dimension is wrong.
    """
    n = len(chunk_ids)
    if vectors.ndim != 2 or vectors.shape[1] != _EMBEDDING_DIM:
        raise ValueError(
            f"Expected vectors of shape (N, {_EMBEDDING_DIM}), "
            f"got {vectors.shape!r}."
        )
    if vectors.shape[0] != n:
        raise ValueError(
            f"vectors has {vectors.shape[0]} rows but chunk_ids has {n} items."
        )
    if n == 0:
        return []

    cached = _cache_get(project_id)
    if cached is None:
        # Auto-create an in-memory index so callers don't have to call
        # create_index explicitly.
        index = create_index(project_id)
        existing_ids: list[str] = []
    else:
        index, existing_ids = cached

    # FAISS IDs are sequential integers starting from current ntotal.
    first_id = index.ntotal
    vecs = vectors.astype(np.float32)
    index.add(vecs)  # type: ignore[arg-type]

    new_ids = list(range(first_id, first_id + n))
    existing_ids.extend(chunk_ids)
    _cache_put(project_id, index, existing_ids)

    logger.debug(
        "Added %d vectors to project '%s' index (now ntotal=%d).",
        n, project_id, index.ntotal,
    )
    return new_ids


def save_index(project_id: str) -> Path:
    """
    Persist the in-memory index for *project_id* to disk.

    Writes:
      - ``{FAISS_DATA_DIR}/{project_id}/index.faiss``
      - ``{FAISS_DATA_DIR}/{project_id}/chunk_ids.json``

    Args:
        project_id: Project whose index to save.

    Returns:
        Path to the project index directory.

    Raises:
        KeyError: If no in-memory index exists for project_id.
    """
    cached = _cache_get(project_id)
    if cached is None:
        raise KeyError(
            f"No in-memory index for project '{project_id}'. "
            "Call create_index() or add_vectors() first."
        )

    index, chunk_ids = cached
    project_dir = _project_dir(project_id)
    project_dir.mkdir(parents=True, exist_ok=True)

    faiss_path = project_dir / _INDEX_FILENAME
    ids_path = project_dir / _CHUNK_IDS_FILENAME

    faiss.write_index(index, str(faiss_path))
    ids_path.write_text(json.dumps(chunk_ids), encoding="utf-8")

    logger.debug(
        "Saved FAISS index for project '%s' to '%s'.",
        project_id, project_dir,
    )
    # Invalidate cache so the freshly saved file is authoritative.
    _cache_invalidate(project_id)
    return project_dir


def load_index(project_id: str) -> faiss.IndexFlatIP:
    """
    Load the FAISS index for *project_id* from disk.

    Results are cached so subsequent calls within the same process do not
    re-read files.

    Args:
        project_id: Project whose index to load.

    Returns:
        The loaded faiss.IndexFlatIP.

    Raises:
        IndexNotFoundError: If the index files do not exist on disk.
    """
    cached = _cache_get(project_id)
    if cached is not None:
        logger.debug("Returning cached FAISS index for project '%s'.", project_id)
        return cached[0]

    project_dir = _project_dir(project_id)
    faiss_path = project_dir / _INDEX_FILENAME
    ids_path = project_dir / _CHUNK_IDS_FILENAME

    if not faiss_path.exists() or not ids_path.exists():
        raise IndexNotFoundError(project_id)

    index: faiss.IndexFlatIP = faiss.read_index(str(faiss_path))  # type: ignore[assignment]
    chunk_ids: list[str] = json.loads(ids_path.read_text(encoding="utf-8"))

    _cache_put(project_id, index, chunk_ids)
    logger.debug(
        "Loaded FAISS index for project '%s' (ntotal=%d).",
        project_id, index.ntotal,
    )
    return index


def get_or_create_index(project_id: str) -> faiss.IndexFlatIP:
    """
    Return the existing index for *project_id* (from cache or disk) or create
    a fresh empty index if none exists.

    Args:
        project_id: Project identifier.

    Returns:
        A faiss.IndexFlatIP — either loaded or freshly created.
    """
    # Fast-path: already in cache
    cached = _cache_get(project_id)
    if cached is not None:
        return cached[0]

    # Try to load from disk
    if index_exists(project_id):
        return load_index(project_id)

    # Nothing on disk — create a fresh index
    return create_index(project_id)


def delete_index(project_id: str) -> None:
    """
    Remove the index directory for *project_id* from disk and evict from cache.

    Safe to call even if the index does not exist.

    Args:
        project_id: Project whose index to delete.
    """
    _cache_invalidate(project_id)
    project_dir = _project_dir(project_id)
    if project_dir.exists():
        shutil.rmtree(project_dir)
        logger.debug("Deleted FAISS index directory for project '%s'.", project_id)


def index_exists(project_id: str) -> bool:
    """
    Check whether a saved FAISS index exists on disk for *project_id*.

    Note: This checks the *on-disk* state only, not the in-memory cache.
    An index may be in-memory (after create_index / add_vectors) but not yet
    on disk until save_index() is called.

    Args:
        project_id: Project to check.

    Returns:
        True if both ``index.faiss`` and ``chunk_ids.json`` exist.
    """
    project_dir = _project_dir(project_id)
    return (
        (project_dir / _INDEX_FILENAME).exists()
        and (project_dir / _CHUNK_IDS_FILENAME).exists()
    )


def get_chunk_ids(project_id: str) -> list[str]:
    """
    Return the list of chunk IDs for *project_id* (in FAISS ID order).

    Tries the cache first, then disk.

    Raises:
        IndexNotFoundError: If no index is found for the project.
    """
    cached = _cache_get(project_id)
    if cached is not None:
        return cached[1]

    # Force load from disk (which also populates cache)
    load_index(project_id)
    return _cache[project_id][1]
