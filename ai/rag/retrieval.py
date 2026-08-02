"""
Vector retrieval for the FoundrAI RAG pipeline.

Embeds a query string, searches the project's FAISS index, and returns
ranked SearchResult objects sorted by cosine-similarity score (descending).

Usage:
    from ai.rag.retrieval import search, SearchResult

    results = search("my-project-id", "What is the TAM?", top_k=5)
    for r in results:
        print(r.chunk_id, r.score)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Callable

import numpy as np

logger = logging.getLogger(__name__)


# ── Embedding hook ─────────────────────────────────────────────────────────────
# Stored as a module-level callable so tests can monkeypatch it without
# triggering torch / sentence-transformers at import time.
# The real function is loaded lazily on first call.

_embed_single_fn: Callable[[str], np.ndarray] | None = None


def _get_embed_single() -> Callable[[str], np.ndarray]:
    """Return the active embed_single callable (lazy-loaded)."""
    global _embed_single_fn
    if _embed_single_fn is None:
        from ai.rag.embeddings import embed_single as _real
        _embed_single_fn = _real
    return _embed_single_fn


def _set_embed_single(fn: Callable[[str], np.ndarray] | None) -> None:
    """
    Override the embed_single implementation used by search().

    Pass None to revert to the real sentence-transformers implementation.
    This is primarily for testing.
    """
    global _embed_single_fn
    _embed_single_fn = fn


# ── Data model ────────────────────────────────────────────────────────────────

@dataclass(frozen=True, order=False)
class SearchResult:
    """A single result from a FAISS similarity search."""

    chunk_id: str   # string UUID of the matching chunk
    score: float    # inner-product (cosine) similarity, higher is more similar
    faiss_id: int   # integer FAISS vector ID


# ── Public API ────────────────────────────────────────────────────────────────

def search(
    project_id: str,
    query: str,
    top_k: int = 8,
) -> list[SearchResult]:
    """
    Embed *query* and search the FAISS index for *project_id*.

    Args:
        project_id: Project whose index to search.
        query:      Natural-language query string.
        top_k:      Maximum number of results to return.

    Returns:
        List of SearchResult objects sorted by score descending.
        Returns [] if the index does not exist or is empty.
    """
    from ai.rag.indexing import IndexNotFoundError, get_chunk_ids, load_index

    # ── Load index ────────────────────────────────────────────────────────
    try:
        index = load_index(project_id)
    except IndexNotFoundError:
        logger.debug(
            "No FAISS index for project '%s'; returning empty results.", project_id
        )
        return []

    if index.ntotal == 0:
        logger.debug(
            "FAISS index for project '%s' is empty; returning empty results.",
            project_id,
        )
        return []

    # ── Embed query ───────────────────────────────────────────────────────
    embed_fn = _get_embed_single()
    query_vec: np.ndarray = embed_fn(query)                      # shape (768,)
    query_matrix = query_vec.reshape(1, -1).astype(np.float32)   # shape (1, 768)

    # ── Search ─────────────────────────────────────────────────────────────
    k = min(top_k, index.ntotal)
    scores_matrix, ids_matrix = index.search(query_matrix, k)    # type: ignore[arg-type]

    scores: np.ndarray = scores_matrix[0]   # shape (k,)
    faiss_ids: np.ndarray = ids_matrix[0]   # shape (k,)

    # ── Build results ──────────────────────────────────────────────────────
    chunk_ids_list = get_chunk_ids(project_id)
    results: list[SearchResult] = []

    for faiss_id, score in zip(faiss_ids.tolist(), scores.tolist()):
        if faiss_id < 0:
            # FAISS returns -1 for padding when fewer results than k exist
            continue
        if faiss_id >= len(chunk_ids_list):
            logger.warning(
                "FAISS returned ID %d but chunk_ids list has only %d entries "
                "(project '%s'). Skipping.",
                faiss_id, len(chunk_ids_list), project_id,
            )
            continue
        results.append(
            SearchResult(
                chunk_id=chunk_ids_list[faiss_id],
                score=float(score),
                faiss_id=int(faiss_id),
            )
        )

    # Ensure descending order by score (FAISS usually returns sorted, but
    # be explicit to satisfy the acceptance criteria).
    results.sort(key=lambda r: r.score, reverse=True)

    logger.debug(
        "search(project='%s', top_k=%d) → %d results.",
        project_id, top_k, len(results),
    )
    return results
