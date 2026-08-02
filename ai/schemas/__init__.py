"""
ai.schemas — Pydantic schema registry for FoundrAI module outputs.

Usage:
    from ai.schemas import get_schema_for_module

    schema_class = get_schema_for_module("idea_validation")
    if schema_class:
        validated = schema_class(**parsed_dict)
"""

from __future__ import annotations

from typing import Type

from pydantic import BaseModel

from ai.schemas.architecture_doc import ArchitectureDoc
from ai.schemas.business_model_canvas import BusinessModelCanvas
from ai.schemas.financial_model import FinancialModel
from ai.schemas.investor_deck_outline import InvestorDeckOutline
from ai.schemas.market_analysis import MarketAnalysis
from ai.schemas.marketing_plan import MarketingPlan
from ai.schemas.product_roadmap import ProductRoadmap
from ai.schemas.validation_report import ValidationReport

_MAP: dict[str, Type[BaseModel]] = {
    "idea_validation": ValidationReport,
    "market_research": MarketAnalysis,
    "business_model": BusinessModelCanvas,
    "product_strategy": ProductRoadmap,
    "technical_architecture": ArchitectureDoc,
    "financial_planning": FinancialModel,
    "marketing_strategy": MarketingPlan,
    "investor_documentation": InvestorDeckOutline,
}


def get_schema_for_module(module_key: str) -> Type[BaseModel] | None:
    """
    Return the Pydantic schema class for a module_key, or None if not registered.

    Args:
        module_key: e.g. "idea_validation", "market_research"

    Returns:
        A Pydantic BaseModel subclass, or None if no schema is registered.
    """
    return _MAP.get(module_key)


__all__ = [
    "get_schema_for_module",
    "ValidationReport",
    "MarketAnalysis",
    "BusinessModelCanvas",
    "ProductRoadmap",
    "ArchitectureDoc",
    "FinancialModel",
    "MarketingPlan",
    "InvestorDeckOutline",
]
