"""SQLAlchemy engine, declarative base, sessions, and health checks."""

from __future__ import annotations

import logging
from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings

logger = logging.getLogger(__name__)

engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


class Base(DeclarativeBase):
	"""Declarative base for future SQLAlchemy models."""


def get_db() -> Generator[Session, None, None]:
	"""Yield one database session per request and always close it."""
	database = SessionLocal()
	try:
		yield database
	finally:
		database.close()


def check_database_health() -> bool:
	"""Check database connectivity without changing application data."""
	try:
		with engine.connect() as connection:
			connection.execute(text("SELECT 1"))
		return True
	except SQLAlchemyError:
		logger.warning("Database health check failed", exc_info=True)
		return False
