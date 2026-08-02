"""
PromptBuilder — assembles Ollama message lists from versioned prompt templates.

Template files live at:
  ai/prompts/agents/{agent_id}/{type}.{version}.md

Supported types:  system | developer | user | repair | reflection | validation

Usage:
    from ai.runtime.prompt_builder import PromptBuilder

    builder = PromptBuilder()
    messages, version_str = builder.build("idea_validator", state)
    # → ([{"role": "system", ...}, {"role": "user", ...}], "v1")
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ai.graphs.state import WorkflowState

logger = logging.getLogger(__name__)

# Default directory: ai/prompts/agents/
_DEFAULT_PROMPTS_DIR = Path(__file__).parent.parent / "prompts" / "agents"


class PromptBuilder:
    """
    Loads versioned prompt templates and assembles them into an Ollama
    messages list for a given agent and workflow state.
    """

    def __init__(self, prompts_dir: Path | None = None) -> None:
        self._prompts_dir = prompts_dir or _DEFAULT_PROMPTS_DIR

    # ── Public API ────────────────────────────────────────────────────────

    def build(
        self,
        agent_id: str,
        state: "WorkflowState",
        prompt_version: str = "v1",
    ) -> tuple[list[dict[str, str]], str]:
        """
        Build the Ollama messages list for a standard generation invoke.

        Returns:
            (messages, prompt_version_string)
            messages = [
                {"role": "system", "content": "..."},
                {"role": "user", "content": "..."},
            ]
        """
        # ── System message ────────────────────────────────────────────────
        system_tmpl = self._load_template(agent_id, "system", prompt_version)
        dev_tmpl = self._load_template(agent_id, "developer", prompt_version)

        system_parts = []
        if system_tmpl:
            system_parts.append(self._fill_placeholders(system_tmpl, state))
        if dev_tmpl:
            system_parts.append(self._fill_placeholders(dev_tmpl, state))
        system_content = "\n\n".join(system_parts) if system_parts else (
            f"You are {agent_id}, an AI assistant for startup analysis."
        )

        # ── User message ──────────────────────────────────────────────────
        context_block = self._build_context_block(state)
        user_tmpl = self._load_template(agent_id, "user", prompt_version)
        user_tmpl_filled = self._fill_placeholders(user_tmpl, state) if user_tmpl else ""

        user_content_parts = [context_block]
        if user_tmpl_filled:
            user_content_parts.append(user_tmpl_filled)
        user_content = "\n\n".join(p for p in user_content_parts if p)

        messages: list[dict[str, str]] = [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_content},
        ]

        logger.debug(
            "PromptBuilder.build: agent=%s version=%s system=%d chars user=%d chars",
            agent_id,
            prompt_version,
            len(system_content),
            len(user_content),
        )

        return messages, prompt_version

    def build_repair(
        self,
        agent_id: str,
        state: "WorkflowState",
        original_output: str,
        errors: list[str],
        prompt_version: str = "v1",
    ) -> list[dict[str, str]]:
        """
        Build repair messages that include the original (broken) output and
        the validation errors so the LLM can produce a corrected version.

        Returns:
            messages list (system + user + assistant + repair)
        """
        repair_tmpl = self._load_template(agent_id, "repair", prompt_version)

        # Start from the standard messages
        base_messages, _ = self.build(agent_id, state, prompt_version)

        # Append the original (broken) assistant turn
        base_messages.append({"role": "assistant", "content": original_output})

        # Build the repair instruction
        error_block = "\n".join(f"- {e}" for e in errors)
        if repair_tmpl:
            repair_instruction = self._fill_placeholders(repair_tmpl, state)
            repair_content = (
                f"{repair_instruction}\n\n"
                f"## Errors to fix\n{error_block}"
            )
        else:
            repair_content = (
                "The JSON output above has the following errors. "
                "Please produce corrected, valid JSON:\n\n"
                f"## Errors\n{error_block}"
            )

        base_messages.append({"role": "user", "content": repair_content})

        logger.debug(
            "PromptBuilder.build_repair: agent=%s errors=%d",
            agent_id,
            len(errors),
        )

        return base_messages

    # ── Template loading ──────────────────────────────────────────────────

    def _load_template(
        self,
        agent_id: str,
        template_type: str,
        version: str,
    ) -> str:
        """
        Load a prompt template file.

        Path pattern: {prompts_dir}/{agent_id}/{template_type}.{version}.md

        Returns:
            File contents as a string, or empty string if the file does not
            exist (graceful degradation — a warning is logged).
        """
        path = self._prompts_dir / agent_id / f"{template_type}.{version}.md"
        if not path.exists():
            logger.debug(
                "PromptBuilder: template not found (graceful): %s",
                path,
            )
            return ""
        try:
            content = path.read_text(encoding="utf-8")
            logger.debug("PromptBuilder: loaded template %s (%d chars)", path, len(content))
            return content
        except OSError as exc:
            logger.warning("PromptBuilder: could not read template %s: %s", path, exc)
            return ""

    # ── Placeholder substitution ──────────────────────────────────────────

    def _fill_placeholders(self, template: str, state: "WorkflowState") -> str:
        """
        Replace well-known placeholders with values from state.

        Supported placeholders:
          {project_name}, {idea_brief}, {industry}, {module_key},
          {agent_id}, {retrieved_context}, {prior_artifacts}
        """
        if not template:
            return template

        inputs: dict = state.get("inputs") or {}
        chunks: list = state.get("retrieved_chunks") or []
        artifacts: dict = state.get("required_artifacts") or {}

        replacements = {
            "{project_name}": inputs.get("project_name", ""),
            "{idea_brief}": inputs.get("idea_brief", ""),
            "{industry}": inputs.get("industry", ""),
            "{module_key}": state.get("module_key", ""),
            "{agent_id}": state.get("agent_id", ""),
            "{run_id}": state.get("run_id", ""),
            "{retrieved_context}": self._format_retrieved_chunks(chunks),
            "{prior_artifacts}": self._format_prior_artifacts(artifacts),
        }

        result = template
        for placeholder, value in replacements.items():
            result = result.replace(placeholder, value)
        return result

    # ── Context block ─────────────────────────────────────────────────────

    def _build_context_block(self, state: "WorkflowState") -> str:
        """
        Build the structured context block that prefixes the user message.

        Format (from design doc §3.5):
            ## Project Context
            - Name: {project_name}
            - Industry: {industry}

            ## Idea Brief
            {idea_brief}

            ## Retrieved Memory
            [1] (source_type/module_key) chunk_text
            ...

            ## Prior Artifacts Summary
            {json summaries}
        """
        inputs: dict = state.get("inputs") or {}
        chunks: list = state.get("retrieved_chunks") or []
        artifacts: dict = state.get("required_artifacts") or {}

        project_name = inputs.get("project_name", "")
        industry = inputs.get("industry", "")
        idea_brief = inputs.get("idea_brief", "")

        lines: list[str] = []

        # Project context header
        lines.append("## Project Context")
        lines.append(f"- Name: {project_name}")
        lines.append(f"- Industry: {industry}")
        lines.append("")

        # Idea brief
        lines.append("## Idea Brief")
        lines.append(idea_brief)
        lines.append("")

        # Retrieved memory
        lines.append("## Retrieved Memory")
        lines.append(self._format_retrieved_chunks(chunks))
        lines.append("")

        # Prior artifacts summary
        lines.append("## Prior Artifacts Summary")
        lines.append(self._format_prior_artifacts(artifacts))

        return "\n".join(lines)

    # ── Formatting helpers ────────────────────────────────────────────────

    def _format_retrieved_chunks(self, chunks: list[dict]) -> str:
        """Format chunks as a numbered context block."""
        if not chunks:
            return "<no retrieved context>"

        lines: list[str] = []
        for i, chunk in enumerate(chunks, start=1):
            source_type = chunk.get("source_type", "")
            module_key = chunk.get("module_key") or ""
            label = f"{source_type}/{module_key}" if module_key else source_type
            content = chunk.get("content_text", "").strip()
            lines.append(f"[{i}] ({label}) {content}")

        return "\n".join(lines)

    def _format_prior_artifacts(self, artifacts: dict) -> str:
        """Format prior artifact JSON summaries."""
        if not artifacts:
            return "<no prior artifacts>"

        lines: list[str] = []
        for artifact_type, content in artifacts.items():
            if isinstance(content, (dict, list)):
                try:
                    summary = json.dumps(content, indent=2)
                    # Truncate very long summaries
                    if len(summary) > 1000:
                        summary = summary[:1000] + "\n... (truncated)"
                except (TypeError, ValueError):
                    summary = str(content)[:500]
            else:
                summary = str(content)[:500] if content else "<empty>"
            lines.append(f"### {artifact_type}\n{summary}")

        return "\n\n".join(lines)
