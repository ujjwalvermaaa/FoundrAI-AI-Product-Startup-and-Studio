"""
Embedding pipeline for FoundrAI RAG system.

Uses BAAI/bge-base-en-v1.5 (768-dim) via sentence-transformers.
Embeddings are L2-normalized for use with FAISS InnerProduct index.

Usage:
    from ai.rag.embeddings import embed, embed_single

    vectors = embed(["text one", "text two"])   # shape (2, 768)
    vec     = embed_single("single text")        # shape (768,)
"""

from __future__ import annotations

import logging
from typing import ClassVar

import numpy as np

logger = logging.getLogger(__name__)

# Default model name — can be overridden by config
_DEFAULT_MODEL = "BAAI/bge-base-en-v1.5"
_EMBEDDING_DIM = 768


def _resolve_model_name() -> str:
    """
    Resolve embedding model name from application settings if available,
    falling back to the hardcoded default.
    """
    try:
        from app.core.config import settings
        return settings.embedding_model
    except Exception:
        return _DEFAULT_MODEL


class EmbeddingModel:
    """
    Singleton wrapper around a SentenceTransformer model.

    The model is loaded lazily — on the first call to embed() — and then
    reused for the lifetime of the process. This avoids repeated ~440MB
    model loads and keeps startup time fast.

    Usage:
        model = EmbeddingModel.get_instance()
        vectors = model.embed(["hello world"])  # shape (1, 768)
    """

    _instance: ClassVar[EmbeddingModel | None] = None
    _st_model: object | None  # SentenceTransformer, typed loosely to defer import

    def __init__(self) -> None:
        self._st_model = None

    # ── Singleton ──────────────────────────────────────────────────────────

    @classmethod
    def get_instance(cls) -> "EmbeddingModel":
        """Return the process-level singleton, creating it if necessary."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        """
        Drop the singleton and unload the model.
        Primarily useful in tests to free memory or force a reload.
        """
        cls._instance = None

    # ── Model loading ──────────────────────────────────────────────────────

    def _ensure_loaded(self) -> None:
        """Load the SentenceTransformer model if it hasn't been loaded yet."""
        if self._st_model is not None:
            return

        model_name = _resolve_model_name()
        logger.info("Loading embedding model: %s", model_name)

        try:
            from sentence_transformers import SentenceTransformer
            self._st_model = SentenceTransformer(model_name)
            logger.info("Embedding model loaded successfully.")
        except Exception as exc:
            logger.error("Failed to load embedding model %r: %s", model_name, exc)
            raise

    # ── Public API ─────────────────────────────────────────────────────────

    def embed(self, texts: list[str]) -> np.ndarray:
        """
        Encode a list of texts into L2-normalized embeddings.

        Args:
            texts: Non-empty list of strings to embed.

        Returns:
            numpy array of shape (N, 768), L2-normalized (unit vectors).
            Suitable for FAISS InnerProduct similarity search.
        """
        if not texts:
            return np.empty((0, _EMBEDDING_DIM), dtype=np.float32)

        self._ensure_loaded()

        # encode() returns a numpy array of shape (N, 768)
        raw: np.ndarray = self._st_model.encode(  # type: ignore[union-attr]
            texts,
            convert_to_numpy=True,
            normalize_embeddings=False,  # we normalise manually below
        )

        # L2-normalize so dot product == cosine similarity (FAISS InnerProduct)
        norms = np.linalg.norm(raw, axis=1, keepdims=True)
        # Avoid division by zero for zero-vectors (edge case)
        norms = np.where(norms == 0, 1.0, norms)
        normalized: np.ndarray = raw / norms

        return normalized.astype(np.float32)

    def embed_single(self, text: str) -> np.ndarray:
        """
        Encode a single text into a 1-D embedding.

        Args:
            text: A single string to embed.

        Returns:
            numpy array of shape (768,), L2-normalized.
        """
        return self.embed([text])[0]


# ── Module-level convenience functions ────────────────────────────────────────
# These delegate to the singleton and are the preferred public interface.

def embed(texts: list[str]) -> np.ndarray:
    """
    Encode a list of texts into L2-normalized embeddings.

    Returns:
        numpy array of shape (N, 768).
    """
    return EmbeddingModel.get_instance().embed(texts)


def embed_single(text: str) -> np.ndarray:
    """
    Encode a single text into a 1-D embedding.

    Returns:
        numpy array of shape (768,).
    """
    return EmbeddingModel.get_instance().embed_single(text)
