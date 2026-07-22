"""PDF validation, storage, and text extraction service."""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from app.core.config import Settings
from app.core.exceptions import InvalidRequestError


class PDFService:
	"""Extract text from PDF files without OCR or AI processing."""

	def __init__(self, application_settings: Settings) -> None:
		self.settings = application_settings

	def process_pdf(self, filename: str, content_type: str, content: bytes) -> tuple[str, str]:
		"""Save a PDF and return its storage path and extracted text."""
		if content_type != "application/pdf" and not filename.lower().endswith(".pdf"):
			raise InvalidRequestError("Only PDF files are supported")
		if len(content) > self.settings.max_upload_size:
			raise InvalidRequestError("Uploaded file exceeds the configured size limit")

		target_directory = self.settings.upload_directory
		target_directory.mkdir(parents=True, exist_ok=True)
		safe_name = f"{uuid4().hex}_{Path(filename).name}"
		target_path = target_directory / safe_name
		target_path.write_bytes(content)

		try:
			import fitz
		except ImportError as exc:
			raise RuntimeError("PyMuPDF is required for PDF text extraction") from exc

		try:
			with fitz.open(stream=content, filetype="pdf") as document:
				extracted_text = "\n".join(page.get_text() for page in document).strip()
		except Exception:
			target_path.unlink(missing_ok=True)
			raise

		return str(target_path), extracted_text
