"""
rag_node — retrieves relevant memory chunks before generation.

Responsibility:
  - Build a query from inputs (idea_brief + module_key).
  - Search the project's FAISS index.
  - Also search the shared "knowledge" index for background context.
  - Merge and return chunk dicts in retrieved_chunks.

Graceful degradation: if no index exists for the project, returns an
empty list rather than raising an error.

Test hook: call ``ai.rag.retrieval._set_embed_single(stub_fn)`` before
invoking this node to avoid loading sentence-transformers.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from ai.graphs.state import WorkflowState

logger = logging.getLogger(__name__)

# How many chunks to retrieve from each index source
_TOP_K = 8
_KNOWLEDGE_TOP_K = 4
_KNOWLEDGE_PROJECT_ID = "knowledge"  # shared knowledge index project ID


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _search_safe(
    project_id: str,
    query: str,
    top_k: int,
    source_type: str,
    module_key: str | None,
) -> list[dict[str, Any]]:
    """
    Call retrieval.search() and return a list of chunk dicts.

    Returns [] silently if the index does not exist or any error occurs.
    """
    from ai.rag.indexing import IndexNotFoundError
    from ai.rag.retrieval import search

    try:
        results = search(project_id, query, top_k=top_k)
    except IndexNotFoundError:
        logger.debug(
            "rag_node: no index for project '%s' — returning empty chunks.",
            project_id,
        )
        return []
    except Exception as exc:  # noqa: BLE001
        logger.warning(
            "rag_node: unexpected error searching project '%s': %s",
            project_id,
            exc,
        )
        return []

    chunks: list[dict[str, Any]] = []
    for r in results:
        chunks.append(
            {
                "chunk_id": r.chunk_id,
                "content_text": "",   # populated later by memory_manager if session available
                "score": r.score,
                "source_type": source_type,
                "module_key": module_key,
            }
        )
    return chunks


async def rag_node(state: WorkflowState) -> dict:
    """
    Retrieve memory chunks relevant to the current module generation task.

    Returns a dict with:
      - ``retrieved_chunks``: list of chunk dicts from project + knowledge indexes.
      - ``steps_metadata``: existing list with this step's record appended.
    """
    started_at = _utc_now_iso()
    project_id: str = state.get("project_id", "")
    module_key: str = state.get("module_key", "")
    inputs: dict[str, Any] = state.get("inputs") or {}

    idea_brief: str = inputs.get("idea_brief", "")
    project_name: str = inputs.get("project_name", "")

    # Build query string: combine brief and module context
    query_parts = []
    if idea_brief:
        query_parts.append(idea_brief[:500])   # cap to avoid token bloat
    if module_key:
        query_parts.append(f"module: {module_key}")
    if project_name:
        query_parts.append(f"project: {project_name}")
    query = " ".join(query_parts) if query_parts else "startup project analysis"

    logger.debug(
        "rag_node: project=%s module=%s query=%r",
        project_id,
        module_key,
        query[:80],
    )

    # ── Search project index ───────────────────────────────────────────────
    project_chunks = _search_safe(
        project_id=project_id,
        query=query,
        top_k=_TOP_K,
        source_type="artifact",
        module_key=module_key,
    )

    # ── Search knowledge index ─────────────────────────────────────────────
    knowledge_chunks = _search_safe(
        project_id=_KNOWLEDGE_PROJECT_ID,
        query=query,
        top_k=_KNOWLEDGE_TOP_K,
        source_type="knowledge",
        module_key=None,
    )

    all_chunks: list[dict[str, Any]] = project_chunks + knowledge_chunks

    logger.debug(
        "rag_node: retrieved %d project chunks + %d knowledge chunks.",
        len(project_chunks),
        len(knowledge_chunks),
    )

    # ── Build step record ─────────────────────────────────────────────────
    completed_at = _utc_now_iso()
    step_record: dict[str, Any] = {
        "step_key": "rag_retrieval",
        "started_at": started_at,
        "completed_at": completed_at,
        "metadata": {
            "project_id": project_id,
            "module_key": module_key,
            "project_chunks": len(project_chunks),
            "knowledge_chunks": len(knowledge_chunks),
            "total_chunks": len(all_chunks),
            "query_length": len(query),
        },
    }

    existing_steps: list[dict] = list(state.get("steps_metadata") or [])
    updated_steps = existing_steps + [step_record]

    return {
        "retrieved_chunks": all_chunks,
        "steps_metadata": updated_steps,
    }
