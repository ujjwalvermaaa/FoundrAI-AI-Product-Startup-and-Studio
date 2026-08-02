"""
RAG (Retrieval-Augmented Generation) subpackage.

Provides:
  - embeddings: EmbeddingModel singleton for BAAI/bge-base-en-v1.5
  - chunking: content-aware text chunking utilities
  - indexing: FAISS index management (create, add, save, load, delete)
  - retrieval: vector search returning ranked SearchResult objects
"""

from ai.rag.embeddings import EmbeddingModel, embed, embed_single
from ai.rag.chunking import chunk_text
from ai.rag.indexing import (
    IndexNotFoundError,
    add_vectors,
    create_index,
    delete_index,
    get_or_create_index,
    index_exists,
    load_index,
    save_index,
)
from ai.rag.retrieval import SearchResult, search

__all__ = [
    # embeddings
    "EmbeddingModel",
    "embed",
    "embed_single",
    # chunking
    "chunk_text",
    # indexing
    "IndexNotFoundError",
    "add_vectors",
    "create_index",
    "delete_index",
    "get_or_create_index",
    "index_exists",
    "load_index",
    "save_index",
    # retrieval
    "SearchResult",
    "search",
]
