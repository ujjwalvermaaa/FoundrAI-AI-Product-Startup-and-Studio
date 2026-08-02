"""
reflection_node — advisory quality check on the generated output.

Responsibilities:
  - Ask the LLM to evaluate the parsed output against a yes/no rubric.
  - Record result in step metadata.
  - Append a warning to errors if key rubric items fail (non-blocking).
  - On any error: return gracefully — reflection is advisory.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from ai.graphs.state import WorkflowState
from ai.models.model_factory import ModelFactory
from ai.models.ollama import OllamaError

logger = logging.getLogger(__name__)

_REFLECTION_SYSTEM = """\
You are a quality auditor for AI-generated startup analysis documents.
Evaluate the provided output against the rubric and answer each question
with exactly "yes" or "no" on a separate line.

Rubric:
1. Does the output faithfully reflect the idea brief?
2. Are all required fields populated (no empty or null values where content is expected)?
3. Are there unsupported factual claims not grounded in the provided context?

Respond ONLY with three lines, each starting with "1.", "2.", or "3." followed by "yes" or "no".
Example:
1. yes
2. no
3. yes
"""


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _build_reflection_messages(state: WorkflowState) -> list[dict[str, str]]:
    """Build the reflection prompt messages."""
    parsed_output = state.get("parsed_output")
    retrieved_chunks = state.get("retrieved_chunks") or []
    inputs = state.get("inputs") or {}

    idea_brief = inputs.get("idea_brief", "<not provided>")

    # Summarise retrieved context (first 2 chunks for brevity)
    context_snippets = []
    for chunk in retrieved_chunks[:2]:
        text = chunk.get("content_text", "").strip()
        if text:
            context_snippets.append(text[:300])
    context_block = "\n".join(context_snippets) if context_snippets else "<none>"

    import json
    try:
        output_text = json.dumps(parsed_output, indent=2) if parsed_output else "<none>"
        if len(output_text) > 2000:
            output_text = output_text[:2000] + "\n... (truncated)"
    except (TypeError, ValueError):
        output_text = str(parsed_output)[:2000]

    user_content = (
        f"## Idea Brief\n{idea_brief}\n\n"
        f"## Retrieved Context\n{context_block}\n\n"
        f"## Generated Output\n{output_text}\n\n"
        "Please evaluate the output against the rubric."
    )

    return [
        {"role": "system", "content": _REFLECTION_SYSTEM},
        {"role": "user", "content": user_content},
    ]


def _parse_rubric_response(response: str) -> dict[str, bool | None]:
    """
    Parse the yes/no rubric response.

    Returns a dict with keys "faithful", "fields_populated", "unsupported_claims".
    Values are True/False/None (None = could not parse).
    """
    lines = response.strip().splitlines()
    results: dict[str, bool | None] = {
        "faithful": None,
        "fields_populated": None,
        "unsupported_claims": None,
    }
    keys = ["faithful", "fields_populated", "unsupported_claims"]

    for line in lines:
        line = line.strip().lower()
        for i, key in enumerate(keys, start=1):
            prefix = f"{i}."
            if line.startswith(prefix):
                answer = line[len(prefix):].strip()
                if "yes" in answer:
                    results[key] = True
                elif "no" in answer:
                    results[key] = False
                break

    return results


async def reflection_node(state: WorkflowState) -> dict:
    """
    Perform an advisory reflection pass on the generated output.

    Returns a dict containing:
      - ``steps_metadata``: existing list with this step's record appended.
      - ``errors``: updated list (warning appended if rubric fails).
    """
    started_at = _utc_now_iso()
    agent_id: str = state.get("agent_id", "")
    existing_errors: list[str] = list(state.get("errors") or [])
    existing_steps: list[dict] = list(state.get("steps_metadata") or [])

    logger.debug("reflection_node: starting for agent=%s", agent_id)

    reflection_result: dict[str, Any] = {}
    error_occurred: str | None = None

    try:
        config = ModelFactory.get_agent_config(agent_id)
        client = ModelFactory.get_client()
        messages = _build_reflection_messages(state)

        response = await client.chat(messages, **config.generation_kwargs())
        rubric = _parse_rubric_response(response)
        reflection_result = {
            "response": response,
            "rubric": rubric,
        }
        logger.debug("reflection_node: rubric=%s", rubric)

        # ── Warnings for failing rubric items ─────────────────────────────
        if rubric.get("faithful") is False:
            existing_errors = existing_errors + [
                "Reflection warning: output may not faithfully reflect the idea brief"
            ]
        if rubric.get("fields_populated") is False:
            existing_errors = existing_errors + [
                "Reflection warning: some required fields may be empty or null"
            ]

    except Exception as exc:  # noqa: BLE001
        # Reflection is advisory — never block the pipeline
        error_occurred = str(exc)
        logger.warning("reflection_node: error (non-blocking): %s", exc)
        reflection_result = {"error": error_occurred}

    # ── Build step record ─────────────────────────────────────────────────
    completed_at = _utc_now_iso()
    step_record: dict[str, Any] = {
        "step_key": "reflection",
        "started_at": started_at,
        "completed_at": completed_at,
        "metadata": {
            "agent_id": agent_id,
            "success": error_occurred is None,
            **reflection_result,
        },
    }
    updated_steps = existing_steps + [step_record]

    return {
        "steps_metadata": updated_steps,
        "errors": existing_errors,
    }
