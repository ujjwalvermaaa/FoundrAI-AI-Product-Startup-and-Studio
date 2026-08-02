"""
ai.schemas.business_model_canvas — Pydantic schema for the business_model module output.
"""

from __future__ import annotations

from pydantic import BaseModel, field_validator, model_validator


_CANVAS_FIELDS = [
    "value_proposition",
    "customer_segments",
    "channels",
    "customer_relationships",
    "revenue_streams",
    "key_resources",
    "key_activities",
    "key_partnerships",
    "cost_structure",
]


class BusinessModelCanvas(BaseModel):
    value_proposition: str | list
    customer_segments: str | list
    channels: str | list
    customer_relationships: str | list
    revenue_streams: str | list
    key_resources: str | list
    key_activities: str | list
    key_partnerships: str | list
    cost_structure: str | list
    summary: str = ""

    @model_validator(mode="after")
    def all_canvas_fields_non_empty(self) -> "BusinessModelCanvas":
        for field_name in _CANVAS_FIELDS:
            value = getattr(self, field_name)
            if value == "" or value == [] or value is None:
                raise ValueError(f"canvas field '{field_name}' must not be empty")
        return self


# ── Valid fixture ─────────────────────────────────────────────────────────────
VALID_FIXTURE: dict = {
    "value_proposition": "AI-powered startup validation in minutes.",
    "customer_segments": ["Early-stage founders", "Startup accelerators"],
    "channels": ["Direct web app", "Partner integrations"],
    "customer_relationships": "Self-serve with AI assistance",
    "revenue_streams": ["SaaS subscriptions", "Pay-per-report"],
    "key_resources": ["AI models", "Proprietary dataset", "Engineering team"],
    "key_activities": ["Model training", "Platform development", "Customer support"],
    "key_partnerships": ["Cloud providers", "Accelerator programs"],
    "cost_structure": ["Cloud compute", "Engineering salaries", "Marketing"],
    "summary": "A lean SaaS business model leveraging AI to deliver startup validation.",
}
