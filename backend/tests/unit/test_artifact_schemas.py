"""
Unit tests for ai.schemas — artifact Pydantic schema validation.

Tests verify:
- Valid fixtures pass validation
- Missing required fields raise ValidationError
- Minimum-count validators work correctly
- get_schema_for_module() returns correct classes
"""

from __future__ import annotations

import copy

import pytest
from pydantic import ValidationError

from ai.schemas import get_schema_for_module
from ai.schemas.architecture_doc import ArchitectureDoc
from ai.schemas.architecture_doc import VALID_FIXTURE as ARCH_FIXTURE
from ai.schemas.business_model_canvas import BusinessModelCanvas
from ai.schemas.business_model_canvas import VALID_FIXTURE as BMC_FIXTURE
from ai.schemas.financial_model import FinancialModel
from ai.schemas.financial_model import VALID_FIXTURE as FINANCIAL_FIXTURE
from ai.schemas.investor_deck_outline import InvestorDeckOutline
from ai.schemas.investor_deck_outline import VALID_FIXTURE as INVESTOR_FIXTURE
from ai.schemas.market_analysis import MarketAnalysis
from ai.schemas.market_analysis import VALID_FIXTURE as MARKET_FIXTURE
from ai.schemas.marketing_plan import MarketingPlan
from ai.schemas.marketing_plan import VALID_FIXTURE as MARKETING_FIXTURE
from ai.schemas.product_roadmap import ProductRoadmap
from ai.schemas.product_roadmap import VALID_FIXTURE as ROADMAP_FIXTURE
from ai.schemas.validation_report import ValidationReport
from ai.schemas.validation_report import VALID_FIXTURE as VALIDATION_FIXTURE


# ─────────────────────────────────────────────────────────────────────────────
# ValidationReport
# ─────────────────────────────────────────────────────────────────────────────


def test_validation_report_valid_fixture():
    report = ValidationReport(**copy.deepcopy(VALIDATION_FIXTURE))
    assert report.problem
    assert report.validation_score == 72
    assert len(report.risks) == 3


def test_validation_report_invalid_fixture():
    """Missing required fields should raise ValidationError."""
    with pytest.raises(ValidationError):
        ValidationReport(problem="Only problem, missing solution and more")


def test_validation_report_risks_min_three():
    """Fewer than 3 risks raises ValidationError."""
    data = copy.deepcopy(VALIDATION_FIXTURE)
    data["risks"] = data["risks"][:2]  # only 2
    with pytest.raises(ValidationError, match="risks must have at least 3"):
        ValidationReport(**data)


def test_validation_report_score_range_too_high():
    """Score of 101 raises ValidationError."""
    data = copy.deepcopy(VALIDATION_FIXTURE)
    data["validation_score"] = 101
    with pytest.raises(ValidationError, match="validation_score must be 0-100"):
        ValidationReport(**data)


def test_validation_report_score_range_negative():
    """Score of -1 raises ValidationError."""
    data = copy.deepcopy(VALIDATION_FIXTURE)
    data["validation_score"] = -1
    with pytest.raises(ValidationError, match="validation_score must be 0-100"):
        ValidationReport(**data)


# ─────────────────────────────────────────────────────────────────────────────
# MarketAnalysis
# ─────────────────────────────────────────────────────────────────────────────


def test_market_analysis_valid_fixture():
    analysis = MarketAnalysis(**copy.deepcopy(MARKET_FIXTURE))
    assert analysis.summary
    assert len(analysis.competitors) == 3


def test_market_analysis_invalid_fixture():
    """Missing required 'summary' field raises ValidationError."""
    with pytest.raises(ValidationError):
        MarketAnalysis(
            tam={"value": "50B"},
            sam={"value": "5B"},
            som={"value": "500M"},
            competitors=[
                {"name": "A"},
                {"name": "B"},
                {"name": "C"},
            ],
            # summary missing
        )


def test_market_analysis_competitors_min_three():
    """Fewer than 3 competitors raises ValidationError."""
    data = copy.deepcopy(MARKET_FIXTURE)
    data["competitors"] = data["competitors"][:2]
    with pytest.raises(ValidationError, match="competitors must have at least 3"):
        MarketAnalysis(**data)


# ─────────────────────────────────────────────────────────────────────────────
# BusinessModelCanvas
# ─────────────────────────────────────────────────────────────────────────────


def test_business_model_canvas_valid_fixture():
    canvas = BusinessModelCanvas(**copy.deepcopy(BMC_FIXTURE))
    assert canvas.value_proposition


def test_business_model_canvas_invalid_fixture():
    """Missing required canvas field raises ValidationError."""
    with pytest.raises(ValidationError):
        # Missing value_proposition
        BusinessModelCanvas(
            customer_segments="Founders",
            channels="Web",
            customer_relationships="Self-serve",
            revenue_streams="SaaS",
            key_resources="AI",
            key_activities="Dev",
            key_partnerships="Cloud",
            cost_structure="Compute",
        )


def test_business_model_canvas_empty_field():
    """An empty string for a canvas field raises ValidationError."""
    data = copy.deepcopy(BMC_FIXTURE)
    data["value_proposition"] = ""
    with pytest.raises(ValidationError, match="must not be empty"):
        BusinessModelCanvas(**data)


# ─────────────────────────────────────────────────────────────────────────────
# ProductRoadmap
# ─────────────────────────────────────────────────────────────────────────────


