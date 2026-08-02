"""
Custom application exceptions.
All domain errors map to structured HTTP error responses via handlers in main.py.
"""

from typing import Any, Optional


class FoundrAIException(Exception):
    """Base exception for all FoundrAI application errors."""

    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_ERROR",
        status_code: int = 500,
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}


# ── Auth Exceptions ──────────────────────────────────────────────────────────

class EmailAlreadyExistsError(FoundrAIException):
    def __init__(self, email: str) -> None:
        super().__init__(
            message=f"An account with email '{email}' already exists.",
            code="EMAIL_ALREADY_EXISTS",
            status_code=409,
        )


class InvalidCredentialsError(FoundrAIException):
    def __init__(self) -> None:
        super().__init__(
            message="Invalid email or password.",
            code="INVALID_CREDENTIALS",
            status_code=401,
        )


class InvalidRefreshTokenError(FoundrAIException):
    def __init__(self) -> None:
        super().__init__(
            message="Refresh token is invalid or expired.",
            code="INVALID_REFRESH_TOKEN",
            status_code=401,
        )


class UnauthorizedError(FoundrAIException):
    def __init__(self, message: str = "Authentication required.") -> None:
        super().__init__(message=message, code="UNAUTHORIZED", status_code=401)


class AccountDisabledError(FoundrAIException):
    def __init__(self) -> None:
        super().__init__(
            message="This account has been disabled.",
            code="ACCOUNT_DISABLED",
            status_code=403,
        )


# ── Project Exceptions ────────────────────────────────────────────────────────

class ProjectNotFoundError(FoundrAIException):
    def __init__(self, project_id: str = "") -> None:
        super().__init__(
            message="Project not found.",
            code="PROJECT_NOT_FOUND",
            status_code=404,
            details={"project_id": project_id} if project_id else {},
        )


class ModuleNotFoundError(FoundrAIException):
    def __init__(self, module_key: str = "") -> None:
        super().__init__(
            message=f"Module '{module_key}' not found.",
            code="MODULE_NOT_FOUND",
            status_code=404,
            details={"module_key": module_key} if module_key else {},
        )


# ── Workflow Exceptions ───────────────────────────────────────────────────────

class ModuleDependencyNotMetError(FoundrAIException):
    def __init__(self, missing: list[str]) -> None:
        super().__init__(
            message="Required artifacts are missing to run this module.",
            code="MODULE_DEPENDENCY_NOT_MET",
            status_code=409,
            details={"missing_artifacts": missing},
        )


class WorkflowAlreadyRunningError(FoundrAIException):
    def __init__(self, module_key: str) -> None:
        super().__init__(
            message=f"A workflow for module '{module_key}' is already pending or running.",
            code="WORKFLOW_ALREADY_RUNNING",
            status_code=409,
            details={"module_key": module_key},
        )


class WorkflowNotCancellableError(FoundrAIException):
    def __init__(self) -> None:
        super().__init__(
            message="This workflow run cannot be cancelled in its current state.",
            code="WORKFLOW_NOT_CANCELLABLE",
            status_code=409,
        )


# ── Artifact Exceptions ───────────────────────────────────────────────────────

class ArtifactNotFoundError(FoundrAIException):
    def __init__(self, artifact_id: str = "") -> None:
        super().__init__(
            message="Artifact not found.",
            code="ARTIFACT_NOT_FOUND",
            status_code=404,
            details={"artifact_id": artifact_id} if artifact_id else {},
        )


class SchemaValidationFailedError(FoundrAIException):
    def __init__(self, detail: str = "") -> None:
        super().__init__(
            message="Artifact content failed schema validation.",
            code="SCHEMA_VALIDATION_FAILED",
            status_code=422,
            details={"detail": detail} if detail else {},
        )


# ── Export Exceptions ─────────────────────────────────────────────────────────

class InsufficientArtifactsError(FoundrAIException):
    def __init__(self, missing: list[str]) -> None:
        super().__init__(
            code="INSUFFICIENT_ARTIFACTS",
            message=f"Missing required artifacts: {', '.join(missing)}",
            status_code=409,
            details={"missing_artifacts": missing},
        )


# ── AI / Ollama Exceptions ────────────────────────────────────────────────────

class OllamaUnavailableError(FoundrAIException):
    def __init__(self) -> None:
        super().__init__(
            message="Ollama LLM service is unavailable. Please ensure Ollama is running.",
            code="OLLAMA_UNAVAILABLE",
            status_code=503,
        )


class ValidationError(FoundrAIException):
    def __init__(self, message: str, details: Optional[dict] = None) -> None:
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            status_code=422,
            details=details or {},
        )
