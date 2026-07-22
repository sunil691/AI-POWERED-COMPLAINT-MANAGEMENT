"""PDF upload and text extraction endpoint."""

from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from app.core.exceptions import ResourceNotFoundError
from app.core.config import settings
from app.database.database import get_db
from app.models.chat_message import ChatMessage
from app.models.complaint import Complaint
from app.models.uploaded_document import UploadedDocument
from app.schemas.upload import UploadResponse
from app.services.chat_service import ChatService
from app.services.langgraph_service import run_complaint_graph
from app.services.pdf_service import PDFService

router = APIRouter(tags=["uploads"])


def get_pdf_service() -> PDFService:
	"""Provide a PDF service using application configuration."""
	return PDFService(settings)


@router.post("/upload", response_model=UploadResponse)
async def upload_pdf(
	file: UploadFile = File(...),
	complaint_id: int | None = Form(default=None),
	database: Session = Depends(get_db),
	service: PDFService = Depends(get_pdf_service),
) -> UploadResponse:
	"""Extract text from a PDF and persist its document metadata."""
	complaint = None
	if complaint_id is not None:
		complaint = database.get(Complaint, complaint_id)
		if complaint is None:
			raise ResourceNotFoundError("Complaint", complaint_id)

	content = await file.read()
	file_path, extracted_text = service.process_pdf(
		filename=file.filename or "uploaded.pdf",
		content_type=file.content_type or "application/octet-stream",
		content=content,
	)
	document = UploadedDocument(
		complaint_id=complaint_id,
		filename=file.filename or "uploaded.pdf",
		content_type=file.content_type or "application/pdf",
		file_path=file_path,
		extracted_text=extracted_text,
	)
	database.add(document)
	database.commit()
	database.refresh(document)
	result = run_complaint_graph(
		complaint_id,
		extracted_text,
		ChatService._form_state(complaint),
		database,
	)
	database.add(
		ChatMessage(
			complaint_id=complaint_id,
			role="assistant",
			content=result["reply_message"],
		)
	)
	database.commit()
	return UploadResponse(
		**result,
		filename=document.filename,
		document_id=document.id,
	)
