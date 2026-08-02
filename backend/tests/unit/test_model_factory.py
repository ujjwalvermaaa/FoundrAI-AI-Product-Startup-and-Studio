"""
Unit tests for ModelFactory and agent model resolution.
No Ollama connection required — tests config loading and resolution logic.
"""

import pytest


def test_default_config_loads():
    """ModelFactory returns a valid default config."""
    from ai.models.model_factory import ModelFactory
    ModelFactory.reset_cache()
    cfg = ModelFactory.get_default_config()
    assert cfg.model  # non-empty string
    assert 0.0 <= cfg.temperature <= 2.0
    assert cfg.max_tokens > 0


def test_known_agent_config():
    """Known agent IDs resolve to correct settings from agents.yaml."""
    from ai.models.model_factory import ModelFactory
    ModelFactory.reset_cache()
    cfg = ModelFactory.get_agent_config("idea_validator")
    assert cfg.model == "qwen3:4b"
    assert cfg.temperature == 0.3
    assert cfg.max_tokens == 2048


def test_unknown_agent_falls_back_to_default():
    """Unknown agent IDs fall back gracefully to defaults."""
    from ai.models.model_factory import ModelFactory
    ModelFactory.reset_cache()
    cfg = ModelFactory.get_agent_config("nonexistent_agent")
    assert cfg.model == "qwen3:4b"
    assert cfg.max_tokens == 4096


def test_all_8_agents_resolve():
    """All 8 defined agents resolve without error."""
    from ai.models.model_factory import ModelFactory
    ModelFactory.reset_cache()
    agents = [
        "idea_validator", "market_researcher", "business_modeler",
        "product_strategist", "technical_architect", "financial_analyst",
        "marketing_strategist", "investor_writer",
    ]
    for agent_id in agents:
        cfg = ModelFactory.get_agent_config(agent_id)
        assert cfg.model == "qwen3:4b", f"{agent_id} has wrong model: {cfg.model}"
        assert cfg.temperature >= 0.0
        assert cfg.max_tokens > 0


def test_generation_kwargs_shape():
    """generation_kwargs() returns all required keys for OllamaClient."""
    from ai.models.model_factory import ModelFactory
    ModelFactory.reset_cache()
    cfg = ModelFactory.get_agent_config("idea_validator")
    kwargs = cfg.generation_kwargs()
    assert "model" in kwargs
    assert "temperature" in kwargs
    assert "top_p" in kwargs
    assert "top_k" in kwargs
    assert "max_tokens" in kwargs


def test_get_client_returns_ollama_client():
    """get_client() returns an OllamaClient instance."""
    from ai.models.model_factory import ModelFactory
    from ai.models.ollama import OllamaClient
    client = ModelFactory.get_client()
    assert isinstance(client, OllamaClient)


# ── Ollama connection tests (skipped if Ollama not running) ───────────────────

import asyncio


@pytest.mark.asyncio
async def test_ollama_is_available():
    """Skip if Ollama is not running locally."""
    from ai.models.ollama import OllamaClient
    client = OllamaClient()
    available = await client.is_available()
    if not available:
        pytest.skip("Ollama is not running — skipping connection test")
    assert available is True


@pytest.mark.asyncio
async def test_ollama_list_models_when_available():
    """List models returns a list (may be empty if no models pulled yet)."""
    from ai.models.ollama import OllamaClient
    client = OllamaClient()
    if not await client.is_available():
        pytest.skip("Ollama is not running")
    models = await client.list_models()
    assert isinstance(models, list)


@pytest.mark.asyncio
async def test_qwen3_8b_available_when_running():
    """Check qwen3:4b is listed (only if Ollama running and model pulled)."""
    from ai.models.ollama import OllamaClient
    from app.core.config import settings
    client = OllamaClient()
    if not await client.is_available():
        pytest.skip("Ollama is not running")
    models = await client.list_models()
    if settings.ollama_model not in models:
        pytest.skip(f"{settings.ollama_model} not yet pulled — run: ollama pull {settings.ollama_model}")
    assert settings.ollama_model in models
