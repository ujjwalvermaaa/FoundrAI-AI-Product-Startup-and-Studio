"""
persist_node — persists the validated artifact via the injected callback.

Responsibilities:
  - Skip if parsed_output is None.
  - Call state["persist_callback"](artifact_type, content_json, content_markdown).
  - artifact_type is resolved from module_key via MODULE_ARTIFACT_MAP.
  - On any callback exception: append to errors, do NOT re-raise.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from ai.graphs.state import WorkflowState

logger = logging.getLogger(__name__)

# Maps module_key → artifact_type string stored in the DB
MODULE_ARTIFACT_MAP: dict[str, str] = {
    "idea_validation": "validation_report",
    "market_research": "market_analysis",
    "business_model": "business_model_canvas",
    "product_strategy": "product_roadmap",
    "technical_architecture": "architecture_doc",
    "financial_planning": "financial_model",
    "marketing_strategy": "marketing_plan",
    "investor_documentation": "investor_deck_outline",
}


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


async def persist_node(state: WorkflowState) -> dict:
    """
    Persist the validated artifact using the injected persist_callback.

    Returns a dict containing:
      - ``steps_metadata``: existing list with this step's record appended.
      - ``errors``: updated list (only if persistence fails or output is missing).
    """
    started_at = _utc_now_iso()
    module_key: str = state.get("module_key", "")
    parsed_output: dict | None = state.get("parsed_output")
    persist_callback = state.get("persist_callback")
    existing_errors: list[str] = list(state.get("errors") or [])
    existing_steps: list[dict] = list(state.get("steps_metadata") or [])

    logger.debug("persist_node: module=%s has_output=%s", module_key, parsed_output is not None)

    persist_error: str | None = None
    persisted: bool = False

    # ── Guard: nothing to persist ─────────────────────────────────────────
    if parsed_output is None:
        persist_error = "persist_node: parsed_output is None — skipping persistence"
        logger.warning(persist_error)
    elif persist_callback is None:
        # No callback injected — skip silently (common in unit tests)
        logger.debug("persist_node: no persist_callback set — skipping")
    else:
        artifact_type = MODULE_ARTIFACT_MAP.get(module_key, module_key)
        content_json = parsed_output
        content_markdown: str | None = None  # v1 — markdown generation deferred

        try:
            await persist_callback(artifact_type, content_json, content_markdown)
            persisted = True
            logger.debug(
                "persist_node: callback succeeded for artifact_type=%s", artifact_type
            )
        except Exception as exc:  # noqa: BLE001
            persist_error = f"persist_node: callback raised {type(exc).__name__}: {exc}"
            logger.warning(persist_error)

    # ── Build step record ─────────────────────────────────────────────────
    completed_at = _utc_now_iso()
    artifact_type_used = MODULE_ARTIFACT_MAP.get(module_key, module_key)
    step_record: dict[str, Any] = {
        "step_key": "persist",
        "started_at": started_at,
        "completed_at": completed_at,
        "metadata": {
            "module_key": module_key,
            "artifact_type": artifact_type_used,
            "persisted": persisted,
            "error": persist_error,
        },
    }
    updated_steps = existing_steps + [step_record]

    result: dict[str, Any] = {"steps_metadata": updated_steps}

    if persist_error is not None:
        result["errors"] = existing_errors + [persist_error]

    return result
