"""
Ollama HTTP client.

Provides async methods:
  - chat()        — multi-turn conversation
  - generate()    — single-turn completion
  - list_models() — list available models
  - is_available() — health check

Uses httpx for async HTTP. No LangChain dependency here — this is the
raw transport layer. LangChain integration wraps this in model_factory.py.
"""

from __future__ import annotations

import json
import logging
from typing import Any, AsyncGenerator

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class OllamaError(Exception):
    """Raised when Ollama returns an error or is unreachable."""


class OllamaClient:
    """
    Async HTTP client for the Ollama local API.

    Usage:
        client = OllamaClient()
        response = await client.chat(
            model="qwen3:8b",
            messages=[{"role": "user", "content": "Hello"}],
        )
    """

    def __init__(
        self,
        base_url: str | None = None,
        timeout: float = 300.0,
    ) -> None:
        self._base_url = (base_url or settings.ollama_base_url).rstrip("/")
        self._timeout = timeout

    # ── Health ────────────────────────────────────────────────────────────

    async def is_available(self) -> bool:
        """Return True if Ollama is reachable, False otherwise."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{self._base_url}/api/tags")
                return resp.status_code == 200
        except Exception:
            return False

    async def list_models(self) -> list[str]:
        """
        Return a list of model names available in this Ollama instance.

        Example: ["qwen3:8b", "llama3:8b"]
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(f"{self._base_url}/api/tags")
                resp.raise_for_status()
                data = resp.json()
                return [m["name"] for m in data.get("models", [])]
        except httpx.HTTPError as e:
            raise OllamaError(f"Failed to list models: {e}") from e

    # ── Chat ──────────────────────────────────────────────────────────────

    async def chat(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
        temperature: float | None = None,
        top_p: float | None = None,
        top_k: int | None = None,
        max_tokens: int | None = None,
        stream: bool = False,
    ) -> str:
        """
        Send a multi-turn chat request to Ollama.

        Args:
            messages: List of {"role": "user"|"assistant"|"system", "content": "..."}
            model: Model name. Defaults to settings.ollama_model.
            stream: If True, stream tokens (yields str chunks).

        Returns:
            The assistant's reply as a plain string.

        Raises:
            OllamaError: On HTTP error or non-200 response.
        """
        payload: dict[str, Any] = {
            "model": model or settings.ollama_model,
            "messages": messages,
            "stream": stream,
            "think": False,  # disable qwen3 extended thinking mode
            "options": self._build_options(temperature, top_p, top_k, max_tokens),
        }

        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                resp = await client.post(
                    f"{self._base_url}/api/chat",
                    json=payload,
                )
                self._raise_for_status(resp)
                data = resp.json()
                return data["message"]["content"]
        except OllamaError:
            raise
        except httpx.TimeoutException as e:
            raise OllamaError(f"Ollama request timed out after {self._timeout}s") from e
        except httpx.HTTPError as e:
            raise OllamaError(f"Ollama HTTP error: {e}") from e

    async def chat_stream(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
        temperature: float | None = None,
        top_p: float | None = None,
        top_k: int | None = None,
        max_tokens: int | None = None,
    ) -> AsyncGenerator[str, None]:
        """
        Stream chat tokens from Ollama.

        Yields:
            Token strings as they are generated.
        """
        payload: dict[str, Any] = {
            "model": model or settings.ollama_model,
            "messages": messages,
            "stream": True,
            "think": False,  # disable qwen3 extended thinking mode
            "options": self._build_options(temperature, top_p, top_k, max_tokens),
        }

        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                async with client.stream(
                    "POST",
                    f"{self._base_url}/api/chat",
                    json=payload,
                ) as resp:
                    self._raise_for_status(resp)
                    async for line in resp.aiter_lines():
                        if not line.strip():
                            continue
                        try:
                            chunk = json.loads(line)
                            token = chunk.get("message", {}).get("content", "")
                            if token:
                                yield token
                            if chunk.get("done"):
                                break
                        except json.JSONDecodeError:
                            continue
        except OllamaError:
            raise
        except httpx.HTTPError as e:
            raise OllamaError(f"Ollama stream error: {e}") from e

    # ── Generate ──────────────────────────────────────────────────────────

    async def generate(
        self,
        prompt: str,
        model: str | None = None,
        system: str | None = None,
        temperature: float | None = None,
        top_p: float | None = None,
        top_k: int | None = None,
        max_tokens: int | None = None,
    ) -> str:
        """
        Single-turn text generation (no conversation history).

        Args:
            prompt: The input prompt.
            system: Optional system prompt.

        Returns:
            Generated text as a string.
        """
        payload: dict[str, Any] = {
            "model": model or settings.ollama_model,
            "prompt": prompt,
            "stream": False,
            "think": False,  # disable qwen3 extended thinking mode
            "options": self._build_options(temperature, top_p, top_k, max_tokens),
        }
        if system:
            payload["system"] = system

        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                resp = await client.post(
                    f"{self._base_url}/api/generate",
                    json=payload,
                )
                self._raise_for_status(resp)
                return resp.json()["response"]
        except OllamaError:
            raise
        except httpx.TimeoutException as e:
            raise OllamaError(f"Ollama generate timed out after {self._timeout}s") from e
        except httpx.HTTPError as e:
            raise OllamaError(f"Ollama HTTP error: {e}") from e

    # ── Helpers ───────────────────────────────────────────────────────────

    def _build_options(
        self,
        temperature: float | None,
        top_p: float | None,
        top_k: int | None,
        max_tokens: int | None,
    ) -> dict[str, Any]:
        opts: dict[str, Any] = {}
        if temperature is not None:
            opts["temperature"] = temperature
        else:
            opts["temperature"] = settings.llm_temperature
        if top_p is not None:
            opts["top_p"] = top_p
        else:
            opts["top_p"] = settings.llm_top_p
        if top_k is not None:
            opts["top_k"] = top_k
        else:
            opts["top_k"] = settings.llm_top_k
        if max_tokens is not None:
            opts["num_predict"] = max_tokens
        else:
            opts["num_predict"] = settings.llm_max_tokens
        return opts

    @staticmethod
    def _raise_for_status(resp: httpx.Response) -> None:
        if resp.status_code != 200:
            try:
                detail = resp.json().get("error", resp.text)
            except Exception:
                detail = resp.text
            raise OllamaError(f"Ollama returned {resp.status_code}: {detail}")


# ── Module-level singleton ─────────────────────────────────────────────────────
# Import and use this everywhere instead of constructing a new client each time.
ollama_client = OllamaClient()
