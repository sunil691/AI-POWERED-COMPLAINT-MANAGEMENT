"""Complaint application service."""

from __future__ import annotations

import json
from collections.abc import Sequence
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session

from app.core.exceptions import ResourceNotFoundError
from app.models.complaint import Complaint
from app.schemas.complaint import ComplaintCreate, ComplaintUpdate


class ComplaintService:
	"""Encapsulate complaint persistence and lifecycle operations."""

	def __init__(self, database: Session) -> None:
		self.database = database

	def list_complaints(self, skip: int = 0, limit: int = 100) -> Sequence[Complaint]:
		"""Return a bounded, newest-first complaint collection."""
		statement = (
			select(Complaint)
			.order_by(Complaint.created_at.desc(), Complaint.id.desc())
			.offset(skip)
			.limit(limit)
		)
		return self.database.scalars(statement).all()

	def find_potential_duplicates(
		self,
		product_name: str | None,
		batch_number: str | None,
		complaint_category: str | None,
		exclude_id: int | None = None,
	) -> list[Complaint]:
		"""Return recent committed complaints matching deterministic duplicate rules."""
		if not product_name:
			return []

		product_match = func.lower(Complaint.product_name) == product_name.strip().lower()
		batch_match = (
			batch_number is not None
			and func.lower(Complaint.batch_number) == batch_number.strip().lower()
		)
		category_match = (
			complaint_category is not None
			and func.lower(Complaint.complaint_category) == complaint_category.strip().lower()
		)
		cutoff = datetime.now(timezone.utc) - timedelta(days=30)
		duplicate_match = or_(
			and_(batch_match),
			and_(category_match, Complaint.created_at >= cutoff),
		)
		statement = select(Complaint).where(
			Complaint.status == "committed",
			product_match,
			duplicate_match,
		)
		if exclude_id is not None:
			statement = statement.where(Complaint.id != exclude_id)
		statement = statement.order_by(Complaint.created_at.desc()).limit(5)
		return list(self.database.scalars(statement).all())

	def get_complaint(self, complaint_id: int) -> Complaint:
		"""Return a complaint or raise a domain-aware not-found error."""
		complaint = self.database.get(Complaint, complaint_id)
		if complaint is None:
			raise ResourceNotFoundError("Complaint", complaint_id)
		return complaint

	def create_complaint(self, payload: ComplaintCreate) -> Complaint:
		"""Create and commit a complaint draft."""
		complaint = Complaint(
			complaint_number=self._generate_complaint_number(),
			**payload.model_dump(),
		)
		self.database.add(complaint)
		self.database.commit()
		self.database.refresh(complaint)
		return complaint

	def update_complaint(self, complaint_id: int, payload: ComplaintUpdate) -> Complaint:
		"""Apply only supplied fields, preserving all other complaint state."""
		complaint = self.get_complaint(complaint_id)
		for field, value in payload.model_dump(exclude_unset=True).items():
			setattr(complaint, field, value)
		complaint.updated_at = datetime.now(timezone.utc)
		self.database.commit()
		self.database.refresh(complaint)
		return complaint

	def commit_complaint(self, complaint_id: int, payload: ComplaintUpdate) -> Complaint:
		"""Apply final complaint fields and commit the complaint to the QMS ledger."""
		complaint = self.get_complaint(complaint_id)
		fields = payload.model_dump(exclude_unset=True)
		risk_assessment = fields.get("risk_assessment")
		if isinstance(risk_assessment, dict):
			fields["risk_assessment"] = json.dumps(risk_assessment)
		for field, value in fields.items():
			setattr(complaint, field, value)
		if not complaint.complaint_number:
			complaint.complaint_number = self._generate_complaint_number()
		complaint.status = "committed"
		complaint.committed_at = datetime.now(timezone.utc)
		complaint.updated_at = datetime.now(timezone.utc)
		self.database.commit()
		self.database.refresh(complaint)
		return complaint

	def delete_complaint(self, complaint_id: int) -> None:
		"""Delete a complaint and its related documents and messages."""
		complaint = self.get_complaint(complaint_id)
		self.database.delete(complaint)
		self.database.commit()

	@staticmethod
	def _generate_complaint_number() -> str:
		"""Generate a human-readable unique complaint identifier."""
		timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
		return f"CMP-{timestamp}-{uuid4().hex[:8].upper()}"
