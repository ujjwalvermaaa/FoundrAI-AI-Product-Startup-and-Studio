"""
ai.schemas.marketing_plan — Pydantic schema for the marketing_strategy module output.
"""

from __future__ import annotations

from pydantic import BaseModel, field_validator


class MarketingPlan(BaseModel):
    icp: str | dict  # ideal customer profile
    messaging: str | dict
    channels: list[str | dict]  # min 3
    launch_checklist: list[str]  # min 5
    calendar: dict | list | str = {}
    summary: str = ""

    @field_validator("channels")
    @classmethod
    def channels_min_three(cls, v: list) -> list:
        if len(v) < 3:
            raise ValueError("channels must have at least 3 items")
        return v

    @field_validator("launch_checklist")
    @classmethod
    def checklist_min_five(cls, v: list) -> list:
        if len(v) < 5:
            raise ValueError("launch_checklist must have at least 5 items")
        return v


# ── Valid fixture ─────────────────────────────────────────────────────────────
VALID_FIXTURE: dict = {
    "icp": {
        "role": "Founder / CEO",
        "stage": "Pre-seed to Seed",
        "pain": "Spending too much time on research and strategy",
    },
    "messaging": {
        "headline": "Validate your startup idea in minutes, not months.",
        "tagline": "AI-powered insights. Founder-grade strategy.",
        "value_prop": "Replace expensive consultants with instant AI reports.",
    },
    "channels": [
        "Product Hunt launch",
        "LinkedIn content marketing",
        "Startup newsletter sponsorships",
        "Y Combinator community posts",
    ],
    "launch_checklist": [
        "Set up landing page with waitlist",
        "Record demo video",
        "Prepare Product Hunt assets",
        "Reach out to 50 beta users",
        "Schedule launch day social posts",
        "Set up analytics and funnel tracking",
    ],
    "calendar": {
        "week_1": "Landing page live, waitlist open",
        "week_2": "Beta outreach",
        "week_3": "Product Hunt prep",
        "week_4": "Launch day",
    },
    "summary": "A focused GTM strategy targeting early-stage founders via online startup communities.",
}
