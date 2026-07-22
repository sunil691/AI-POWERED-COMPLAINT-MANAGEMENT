"""Chat message persistence model."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base


class ChatMessage(Base):
	"""A user or assistant message associated with a complaint session."""

	__tablename__ = "chat_messages"

	id: Mapped[int] = mapped_column(Integer, primary_key=True)
	complaint_id: Mapped[int | None] = mapped_column(
		ForeignKey("complaints.id", ondelete="CASCADE"), index=True, nullable=True
	)
	role: Mapped[str] = mapped_column(String(20), nullable=False)
	content: Mapped[str] = mapped_column(Text, nullable=False)
	created_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True), server_default=func.now(), nullable=False
	)

	complaint = relationship("Complaint", back_populates="chat_messages")
