"""Application exceptions and centralized FastAPI exception handlers."""

from __future__ import annotations

import logging

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


class AppException(Exception):
    """Base exception for expected application-level failures."""

    def __init__(self, detail: str, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR) -> None:
        self.detail = detail
        self.status_code = status_code
        super().__init__(detail)


class ResourceNotFoundError(AppException):
    """Raised when a requested resource does not exist."""

    def __init__(self, resource: str, identifier: object) -> None:
        super().__init__(f"{resource} '{identifier}' was not found", status.HTTP_404_NOT_FOUND)


class InvalidRequestError(AppException):
    """Raised when a request is syntactically valid but semantically invalid."""

    def __init__(self, detail: str) -> None:
        super().__init__(detail, status.HTTP_400_BAD_REQUEST)


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Return a consistent response for HTTP exceptions."""
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Return structured details for invalid request payloads."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Request validation failed", "errors": exc.errors()},
    )


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Return a consistent response for expected application failures."""
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


async def unexpected_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Log unexpected failures without exposing internal implementation details."""
    logger.exception("Unhandled exception for %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected server error occurred"},
    )


def register_exception_handlers(application: FastAPI) -> None:
    """Register all application exception handlers on a FastAPI instance."""
    application.add_exception_handler(AppException, app_exception_handler)
    application.add_exception_handler(HTTPException, http_exception_handler)
    application.add_exception_handler(RequestValidationError, validation_exception_handler)
    application.add_exception_handler(Exception, unexpected_exception_handler)