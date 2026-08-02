"""
ai.schemas.financial_model — Pydantic schema for the financial_planning module output.
"""

from __future__ import annotations

from pydantic import BaseModel, field_validator


class FinancialModel(BaseModel):
    revenue_drivers: list[str | dict] | dict
    cost_buckets: list[str | dict] | dict
    projection_12_months: list[dict | str]  # 12 entries
    assumptions: list[str]  # min 5
    unit_economics: dict | str = {}
    summary: str = ""

    @field_validator("assumptions")
    @classmethod
    def assumptions_min_five(cls, v: list) -> list:
        if len(v) < 5:
            raise ValueError("assumptions must have at least 5 items")
        return v


# ── Valid fixture ─────────────────────────────────────────────────────────────
VALID_FIXTURE: dict = {
    "revenue_drivers": ["SaaS subscriptions", "Pay-per-report", "Enterprise licenses"],
    "cost_buckets": ["Cloud infrastructure", "Engineering salaries", "Marketing", "Support"],
    "projection_12_months": [
        {"month": "Jan", "revenue": 5000, "costs": 12000},
        {"month": "Feb", "revenue": 7500, "costs": 12000},
        {"month": "Mar", "revenue": 10000, "costs": 13000},
        {"month": "Apr", "revenue": 13000, "costs": 13000},
        {"month": "May", "revenue": 16000, "costs": 14000},
        {"month": "Jun", "revenue": 20000, "costs": 14000},
        {"month": "Jul", "revenue": 24000, "costs": 15000},
        {"month": "Aug", "revenue": 29000, "costs": 15000},
        {"month": "Sep", "revenue": 34000, "costs": 16000},
        {"month": "Oct", "revenue": 40000, "costs": 16000},
        {"month": "Nov", "revenue": 47000, "costs": 17000},
        {"month": "Dec", "revenue": 55000, "costs": 17000},
    ],
    "assumptions": [
        "Average contract value of $99/month",
        "20% monthly growth rate in Year 1",
        "Churn rate of 5% per month",
        "Customer acquisition cost of $150",
        "Gross margin of 75%",
    ],
    "unit_economics": {
        "ltv": "$594",
        "cac": "$150",
        "ltv_cac_ratio": "3.96",
        "payback_period": "1.5 months",
    },
    "summary": "Path to profitability by Month 9 with conservative growth assumptions.",
}
