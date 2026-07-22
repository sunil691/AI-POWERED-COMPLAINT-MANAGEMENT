"""Uploaded complaint document persistence model."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base


class UploadedDocument(Base):
	"""Metadata and extracted text for a PDF uploaded to a complaint."""

	__tablename__ = "uploaded_documents"

	id: Mapped[int] = mapped_column(Integer, primary_key=True)
	complaint_id: Mapped[int | None] = mapped_column(
		ForeignKey("complaints.id", ondelete="CASCADE"), index=True, nullable=True
	)
	filename: Mapped[str] = mapped_column(String(255), nullable=False)
	content_type: Mapped[str] = mapped_column(String(100), nullable=False)
	file_path: Mapped[str | None] = mapped_column(String(1024), nullable=True)
	extracted_text: Mapped[str] = mapped_column(Text, default="", nullable=False)
	created_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True), server_default=func.now(), nullable=False
	)

	complaint = relationship("Complaint", back_populates="uploaded_documents")
