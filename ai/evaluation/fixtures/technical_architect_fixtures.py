"""
ai.evaluation.fixtures.technical_architect_fixtures — Eval cases for technical_architect agent.

Module key: technical_architecture
Schema: ArchitectureDoc (components required, stack_recommendations, security_considerations)
"""

from __future__ import annotations

from ai.evaluation.evaluator import EvalCase
from ai.schemas.architecture_doc import VALID_FIXTURE

AGENT_ID = "technical_architect"
MODULE_KEY = "technical_architecture"

# ── Happy path ─────────────────────────────────────────────────────────────────
# Full architecture with components, stack, security, data_flows, scalability.
happy_path = EvalCase(
    case_name="happy_path",
    agent_id=AGENT_ID,
    module_key=MODULE_KEY,
    input_fixture={"idea": "AI startup platform architecture."},
    expected_output=VALID_FIXTURE,
    should_pass=True,
)

# ── Edge case ──────────────────────────────────────────────────────────────────
# Minimal valid values for all fields — single-item lists, short strings.
edge_case = EvalCase(
    case_name="edge_case",
    agent_id=AGENT_ID,
    module_key=MODULE_KEY,
    input_fixture={"idea": "Minimal architecture."},
    expected_output={
        "components": ["API server"],
        "stack_recommendations": ["Python"],
        "data_flows": "User → API",
        "security_considerations": "JWT auth",
        "scalability_notes": "",
        "summary": "",
    },
    should_pass=True,
)

# ── Invalid case ───────────────────────────────────────────────────────────────
# Missing required `components` field entirely — Pydantic will raise ValidationError.
invalid_case = EvalCase(
    case_name="invalid_case",
    agent_id=AGENT_ID,
    module_key=MODULE_KEY,
    input_fixture={"idea": "Architecture without components."},
    expected_output={
        # "components" intentionally omitted
        "stack_recommendations": ["Python"],
        "data_flows": "User → API",
        "security_considerations": "JWT auth",
        "scalability_notes": "",
        "summary": "Missing components — should fail.",
    },
    should_pass=False,
)


def get_cases() -> list[EvalCase]:
    return [happy_path, edge_case, invalid_case]
