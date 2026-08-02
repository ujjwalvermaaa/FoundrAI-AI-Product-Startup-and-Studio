"""
repair_node — asks the LLM to fix a broken draft.

Responsibilities:
  - Check retry_count; if >= 2, bail out with "Max retries exceeded".
  - Build repair messages via PromptBuilder.build_repair().
  - Call OllamaClient.chat() with repair messages.
  - Return updated current_draft and incremented retry_count.
  - On OllamaError: append to errors, return current_draft=None.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from ai.graphs.state import WorkflowState
from ai.models.model_factory import ModelFactory
from ai.models.ollama import OllamaError
from ai.runtime.prompt_builder import PromptBuilder

logger = logging.getLogger(__name__)

_MAX_RETRIES = 2


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


async def repair_node(state: WorkflowState) -> dict:
    """
    Attempt to repair a broken draft using the LLM.

    Returns a dict containing:
      - ``current_draft``: repaired LLM output, or None on error.
      - ``retry_count``: incremented count.
      - ``steps_metadata``: existing list with this step's record appended.
      - ``errors``: updated error list (on OllamaError or max retries).
    """
    started_at = _utc_now_iso()
    agent_id: str = state.get("agent_id", "")
    retry_count: int = state.get("retry_count") or 0
    existing_errors: list[str] = list(state.get("errors") or [])
    existing_steps: list[dict] = list(state.get("steps_metadata") or [])
    original_output: str = state.get("current_draft") or ""

    logger.debug("repair_node: agent=%s retry_count=%d", agent_id, retry_count)

    # ── Max retries guard ─────────────────────────────────────────────────
    if retry_count >= _MAX_RETRIES:
        error_msg = f"Max retries exceeded ({_MAX_RETRIES})"
        logger.warning("repair_node: %s for agent=%s", error_msg, agent_id)

        completed_at = _utc_now_iso()
        step_record: dict[str, Any] = {
            "step_key": "repair",
            "started_at": started_at,
            "completed_at": completed_at,
            "metadata": {
                "agent_id": agent_id,
                "retry_count": retry_count,
                "skipped": True,
                "reason": error_msg,
            },
        }
        return {
            "current_draft": None,
            "retry_count": retry_count,
            "errors": existing_errors + [error_msg],
            "steps_metadata": existing_steps + [step_record],
        }

    # ── Build repair messages ─────────────────────────────────────────────
    config = ModelFactory.get_agent_config(agent_id)
    client = ModelFactory.get_client()

    builder = PromptBuilder()
    repair_messages = builder.build_repair(
        agent_id=agent_id,
        state=state,
        original_output=original_output,
        errors=existing_errors,
    )

    # ── Call LLM ──────────────────────────────────────────────────────────
    repaired_output: str | None = None
    llm_error: str | None = None

    try:
        repaired_output = await client.chat(repair_messages, **config.generation_kwargs())
    except OllamaError as exc:
        llm_error = f"OllamaError during repair: {exc}"
        logger.warning("repair_node: %s", llm_error)

    # ── Build step record ─────────────────────────────────────────────────
    completed_at = _utc_now_iso()
    step_record = {
        "step_key": "repair",
        "started_at": started_at,
        "completed_at": completed_at,
        "metadata": {
            "agent_id": agent_id,
            "model": config.model,
            "retry_count": retry_count,
            "success": repaired_output is not None,
        },
    }
    updated_steps = existing_steps + [step_record]

    # ── Build result ──────────────────────────────────────────────────────
    result: dict[str, Any] = {
        "current_draft": repaired_output,
        "retry_count": retry_count + 1,
        "steps_metadata": updated_steps,
    }

    if llm_error is not None:
        result["errors"] = existing_errors + [llm_error]
        result["current_draft"] = None

    return result
