"""
context_loader_node — first node in every FoundrAI workflow graph.

Responsibility:
  - Read project inputs and pre-loaded required_artifacts from state.
  - Build a human-readable context_summary that later nodes can reference.
  - Record a step_metadata entry.

This node does NOT query the database; all inputs are injected by
WorkflowService before the graph starts.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from ai.graphs.state import WorkflowState

logger = logging.getLogger(__name__)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _summarise_artifact(artifact_type: str, content: Any) -> str:
    """Return a short one-line summary of an artifact value."""
    if content is None:
        return f"{artifact_type}: <none>"
    if isinstance(content, dict):
        # Use first few keys as a summary
        keys = list(content.keys())[:4]
        return f"{artifact_type}: {{{', '.join(keys)}, ...}}"
    text = str(content)
    return f"{artifact_type}: {text[:120]}..." if len(text) > 120 else f"{artifact_type}: {text}"


async def context_loader_node(state: WorkflowState) -> dict:
    """
    Load and enrich project context from injected inputs and artifacts.

    Returns a dict with:
      - ``inputs``: original inputs enriched with a ``context_summary`` key.
      - ``steps_metadata``: existing list with this step's record appended.
    """
    started_at = _utc_now_iso()
    project_id = state.get("project_id", "")
    module_key = state.get("module_key", "")
    inputs: dict[str, Any] = dict(state.get("inputs") or {})
    required_artifacts: dict[str, Any] = state.get("required_artifacts") or {}

    logger.debug(
        "context_loader_node: project=%s module=%s artifacts=%s",
        project_id,
        module_key,
        list(required_artifacts.keys()),
    )

    # ── Build context summary ─────────────────────────────────────────────
    project_name = inputs.get("project_name", "")
    idea_brief = inputs.get("idea_brief", "")
    industry = inputs.get("industry", "")

    artifact_lines: list[str] = [
        _summarise_artifact(atype, content)
        for atype, content in required_artifacts.items()
    ]
    artifact_block = "\n".join(artifact_lines) if artifact_lines else "<none>"

    context_summary = (
        f"Project: {project_name}\n"
        f"Industry: {industry}\n"
        f"Module: {module_key}\n"
        f"Brief: {idea_brief[:300]}{'...' if len(idea_brief) > 300 else ''}\n"
        f"Prior Artifacts:\n{artifact_block}"
    )

    enriched_inputs = {**inputs, "context_summary": context_summary}

    # ── Build step record ─────────────────────────────────────────────────
    completed_at = _utc_now_iso()
    step_record: dict[str, Any] = {
        "step_key": "context_loader",
        "started_at": started_at,
        "completed_at": completed_at,
        "metadata": {
            "project_id": project_id,
            "module_key": module_key,
            "artifact_count": len(required_artifacts),
            "inputs_keys": list(inputs.keys()),
        },
    }

    existing_steps: list[dict] = list(state.get("steps_metadata") or [])
    updated_steps = existing_steps + [step_record]

    logger.debug(
        "context_loader_node: built context_summary (%d chars), step appended.",
        len(context_summary),
    )

    return {
        "inputs": enriched_inputs,
        "steps_metadata": updated_steps,
    }
