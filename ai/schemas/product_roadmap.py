"""
ai.schemas.product_roadmap — Pydantic schema for the product_strategy module output.
"""

from __future__ import annotations

from pydantic import BaseModel, field_validator


class Feature(BaseModel):
    name: str
    description: str = ""
    priority: str = "medium"


class Phase(BaseModel):
    name: str
    description: str = ""
    features: list[Feature | str | dict]  # min 3 per phase
    timeline: str = ""


class ProductRoadmap(BaseModel):
    phases: list[Phase | dict]  # min 2 phases
    metrics: list[str] | dict = []
    assumptions: list[str] = []
    summary: str = ""

    @field_validator("phases")
    @classmethod
    def phases_min_two(cls, v: list) -> list:
        if len(v) < 2:
            raise ValueError("phases must have at least 2 items")
        return v


# ── Valid fixture ─────────────────────────────────────────────────────────────
VALID_FIXTURE: dict = {
    "phases": [
        {
            "name": "Phase 1 — MVP",
            "description": "Core validation features",
            "features": [
                {"name": "Idea input form", "description": "Basic form", "priority": "high"},
                {"name": "AI validation report", "description": "LLM-generated report", "priority": "high"},
                {"name": "User authentication", "description": "Login/register", "priority": "high"},
            ],
            "timeline": "Q1 2025",
        },
        {
            "name": "Phase 2 — Growth",
            "description": "Expansion features",
            "features": [
                {"name": "Market analysis", "description": "Competitor mapping", "priority": "medium"},
                {"name": "Business model canvas", "description": "Auto-fill canvas", "priority": "medium"},
                {"name": "Export to PDF", "description": "Report export", "priority": "low"},
            ],
            "timeline": "Q2 2025",
        },
    ],
    "metrics": ["MAU growth", "Report completion rate", "NPS"],
    "assumptions": ["Users prefer AI over consultants", "Monthly billing preferred"],
    "summary": "Two-phase roadmap focusing on MVP then growth features.",
}
