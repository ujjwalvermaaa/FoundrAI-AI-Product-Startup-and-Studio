"""
Application-wide constants. Never put secrets here.
"""

from typing import Final

# ── Module Keys ───────────────────────────────────────────────────────────────
MODULE_KEYS: Final[list[str]] = [
    "idea_validation",
    "market_research",
    "business_model",
    "product_strategy",
    "technical_architecture",
    "financial_planning",
    "marketing_strategy",
    "investor_documentation",
]

MODULE_DISPLAY_NAMES: Final[dict[str, str]] = {
    "idea_validation": "Idea Validation",
    "market_research": "Market Research",
    "business_model": "Business Model",
    "product_strategy": "Product Strategy",
    "technical_architecture": "Technical Architecture",
    "financial_planning": "Financial Planning",
    "marketing_strategy": "Marketing Strategy",
    "investor_documentation": "Investor Documentation",
}

# ── Artifact Types ────────────────────────────────────────────────────────────
ARTIFACT_TYPES: Final[dict[str, str]] = {
    "idea_validation": "validation_report",
    "market_research": "market_analysis",
    "business_model": "business_model_canvas",
    "product_strategy": "product_roadmap",
    "technical_architecture": "architecture_doc",
    "financial_planning": "financial_model",
    "marketing_strategy": "marketing_plan",
    "investor_documentation": "investor_deck_outline",
}

# ── Module Dependencies ───────────────────────────────────────────────────────
# Maps module_key → list of required artifact_types before it can run
MODULE_DEPENDENCIES: Final[dict[str, list[str]]] = {
    "idea_validation": [],
    "market_research": ["validation_report"],
    "business_model": ["validation_report", "market_analysis"],
    "product_strategy": ["business_model_canvas"],
    "technical_architecture": ["product_roadmap"],
    "financial_planning": ["business_model_canvas", "product_roadmap"],
    "marketing_strategy": ["business_model_canvas", "product_roadmap"],
    "investor_documentation": [
        "validation_report",
        "market_analysis",
        "business_model_canvas",
        "product_roadmap",
        "financial_model",
    ],
}

# ── Module Sort Order ─────────────────────────────────────────────────────────
MODULE_SORT_ORDER: Final[dict[str, int]] = {
    "idea_validation": 1,
    "market_research": 2,
    "business_model": 3,
    "product_strategy": 4,
    "technical_architecture": 5,
    "financial_planning": 6,
    "marketing_strategy": 7,
    "investor_documentation": 8,
}

# ── Module Status Values ──────────────────────────────────────────────────────
MODULE_STATUS_LOCKED: Final[str] = "locked"
MODULE_STATUS_AVAILABLE: Final[str] = "available"
MODULE_STATUS_IN_PROGRESS: Final[str] = "in_progress"
MODULE_STATUS_COMPLETED: Final[str] = "completed"
MODULE_STATUS_FAILED: Final[str] = "failed"

# ── Workflow Status Values ────────────────────────────────────────────────────
WORKFLOW_STATUS_PENDING: Final[str] = "pending"
WORKFLOW_STATUS_RUNNING: Final[str] = "running"
WORKFLOW_STATUS_COMPLETED: Final[str] = "completed"
WORKFLOW_STATUS_FAILED: Final[str] = "failed"
WORKFLOW_STATUS_CANCELLED: Final[str] = "cancelled"

# ── Project Stage Values ──────────────────────────────────────────────────────
PROJECT_STAGE_DRAFT: Final[str] = "draft"
PROJECT_STAGE_ACTIVE: Final[str] = "active"
PROJECT_STAGE_ARCHIVED: Final[str] = "archived"

# ── Export ────────────────────────────────────────────────────────────────────
EXPORT_MIN_REQUIRED_ARTIFACTS: Final[list[str]] = [
    "validation_report",
    "business_model_canvas",
    "financial_model",
]

# ── Pagination ────────────────────────────────────────────────────────────────
DEFAULT_PAGE_SIZE: Final[int] = 20
MAX_PAGE_SIZE: Final[int] = 100

# ── AI ────────────────────────────────────────────────────────────────────────
MAX_REPAIR_RETRIES: Final[int] = 2
DEFAULT_RAG_TOP_K: Final[int] = 8
