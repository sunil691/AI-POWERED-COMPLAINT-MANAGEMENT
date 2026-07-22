"""Database initialization hooks for future migrations and models."""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def initialize_database() -> None:
    """Initialize database infrastructure without creating domain tables."""
    logger.info("Database initialization hook completed; migrations are managed by Alembic")