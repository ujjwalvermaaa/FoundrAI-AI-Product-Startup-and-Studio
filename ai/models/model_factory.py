"""
ModelFactory — resolves agent-specific model configuration from YAML.

Usage:
    config = ModelFactory.get_agent_config("idea_validator")
    # → AgentModelConfig(model="qwen3:8b", temperature=0.3, max_tokens=2048)

    client = ModelFactory.get_client()
    response = await client.chat(messages, **config.generation_kwargs())
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from ai.models.ollama import OllamaClient

_CONFIG_DIR = Path(__file__).parent.parent / "config"


@dataclass
class AgentModelConfig:
    """Resolved model configuration for a single agent."""

    model: str
    temperature: float = 0.3
    top_p: float = 0.9
    top_k: int = 40
    max_tokens: int = 1024
    description: str = ""

    def generation_kwargs(self) -> dict[str, Any]:
        """Return kwargs suitable for OllamaClient.chat() / .generate()."""
        return {
            "model": self.model,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "top_k": self.top_k,
            "max_tokens": self.max_tokens,
        }


class ModelFactory:
    """
    Reads models.yaml and agents.yaml to resolve per-agent model configs.

    Both files are loaded once and cached for the process lifetime.
    """

    _models_cfg: dict[str, Any] | None = None
    _agents_cfg: dict[str, Any] | None = None

    # ── Config loading ────────────────────────────────────────────────────

    @classmethod
    def _load_models(cls) -> dict[str, Any]:
        if cls._models_cfg is None:
            path = _CONFIG_DIR / "models.yaml"
            with open(path) as f:
                cls._models_cfg = yaml.safe_load(f)
        return cls._models_cfg  # type: ignore[return-value]

    @classmethod
    def _load_agents(cls) -> dict[str, Any]:
        if cls._agents_cfg is None:
            path = _CONFIG_DIR / "agents.yaml"
            with open(path) as f:
                cls._agents_cfg = yaml.safe_load(f)
        return cls._agents_cfg  # type: ignore[return-value]

    # ── Public API ────────────────────────────────────────────────────────

    @classmethod
    def get_agent_config(cls, agent_id: str) -> AgentModelConfig:
        """
        Return resolved AgentModelConfig for the given agent ID.

        Falls back to defaults from models.yaml if the agent is not listed
        in agents.yaml.

        Args:
            agent_id: e.g. "idea_validator", "market_researcher"

        Returns:
            AgentModelConfig with model name and generation parameters.
        """
        models_cfg = cls._load_models()
        agents_cfg = cls._load_agents()

        defaults = models_cfg.get("defaults", {})
        default_model_key = models_cfg.get("default_model", "qwen3_8b")
        models = models_cfg.get("models", {})

        # Resolve default model name
        default_model_name = models.get(default_model_key, {}).get(
            "name", "qwen3:8b"
        )

        # Agent-specific overrides
        agent_override = agents_cfg.get("agents", {}).get(agent_id, {})

        # Resolve model name from agent config → models.yaml → hardcoded fallback
        agent_model_key = agent_override.get("model", default_model_key)
        model_name = models.get(agent_model_key, {}).get("name", default_model_name)

        return AgentModelConfig(
            model=model_name,
            temperature=agent_override.get(
                "temperature", defaults.get("temperature", 0.3)
            ),
            top_p=defaults.get("top_p", 0.9),
            top_k=defaults.get("top_k", 40),
            max_tokens=agent_override.get(
                "max_tokens", defaults.get("max_tokens", 4096)
            ),
            description=agent_override.get("description", ""),
        )

    @classmethod
    def get_default_config(cls) -> AgentModelConfig:
        """Return the default model config (no agent-specific overrides)."""
        return cls.get_agent_config("__default__")

    @classmethod
    def get_client(cls, timeout: float = 300.0) -> OllamaClient:
        """Return a new OllamaClient with the configured base URL."""
        from app.core.config import settings
        return OllamaClient(base_url=settings.ollama_base_url, timeout=timeout)

    @classmethod
    def reset_cache(cls) -> None:
        """Force re-read of YAML files on next access. Useful in tests."""
        cls._models_cfg = None
        cls._agents_cfg = None
