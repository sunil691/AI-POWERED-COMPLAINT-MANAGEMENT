"""Complaint API schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ComplaintFields(BaseModel):
	"""Shared complaint fields used by create, update, and response schemas."""

	customer_name: str | None = Field(default=None, max_length=255)
	customer_location: str | None = Field(default=None, max_length=255)
	product_name: str | None = Field(default=None, max_length=255)
	dosage_strength: str | None = Field(default=None, max_length=100)
	dosage_unit: str | None = Field(default=None, max_length=50)
	batch_number: str | None = Field(default=None, max_length=100)
	affected_quantity: str | None = Field(default=None, max_length=100)
	manufacturing_date: str | None = Field(default=None, max_length=50)
	expiry_date: str | None = Field(default=None, max_length=50)
	product_type: str | None = Field(default=None, max_length=10)
	originating_site: str | None = Field(default=None, max_length=255)
	manufacturing_site: str | None = Field(default=None, max_length=255)
	impacted_material: str | None = Field(default=None, max_length=255)
	complaint_category: str | None = Field(default=None, max_length=100)
	complaint_description: str | None = None
	structured_summary: str | None = None
	severity: str | None = Field(default=None, max_length=50)
	likely_root_cause: str | None = None
	risk_assessment: str | None = None
	suggested_next_action: str | None = None
	capa_priority: str | None = Field(default=None, max_length=50)
	corrective_action: str | None = None
	preventive_action: str | None = None
	status: str = Field(default="draft", max_length=50)


class ComplaintCreate(ComplaintFields):
	"""Payload for creating a complaint draft."""


class ComplaintUpdate(BaseModel):
	"""Partial payload for updating only supplied complaint fields."""

	model_config = ConfigDict(extra="forbid")

	customer_name: str | None = Field(default=None, max_length=255)
	customer_location: str | None = Field(default=None, max_length=255)
	product_name: str | None = Field(default=None, max_length=255)
	dosage_strength: str | None = Field(default=None, max_length=100)
	dosage_unit: str | None = Field(default=None, max_length=50)
	batch_number: str | None = Field(default=None, max_length=100)
	affected_quantity: str | None = Field(default=None, max_length=100)
	manufacturing_date: str | None = Field(default=None, max_length=50)
	expiry_date: str | None = Field(default=None, max_length=50)
	product_type: str | None = Field(default=None, max_length=10)
	originating_site: str | None = Field(default=None, max_length=255)
	manufacturing_site: str | None = Field(default=None, max_length=255)
	impacted_material: str | None = Field(default=None, max_length=255)
	complaint_category: str | None = Field(default=None, max_length=100)
	complaint_description: str | None = None
	structured_summary: str | None = None
	severity: str | None = Field(default=None, max_length=50)
	likely_root_cause: str | None = None
	risk_assessment: str | dict[str, object] | None = None
	suggested_next_action: str | None = None
	capa_priority: str | None = Field(default=None, max_length=50)
	corrective_action: str | None = None
	preventive_action: str | None = None
	status: str | None = Field(default=None, max_length=50)


class ComplaintResponse(ComplaintFields):
	"""Serialized complaint returned by the API."""

	model_config = ConfigDict(from_attributes=True)

	id: int
	complaint_number: str
	created_at: datetime
	updated_at: datetime
	committed_at: datetime | None = None
