"""Service health endpoints."""

from __future__ import annotations

from fastapi import APIRouter

from app.core.config import settings
from app.database.database import check_database_health

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check() -> dict[str, str]:
    """Return application metadata and current database connectivity status."""
    database_status = "healthy" if check_database_health() else "unhealthy"
    return {
        "application": settings.app_name,
        "version": settings.app_version,
        "database": database_status,
        "environment": settings.environment,
    }