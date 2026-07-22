"""Chat API schemas."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ChatRequest(BaseModel):
	"""User message sent to the structured AI copilot."""

	model_config = ConfigDict(extra="forbid")

	message: str = Field(min_length=1, max_length=20_000)
	complaint_id: int | None = Field(default=None, gt=0)


class ChatResponse(BaseModel):
	"""Structured complaint copilot response."""

	complaint_id: int | str | None = None
	reply_message: str
	updated_fields: dict[str, object]
	risk_assessment: dict[str, object]
	completeness: dict[str, object]
	potential_duplicates: list[dict[str, object]]
	status: str
