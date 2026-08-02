"""
ai.schemas.validation_report — Pydantic schema for the idea_validation module output.
"""

from __future__ import annotations

from pydantic import BaseModel, field_validator


class RiskItem(BaseModel):
    risk: str
    severity: str  # "high" | "medium" | "low"
    mitigation: str = ""


class TargetCustomer(BaseModel):
    description: str
    pain_points: list[str] = []
    demographics: str = ""


class ValidationReport(BaseModel):
    problem: str
    solution: str
    target_customer: TargetCustomer | dict  # allow dict for flexibility
    risks: list[RiskItem | dict]  # min 3 items
    validation_score: int  # 0-100
    recommendations: list[str] = []
    summary: str

    @field_validator("risks")
    @classmethod
    def risks_min_three(cls, v: list) -> list:
        if len(v) < 3:
            raise ValueError("risks must have at least 3 items")
        return v

    @field_validator("validation_score")
    @classmethod
    def score_range(cls, v: int) -> int:
        if not (0 <= v <= 100):
            raise ValueError("validation_score must be 0-100")
        return v


# ── Valid fixture ─────────────────────────────────────────────────────────────
VALID_FIXTURE: dict = {
    "problem": "Founders struggle to validate startup ideas quickly.",
    "solution": "An AI-powered validation platform that gives instant feedback.",
    "target_customer": {
        "description": "Early-stage founders",
        "pain_points": ["slow validation", "expensive consultants"],
        "demographics": "25-40 years old, tech-savvy",
    },
    "risks": [
        {"risk": "Low adoption", "severity": "high", "mitigation": "Marketing push"},
        {"risk": "Data quality", "severity": "medium", "mitigation": "Human review"},
        {"risk": "Competition", "severity": "low", "mitigation": "Differentiate on UX"},
    ],
    "validation_score": 72,
    "recommendations": ["Run user interviews", "Build MVP quickly"],
    "summary": "The idea has strong potential with manageable risks.",
}
