"""
ai.evaluation.fixtures.investor_writer_fixtures — Eval cases for investor_writer agent.

Module key: investor_documentation
Schema: InvestorDeckOutline (slides ≥ 10)
"""

from __future__ import annotations

from ai.evaluation.evaluator import EvalCase
from ai.schemas.investor_deck_outline import VALID_FIXTURE

AGENT_ID = "investor_writer"
MODULE_KEY = "investor_documentation"

# ── Happy path ─────────────────────────────────────────────────────────────────
# 11 slides — uses VALID_FIXTURE as base.
happy_path = EvalCase(
    case_name="happy_path",
    agent_id=AGENT_ID,
    module_key=MODULE_KEY,
    input_fixture={"idea": "Full investor deck."},
    expected_output=VALID_FIXTURE,
    should_pass=True,
)

# ── Edge case ──────────────────────────────────────────────────────────────────
# Exactly 10 slides (minimum allowed).
edge_case = EvalCase(
    case_name="edge_case",
    agent_id=AGENT_ID,
    module_key=MODULE_KEY,
    input_fixture={"idea": "Minimal 10-slide deck."},
    expected_output={
        "slides": [
            {"title": f"Slide {i}", "bullets": [f"Point {i}"], "notes": ""}
            for i in range(1, 11)
        ],
        "narrative_flow": "Problem → Solution → Market → Ask",
        "key_metrics": ["CAC: $150", "LTV: $594"],
        "summary": "",
    },
    should_pass=True,
)

# ── Invalid case ───────────────────────────────────────────────────────────────
# Only 9 slides — below the minimum of 10. Schema should reject this.
invalid_case = EvalCase(
    case_name="invalid_case",
    agent_id=AGENT_ID,
    module_key=MODULE_KEY,
    input_fixture={"idea": "Deck with only 9 slides — invalid."},
    expected_output={
        "slides": [
            {"title": f"Slide {i}", "bullets": [f"Point {i}"], "notes": ""}
            for i in range(1, 10)  # 9 slides — should fail
        ],
        "narrative_flow": "",
        "key_metrics": [],
        "summary": "Only 9 slides — should fail.",
    },
    should_pass=False,
)


def get_cases() -> list[EvalCase]:
    return [happy_path, edge_case, invalid_case]
