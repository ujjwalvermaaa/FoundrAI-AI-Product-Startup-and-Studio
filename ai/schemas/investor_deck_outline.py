"""
ai.schemas.investor_deck_outline — Pydantic schema for the investor_documentation module output.
"""

from __future__ import annotations

from pydantic import BaseModel, field_validator


class Slide(BaseModel):
    title: str
    bullets: list[str] = []
    notes: str = ""


class InvestorDeckOutline(BaseModel):
    slides: list[Slide | dict]  # min 10
    narrative_flow: str = ""
    key_metrics: list[str] | dict = []
    summary: str = ""

    @field_validator("slides")
    @classmethod
    def slides_min_ten(cls, v: list) -> list:
        if len(v) < 10:
            raise ValueError("slides must have at least 10 items")
        return v


# ── Valid fixture ─────────────────────────────────────────────────────────────
VALID_FIXTURE: dict = {
    "slides": [
        {"title": "Cover", "bullets": ["FoundrAI", "AI-Powered Startup Studio"], "notes": ""},
        {"title": "Problem", "bullets": ["Founders waste months on research", "Expensive consultants"], "notes": ""},
        {"title": "Solution", "bullets": ["AI validation in minutes", "8 modules end-to-end"], "notes": ""},
        {"title": "Market Opportunity", "bullets": ["$50B TAM", "$5B SAM", "$500M SOM"], "notes": ""},
        {"title": "Product Demo", "bullets": ["Live walkthrough", "Key features"], "notes": ""},
        {"title": "Business Model", "bullets": ["SaaS $99/month", "Enterprise tiers"], "notes": ""},
        {"title": "Traction", "bullets": ["500 waitlist", "10 beta customers", "NPS 72"], "notes": ""},
        {"title": "Go-to-Market", "bullets": ["Product Hunt", "LinkedIn", "YC communities"], "notes": ""},
        {"title": "Team", "bullets": ["CEO: 2x founder", "CTO: ex-FAANG"], "notes": ""},
        {"title": "Financials", "bullets": ["Path to profitability Month 9", "$2M ARR target Y1"], "notes": ""},
        {"title": "The Ask", "bullets": ["Raising $1.5M pre-seed", "18-month runway"], "notes": ""},
    ],
    "narrative_flow": "Problem → Solution → Market → Product → Business Model → Traction → Team → Ask",
    "key_metrics": ["CAC: $150", "LTV: $594", "Churn: 5%/month", "NPS: 72"],
    "summary": "An 11-slide deck built for pre-seed investors with a clear problem-solution narrative.",
}
