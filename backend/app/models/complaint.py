"""Complaint persistence model."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Index, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base


class Complaint(Base):
	"""A customer complaint and its progressively enriched assessment."""

	__tablename__ = "complaints"
	__table_args__ = (Index("ix_complaints_status", "status"),)

	id: Mapped[int] = mapped_column(Integer, primary_key=True)
	complaint_number: Mapped[str] = mapped_column(String(64), unique=True, index=True)
	customer_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
	product_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
	dosage_strength: Mapped[str | None] = mapped_column(String(100), nullable=True)
	dosage_unit: Mapped[str | None] = mapped_column(String(50), nullable=True)
	batch_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
	affected_quantity: Mapped[str | None] = mapped_column(String(100), nullable=True)
	manufacturing_date: Mapped[str | None] = mapped_column(String(50), nullable=True)
	expiry_date: Mapped[str | None] = mapped_column(String(50), nullable=True)
	product_type: Mapped[str | None] = mapped_column(String(10), nullable=True)
	originating_site: Mapped[str | None] = mapped_column(String(255), nullable=True)
	impacted_material: Mapped[str | None] = mapped_column(String(255), nullable=True)
	complaint_category: Mapped[str | None] = mapped_column(String(100), nullable=True)
	complaint_description: Mapped[str | None] = mapped_column(Text, nullable=True)
	structured_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
	severity: Mapped[str | None] = mapped_column(String(50), nullable=True)
	risk_assessment: Mapped[str | None] = mapped_column(Text, nullable=True)
	suggested_next_action: Mapped[str | None] = mapped_column(Text, nullable=True)
	capa_priority: Mapped[str | None] = mapped_column(String(50), nullable=True)
	corrective_action: Mapped[str | None] = mapped_column(Text, nullable=True)
	preventive_action: Mapped[str | None] = mapped_column(Text, nullable=True)
	status: Mapped[str] = mapped_column(String(50), default="draft", nullable=False)
	committed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
	created_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True), server_default=func.now(), nullable=False
	)
	updated_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
	)

	uploaded_documents = relationship(
		"UploadedDocument", back_populates="complaint", cascade="all, delete-orphan"
	)
	chat_messages = relationship(
		"ChatMessage", back_populates="complaint", cascade="all, delete-orphan"
	)
