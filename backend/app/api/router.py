"""
Central API router — registers all v1 sub-routers.
New routers are added here as each task is completed.
"""

from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.projects import router as projects_router
from app.api.v1.artifacts import router as artifacts_router
from app.api.v1.workflows import router as workflows_router
from app.api.v1.memory import router as memory_router
from app.api.v1.export import router as export_router
from app.api.v1.chat import router as chat_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(projects_router)
api_router.include_router(artifacts_router)
api_router.include_router(workflows_router)
api_router.include_router(memory_router)
api_router.include_router(export_router)
api_router.include_router(chat_router)
