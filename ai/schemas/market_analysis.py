"""
ai.schemas.market_analysis — Pydantic schema for the market_research module output.
"""

from __future__ import annotations

from pydantic import BaseModel, field_validator


class MarketSize(BaseModel):
    value: str
    unit: str = "USD"
    notes: str = ""


class Competitor(BaseModel):
    name: str
    strengths: str = ""
    weaknesses: str = ""
    market_position: str = ""


class MarketAnalysis(BaseModel):
    tam: MarketSize | dict
    sam: MarketSize | dict
    som: MarketSize | dict
    segments: list[str | dict] = []
    competitors: list[Competitor | dict]  # min 3
    trends: list[str | dict] = []
    summary: str

    @field_validator("competitors")
    @classmethod
    def competitors_min_three(cls, v: list) -> list:
        if len(v) < 3:
            raise ValueError("competitors must have at least 3 items")
        return v


# ── Valid fixture ─────────────────────────────────────────────────────────────
VALID_FIXTURE: dict = {
    "tam": {"value": "50B", "unit": "USD", "notes": "Global startup tooling market"},
    "sam": {"value": "5B", "unit": "USD", "notes": "English-speaking markets"},
    "som": {"value": "500M", "unit": "USD", "notes": "Year 3 target"},
    "segments": ["Early-stage founders", "Accelerators", "VCs"],
    "competitors": [
        {"name": "Lean Canvas", "strengths": "Simple", "weaknesses": "Manual", "market_position": "Leader"},
        {"name": "Strategyzer", "strengths": "Comprehensive", "weaknesses": "Expensive", "market_position": "Premium"},
        {"name": "Miro", "strengths": "Flexible", "weaknesses": "Not startup-focused", "market_position": "Broad"},
    ],
    "trends": ["AI-assisted strategy", "Remote-first teams", "No-code tools"],
    "summary": "The market is growing rapidly with clear segments and competitive dynamics.",
}