def test_product_roadmap_valid_fixture():
    roadmap = ProductRoadmap(**copy.deepcopy(ROADMAP_FIXTURE))
    assert len(roadmap.phases) == 2


def test_product_roadmap_invalid_fixture():
    """phases is required; omitting it raises ValidationError."""
    with pytest.raises(ValidationError):
        ProductRoadmap()


def test_product_roadmap_phases_min_two():
    """Fewer than 2 phases raises ValidationError."""
    data = copy.deepcopy(ROADMAP_FIXTURE)
    data["phases"] = data["phases"][:1]
    with pytest.raises(ValidationError, match="phases must have at least 2"):
        ProductRoadmap(**data)


# ─────────────────────────────────────────────────────────────────────────────
# ArchitectureDoc
# ─────────────────────────────────────────────────────────────────────────────


def test_architecture_doc_valid_fixture():
    doc = ArchitectureDoc(**copy.deepcopy(ARCH_FIXTURE))
    assert doc.components


def test_architecture_doc_invalid_fixture():
    """Missing required 'components' and 'security_considerations' raises ValidationError."""
    with pytest.raises(ValidationError):
        ArchitectureDoc(stack_recommendations=["Python"])


# ─────────────────────────────────────────────────────────────────────────────
# FinancialModel
# ─────────────────────────────────────────────────────────────────────────────


def test_financial_model_valid_fixture():
    model = FinancialModel(**copy.deepcopy(FINANCIAL_FIXTURE))
    assert len(model.projection_12_months) == 12
    assert len(model.assumptions) >= 5


def test_financial_model_invalid_fixture():
    """Missing required fields raises ValidationError."""
    with pytest.raises(ValidationError):
        FinancialModel(assumptions=["a", "b", "c", "d", "e"])


def test_financial_model_assumptions_min_five():
    """Fewer than 5 assumptions raises ValidationError."""
    data = copy.deepcopy(FINANCIAL_FIXTURE)
    data["assumptions"] = data["assumptions"][:4]
    with pytest.raises(ValidationError, match="assumptions must have at least 5"):
        FinancialModel(**data)


# ─────────────────────────────────────────────────────────────────────────────
# MarketingPlan
# ─────────────────────────────────────────────────────────────────────────────


def test_marketing_plan_valid_fixture():
    plan = MarketingPlan(**copy.deepcopy(MARKETING_FIXTURE))
    assert len(plan.channels) >= 3
    assert len(plan.launch_checklist) >= 5


def test_marketing_plan_invalid_fixture():
    """Missing required 'icp' and 'messaging' raises ValidationError."""
    with pytest.raises(ValidationError):
        MarketingPlan(
            channels=["A", "B", "C"],
            launch_checklist=["1", "2", "3", "4", "5"],
        )


def test_marketing_plan_channels_min_three():
    """Fewer than 3 channels raises ValidationError."""
    data = copy.deepcopy(MARKETING_FIXTURE)
    data["channels"] = data["channels"][:2]
    with pytest.raises(ValidationError, match="channels must have at least 3"):
        MarketingPlan(**data)


def test_marketing_plan_checklist_min_five():
    """Fewer than 5 launch checklist items raises ValidationError."""
    data = copy.deepcopy(MARKETING_FIXTURE)
    data["launch_checklist"] = data["launch_checklist"][:4]
    with pytest.raises(ValidationError, match="launch_checklist must have at least 5"):
        MarketingPlan(**data)


# ─────────────────────────────────────────────────────────────────────────────
# InvestorDeckOutline
# ─────────────────────────────────────────────────────────────────────────────


def test_investor_deck_outline_valid_fixture():
    deck = InvestorDeckOutline(**copy.deepcopy(INVESTOR_FIXTURE))
    assert len(deck.slides) == 11


def test_investor_deck_outline_invalid_fixture():
    """Missing required 'slides' field raises ValidationError."""
    with pytest.raises(ValidationError):
        InvestorDeckOutline()


def test_investor_deck_slides_min_ten():
    """Fewer than 10 slides raises ValidationError."""
    data = copy.deepcopy(INVESTOR_FIXTURE)
    data["slides"] = data["slides"][:9]
    with pytest.raises(ValidationError, match="slides must have at least 10"):
        InvestorDeckOutline(**data)


# ─────────────────────────────────────────────────────────────────────────────
# get_schema_for_module
# ─────────────────────────────────────────────────────────────────────────────


def test_get_schema_for_module_returns_correct_class():
    """All 8 module keys return the correct Pydantic schema class."""
    expected = {
        "idea_validation": ValidationReport,
        "market_research": MarketAnalysis,
        "business_model": BusinessModelCanvas,
        "product_strategy": ProductRoadmap,
        "technical_architecture": ArchitectureDoc,
        "financial_planning": FinancialModel,
        "marketing_strategy": MarketingPlan,
        "investor_documentation": InvestorDeckOutline,
    }
    for module_key, schema_class in expected.items():
        result = get_schema_for_module(module_key)
        assert result is schema_class, f"Expected {schema_class} for '{module_key}', got {result}"


def test_get_schema_for_module_returns_none_for_unknown():
    """Unknown module key returns None."""
    assert get_schema_for_module("unknown_module") is None
    assert get_schema_for_module("") is None
    assert get_schema_for_module("nonexistent") is None
