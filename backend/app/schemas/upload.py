"""Document upload API schemas."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from app.schemas.chat import ChatResponse


class UploadResponse(ChatResponse):
	"""Structured complaint response enriched with upload metadata."""

	model_config = ConfigDict(from_attributes=True)

	filename: str
	document_id: int
