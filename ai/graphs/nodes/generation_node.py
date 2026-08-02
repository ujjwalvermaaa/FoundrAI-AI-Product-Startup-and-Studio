"""
generation_node — calls the LLM to produce an initial draft for a module.

Responsibilities:
  - Build messages via PromptBuilder.
  - Call OllamaClient.chat() with agent-specific model config.
  - Strip markdown code fences from the response.
  - Record timing and token metadata in steps_metadata.
  - On OllamaError: append to errors, return current_draft=None.
"""

from __future__ import annotations

import logging
import re
from datetime import datetime, timezone
from typing import Any

from ai.graphs.state import WorkflowState
from ai.models.model_factory import ModelFactory
from ai.models.ollama import OllamaError
from ai.runtime.prompt_builder import PromptBuilder

logger = logging.getLogger(__name__)

# Matches ```json ... ``` or ``` ... ``` (with optional language identifier)
_FENCE_RE = re.compile(r"^```(?:json)?\s*\n?(.*?)\n?```\s*$", re.DOTALL)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _strip_fences(text: str) -> str:
    """Remove markdown code fences, returning the inner content."""
    stripped = text.strip()
    match = _FENCE_RE.match(stripped)
    if match:
        return match.group(1).strip()
    return stripped


async def generation_node(state: WorkflowState) -> dict:
    """
    Generate a raw LLM draft for the current module.

    Returns a dict containing:
      - ``current_draft``: raw (fence-stripped) LLM output, or None on error.
      - ``steps_metadata``: existing list with this step's record appended.
      - ``errors``: updated error list (only if OllamaError occurred).
    """
    started_at = _utc_now_iso()
    agent_id: str = state.get("agent_id", "")
    existing_errors: list[str] = list(state.get("errors") or [])
    existing_steps: list[dict] = list(state.get("steps_metadata") or [])

    logger.debug("generation_node: starting for agent=%s", agent_id)

    # ── Resolve model config & build messages ──────────────────────────────
    config = ModelFactory.get_agent_config(agent_id)
    client = ModelFactory.get_client()

    builder = PromptBuilder()
    messages, prompt_version = builder.build(agent_id, state)

    # ── Call LLM ──────────────────────────────────────────────────────────
    raw_output: str | None = None
    llm_error: str | None = None

    try:
        raw_output = await client.chat(messages, **config.generation_kwargs())
    except OllamaError as exc:
        llm_error = f"OllamaError during generation: {exc}"
        logger.warning("generation_node: %s", llm_error)

    # ── Strip fences ──────────────────────────────────────────────────────
    current_draft: str | None = None
    if raw_output is not None:
        current_draft = _strip_fences(raw_output)
        logger.debug("generation_node: draft length=%d chars", len(current_draft))

    # ── Build step record ─────────────────────────────────────────────────
    completed_at = _utc_now_iso()
    step_metadata: dict[str, Any] = {
        "step_key": "generation",
        "started_at": started_at,
        "completed_at": completed_at,
        "metadata": {
            "agent_id": agent_id,
            "model": config.model,
            "prompt_version": prompt_version,
            "success": raw_output is not None,
        },
    }
    updated_steps = existing_steps + [step_metadata]

    # ── Build result ──────────────────────────────────────────────────────
    result: dict[str, Any] = {
        "current_draft": current_draft,
        "steps_metadata": updated_steps,
    }

    if llm_error is not None:
        result["errors"] = existing_errors + [llm_error]

    return result
