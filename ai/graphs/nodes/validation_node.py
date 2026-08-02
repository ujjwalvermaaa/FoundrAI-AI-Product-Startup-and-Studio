"""
validation_node — parses and validates the LLM draft.

Responsibilities:
  - JSON-parse state["current_draft"].
  - Optionally validate against the Pydantic schema for the module_key.
  - On success: sets parsed_output, clears errors.
  - On failure: appends error to errors, sets parsed_output=None.
  - Does NOT retry; graph edges route failures to repair_node.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any

from ai.graphs.state import WorkflowState
from ai.schemas import get_schema_for_module

logger = logging.getLogger(__name__)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


async def validation_node(state: WorkflowState) -> dict:
    """
    Parse and validate the current draft.

    Returns a dict containing:
      - ``parsed_output``: validated dict, or None on failure.
      - ``errors``: updated error list.
      - ``steps_metadata``: existing list with this step's record appended.
    """
    started_at = _utc_now_iso()
    module_key: str = state.get("module_key", "")
    current_draft: str | None = state.get("current_draft")
    existing_errors: list[str] = list(state.get("errors") or [])
    existing_steps: list[dict] = list(state.get("steps_metadata") or [])

    logger.debug("validation_node: module=%s draft_length=%s", module_key, len(current_draft or ""))

    parsed_output: dict | None = None
    validation_error: str | None = None
    validation_method: str = "none"

    # ── JSON parse ────────────────────────────────────────────────────────
    if current_draft is None:
        validation_error = "No draft to validate (current_draft is None)"
    else:
        try:
            parsed_json = json.loads(current_draft)
        except json.JSONDecodeError as exc:
            validation_error = f"JSON parse error: {exc}"
            logger.warning("validation_node: %s", validation_error)
            parsed_json = None

        if parsed_json is not None:
            validation_method = "json"
            # ── Pydantic schema validation ─────────────────────────────────
            schema_class = get_schema_for_module(module_key)
            if schema_class is not None:
                try:
                    validated = schema_class(**parsed_json)
                    parsed_output = validated.model_dump()
                    validation_method = "pydantic"
                    logger.debug("validation_node: Pydantic validation passed for module=%s", module_key)
                except Exception as exc:  # noqa: BLE001
                    validation_error = f"Pydantic validation error: {exc}"
                    logger.warning("validation_node: %s", validation_error)
            else:
                # No schema registered yet — accept raw parsed JSON
                if isinstance(parsed_json, dict):
                    parsed_output = parsed_json
                else:
                    # LLM returned a JSON array or primitive — wrap it
                    parsed_output = {"result": parsed_json}
                logger.debug(
                    "validation_node: no schema for module=%s, accepting parsed JSON",
                    module_key,
                )

    # ── Build step record ─────────────────────────────────────────────────
    completed_at = _utc_now_iso()
    step_record: dict[str, Any] = {
        "step_key": "validation",
        "started_at": started_at,
        "completed_at": completed_at,
        "metadata": {
            "module_key": module_key,
            "validation_method": validation_method,
            "success": parsed_output is not None,
            "error": validation_error,
        },
    }
    updated_steps = existing_steps + [step_record]

    # ── Build result ──────────────────────────────────────────────────────
    if validation_error is not None:
        updated_errors = existing_errors + [validation_error]
        return {
            "parsed_output": None,
            "errors": updated_errors,
            "steps_metadata": updated_steps,
        }

    return {
        "parsed_output": parsed_output,
        "errors": existing_errors,
        "steps_metadata": updated_steps,
    }
