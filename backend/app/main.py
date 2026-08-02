"""
FoundrAI FastAPI application entry point.
Configures middleware, routers, exception handlers, and lifecycle events.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.exceptions import FoundrAIException
from app.core.logging import configure_logging, get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application startup and shutdown lifecycle."""
    configure_logging()
    logger.info(
        "FoundrAI starting",
        env=settings.app_env,
        version="1.0.0",
    )
    yield
    logger.info("FoundrAI shutting down")


app = FastAPI(
    title="FoundrAI API",
    description="From Idea to Startup, Powered by AI",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_allowed_origins_list(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Exception Handlers ────────────────────────────────────────────────────────

@app.exception_handler(FoundrAIException)
async def foundrai_exception_handler(
    request: Request, exc: FoundrAIException
) -> JSONResponse:
    """Convert domain exceptions to structured JSON error responses."""
    logger.warning(
        "Domain error",
        code=exc.code,
        message=exc.message,
        path=str(request.url),
        status_code=exc.status_code,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
            }
        },
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """Catch-all for unexpected errors."""
    logger.error(
        "Unhandled exception",
        path=str(request.url),
        error=str(exc),
        exc_info=True,
    )
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred.",
                "details": {},
            }
        },
    )


# ── Health Endpoints (no auth, no prefix) ─────────────────────────────────────

@app.get("/health", tags=["Health"])
async def health() -> dict:
    """Liveness probe — always returns 200 if process is running."""
    return {"status": "ok"}


@app.get("/health/ready", tags=["Health"])
async def readiness() -> JSONResponse:
    """
    Readiness probe — checks PostgreSQL, Ollama, and FAISS.
    Returns 200 when ready, 503 when degraded.
    """
    checks: dict[str, str] = {}
    degraded = False

    # Check PostgreSQL
    try:
        from app.database.session import check_db_connection
        await check_db_connection()
        checks["database"] = "up"
    except Exception as e:
        logger.error("Database health check failed", error=str(e))
        checks["database"] = "down"
        degraded = True

    # Check Ollama
    try:
        import httpx
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{settings.ollama_base_url}/api/tags")
            if resp.status_code == 200:
                models = [m["name"] for m in resp.json().get("models", [])]
                if any(settings.ollama_model in m for m in models):
                    checks["ollama"] = "up"
                else:
                    checks["ollama"] = "model_missing"
                    degraded = True
            else:
                checks["ollama"] = "down"
                degraded = True
    except Exception as e:
        logger.warning("Ollama health check failed", error=str(e))
        checks["ollama"] = "down"
        degraded = True

    # Check FAISS directory
    import os
    faiss_path = settings.faiss_index_path
    os.makedirs(faiss_path, exist_ok=True)
    if os.access(faiss_path, os.W_OK):
        checks["faiss"] = "up"
    else:
        checks["faiss"] = "warning"

    status_code = 503 if degraded else 200
    status = "degraded" if degraded else "ready"

    return JSONResponse(
        status_code=status_code,
        content={"status": status, "checks": checks},
    )


# ── API Router (v1) ───────────────────────────────────────────────────────────
from app.api.router import api_router
app.include_router(api_router, prefix="/api/v1")
