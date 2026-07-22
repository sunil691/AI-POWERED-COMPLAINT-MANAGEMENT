"""FastAPI application composition root."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import register_api_routers
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logging
from app.database.init_db import initialize_database
from app.middleware.request_logging import RequestLoggingMiddleware


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncIterator[None]:
	"""Run application startup and shutdown hooks."""
	settings.upload_directory.mkdir(parents=True, exist_ok=True)
	initialize_database()
	yield


configure_logging(settings.log_level)

app = FastAPI(
	title=settings.app_name,
	version=settings.app_version,
	debug=settings.debug,
	lifespan=lifespan,
)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(
	CORSMiddleware,
	allow_origins=settings.allowed_origins,
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)
register_exception_handlers(app)
register_api_routers(app)
