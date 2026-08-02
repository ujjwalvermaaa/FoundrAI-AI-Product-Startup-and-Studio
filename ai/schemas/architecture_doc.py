"""
ai.schemas.architecture_doc — Pydantic schema for the technical_architecture module output.
"""

from __future__ import annotations

from pydantic import BaseModel


class ArchitectureDoc(BaseModel):
    components: list[str | dict] | dict
    stack_recommendations: list[str] | dict | str
    data_flows: list[str | dict] | str = []
    security_considerations: str | list
    scalability_notes: str | list = ""
    summary: str = ""


# ── Valid fixture ─────────────────────────────────────────────────────────────
VALID_FIXTURE: dict = {
    "components": [
        {"name": "FastAPI backend", "role": "REST API and business logic"},
        {"name": "PostgreSQL", "role": "Primary database"},
        {"name": "LangGraph", "role": "AI workflow orchestration"},
        {"name": "Next.js frontend", "role": "User interface"},
    ],
    "stack_recommendations": [
        "Python 3.12 + FastAPI for backend",
        "PostgreSQL with asyncpg for async DB access",
        "LangGraph for LLM workflow management",
        "Next.js 14 with App Router for frontend",
    ],
    "data_flows": [
        "User submits idea → API → LangGraph workflow → AI nodes → validated output",
        "Validated output stored in PostgreSQL → returned to frontend",
    ],
    "security_considerations": [
        "JWT-based authentication with short-lived tokens",
        "Row-level security via user_id scoping",
        "API key secrets stored in environment variables",
    ],
    "scalability_notes": "Horizontal scaling via stateless API instances; DB read replicas for load.",
    "summary": "A modern async Python stack with AI orchestration via LangGraph.",
}
