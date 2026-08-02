"""
ai.evaluation.fixtures.idea_validator_fixtures — Eval cases for idea_validator agent.

Module key: idea_validation
Schema: ValidationReport (risks ≥ 3, validation_score 0-100)
"""

from __future__ import annotations

from ai.evaluation.evaluator import EvalCase
from ai.schemas.validation_report import VALID_FIXTURE

AGENT_ID = "idea_validator"
MODULE_KEY = "idea_validation"

# ── Happy path ─────────────────────────────────────────────────────────────────
# Uses the canonical VALID_FIXTURE as expected output.
happy_path = EvalCase(
    case_name="happy_path",
    agent_id=AGENT_ID,
    module_key=MODULE_KEY,
    input_fixture={"idea": "An AI-powered startup validation platform."},
    expected_output=VALID_FIXTURE,
    should_pass=True,
)

# ── Edge case ──────────────────────────────────────────────────────────────────
# Exactly 3 risks (minimum), validation_score=0 (edge of range), minimal fields.
edge_case = EvalCase(
    case_name="edge_case",
    agent_id=AGENT_ID,
    module_key=MODULE_KEY,
    input_fixture={"idea": "A minimal startup idea."},
    expected_output={
        "problem": "Hard to find co-founders.",
        "solution": "A matching platform.",
        "target_customer": {
            "description": "Solo founders",
            "pain_points": ["lonely"],
            "demographics": "20-30",
        },
        "risks": [
            {"risk": "Low traction", "severity": "high", "mitigation": ""},
            {"risk": "Funding gap", "severity": "medium", "mitigation": ""},
            {"risk": "Competition", "severity": "low", "mitigation": ""},
        ],
        "validation_score": 0,
        "recommendations": [],
        "summary": "Minimal but valid.",
    },
    should_pass=True,
)

# ── Invalid case ───────────────────────────────────────────────────────────────
# Only 2 risks — below the minimum of 3. Schema should reject this.
invalid_case = EvalCase(
    case_name="invalid_case",
    agent_id=AGENT_ID,
    module_key=MODULE_KEY,
    input_fixture={"idea": "An idea with insufficient risks."},
    expected_output={
        "problem": "Something hard.",
        "solution": "Something that solves it.",
        "target_customer": {
            "description": "Someone",
            "pain_points": [],
            "demographics": "",
        },
        "risks": [
            {"risk": "Risk A", "severity": "high", "mitigation": ""},
            {"risk": "Risk B", "severity": "low", "mitigation": ""},
        ],
        "validation_score": 50,
        "recommendations": [],
        "summary": "Only 2 risks — should fail validation.",
    },
    should_pass=False,
)


def get_cases() -> list[EvalCase]:
    return [happy_path, edge_case, invalid_case]
