"""
Application configuration via pydantic-settings.
All settings are loaded from environment variables or .env file.
Never hardcode secrets here.
"""

from functools import lru_cache
from typing import List

from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ──────────────────────────────────────────────────────────
    app_name: str = "FoundrAI"
    app_env: str = "development"
    debug: bool = False
    log_level: str = "INFO"

    # ── Backend ───────────────────────────────────────────────────────────────
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000

    # ── Frontend ──────────────────────────────────────────────────────────────
    frontend_url: str = "http://localhost:3000"
    next_public_api_url: str = "http://localhost:8000/api/v1"

    # ── Database ──────────────────────────────────────────────────────────────
    database_url: str = "postgresql+asyncpg://foundrai:foundrai_dev@localhost:5432/foundrai"

    # ── JWT ───────────────────────────────────────────────────────────────────
    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 15
    jwt_refresh_token_expire_days: int = 7

    # ── Ollama ────────────────────────────────────────────────────────────────
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen3:4b"

    # ── Embeddings ────────────────────────────────────────────────────────────
    embedding_model: str = "BAAI/bge-base-en-v1.5"

    # ── FAISS ─────────────────────────────────────────────────────────────────
    faiss_index_path: str = "./data/faiss"

    # ── RAG ───────────────────────────────────────────────────────────────────
    rag_top_k: int = 8
    rag_chunk_size: int = 800
    rag_chunk_overlap: int = 150

    # ── LLM Defaults ─────────────────────────────────────────────────────────
    llm_temperature: float = 0.3
    llm_top_p: float = 0.9
    llm_top_k: int = 40
    llm_max_tokens: int = 4096

    # ── AI Feature Flags ─────────────────────────────────────────────────────
    enable_rag: bool = True
    enable_memory: bool = True
    enable_reflection: bool = True
    enable_repair: bool = True
    enable_streaming: bool = False

    # ── Storage ───────────────────────────────────────────────────────────────
    upload_dir: str = "./data/uploads"
    export_dir: str = "./data/exports"
    knowledge_dir: str = "./data/knowledge"
    log_dir: str = "./logs"

    # ── CORS ──────────────────────────────────────────────────────────────────
    allowed_origins: str = "http://localhost:3000"

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_allowed_origins(cls, v: str) -> str:
        return v

    def get_allowed_origins_list(self) -> List[str]:
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]

    # ── Rate Limiting ─────────────────────────────────────────────────────────
    rate_limit_enabled: bool = False

    # ── Feature Flags ─────────────────────────────────────────────────────────
    enable_marketing_module: bool = True
    enable_financial_module: bool = True
    enable_investor_module: bool = True
    enable_export: bool = True

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @property
    def is_development(self) -> bool:
        return self.app_env == "development"


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance. Use this everywhere."""
    return Settings()


# Module-level singleton for convenience
settings = get_settings()
