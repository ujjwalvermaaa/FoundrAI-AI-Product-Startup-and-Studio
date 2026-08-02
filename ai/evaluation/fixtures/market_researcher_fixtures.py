"""
ai.evaluation.fixtures.market_researcher_fixtures — Eval cases for market_researcher agent.

Module key: market_research
Schema: MarketAnalysis (competitors ≥ 3)
"""

from __future__ import annotations

from ai.evaluation.evaluator import EvalCase
from ai.schemas.market_analysis import VALID_FIXTURE

AGENT_ID = "market_researcher"
MODULE_KEY = "market_research"

# ── Happy path ─────────────────────────────────────────────────────────────────
# Full market analysis with 3 competitors, TAM/SAM/SOM, segments, and trends.
happy_path = EvalCase(
    case_name="happy_path",
    agent_id=AGENT_ID,
    module_key=MODULE_KEY,
    input_fixture={"idea": "AI startup validation platform."},
    expected_output=VALID_FIXTURE,
    should_pass=True,
)

# ── Edge case ──────────────────────────────────────────────────────────────────
# Exactly 3 competitors (minimum allowed).
edge_case = EvalCase(
    case_name="edge_case",
    agent_id=AGENT_ID,
    module_key=MODULE_KEY,
    input_fixture={"idea": "Minimal market research."},
    expected_output={
        "tam": {"value": "1B", "unit": "USD", "notes": ""},
        "sam": {"value": "100M", "unit": "USD", "notes": ""},
        "som": {"value": "10M", "unit": "USD", "notes": ""},
        "segments": ["Founders"],
        "competitors": [
            {"name": "Competitor A", "strengths": "Fast", "weaknesses": "Costly", "market_position": "Leader"},
            {"name": "Competitor B", "strengths": "Cheap", "weaknesses": "Basic", "market_position": "Niche"},
            {"name": "Competitor C", "strengths": "Trusted", "weaknesses": "Slow", "market_position": "Mid"},
        ],
        "trends": ["AI adoption"],
        "summary": "Three-competitor edge case.",
    },
    should_pass=True,
)

# ── Invalid case ───────────────────────────────────────────────────────────────
# Only 2 competitors — below the minimum of 3. Schema should reject this.
invalid_case = EvalCase(
    case_name="invalid_case",
    agent_id=AGENT_ID,
    module_key=MODULE_KEY,
    input_fixture={"idea": "Market with only 2 competitors listed."},
    expected_output={
        "tam": {"value": "1B", "unit": "USD", "notes": ""},
        "sam": {"value": "100M", "unit": "USD", "notes": ""},
        "som": {"value": "10M", "unit": "USD", "notes": ""},
        "segments": ["Founders"],
        "competitors": [
            {"name": "Competitor A", "strengths": "Fast", "weaknesses": "Costly", "market_position": "Leader"},
            {"name": "Competitor B", "strengths": "Cheap", "weaknesses": "Basic", "market_position": "Niche"},
        ],
        "trends": [],
        "summary": "Only 2 competitors — should fail.",
    },
    should_pass=False,
)


def get_cases() -> list[EvalCase]:
    return [happy_path, edge_case, invalid_case]
