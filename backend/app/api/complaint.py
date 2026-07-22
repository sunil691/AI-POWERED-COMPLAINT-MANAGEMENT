"""Complaint CRUD endpoints."""

from __future__ import annotations

from collections.abc import Sequence

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.complaint import Complaint
from app.schemas.complaint import ComplaintCreate, ComplaintResponse, ComplaintUpdate
from app.services.complaint_service import ComplaintService

router = APIRouter(prefix="/complaints", tags=["complaints"])


def get_complaint_service(database: Session = Depends(get_db)) -> ComplaintService:
	"""Provide a complaint service bound to the request database session."""
	return ComplaintService(database)


@router.get("", response_model=list[ComplaintResponse])
def list_complaints(
	skip: int = Query(default=0, ge=0),
	limit: int = Query(default=100, ge=1, le=500),
	service: ComplaintService = Depends(get_complaint_service),
) -> Sequence[Complaint]:
	"""List complaints using bounded pagination."""
	return service.list_complaints(skip=skip, limit=limit)


@router.get("/{complaint_id}", response_model=ComplaintResponse)
def get_complaint(
	complaint_id: int,
	service: ComplaintService = Depends(get_complaint_service),
) -> Complaint:
	"""Retrieve one complaint by database identifier."""
	return service.get_complaint(complaint_id)


@router.post("", response_model=ComplaintResponse, status_code=status.HTTP_201_CREATED)
def create_complaint(
	payload: ComplaintCreate,
	service: ComplaintService = Depends(get_complaint_service),
) -> Complaint:
	"""Create a complaint draft."""
	return service.create_complaint(payload)


@router.put("/{complaint_id}", response_model=ComplaintResponse)
def update_complaint(
	complaint_id: int,
	payload: ComplaintUpdate,
	service: ComplaintService = Depends(get_complaint_service),
) -> Complaint:
	"""Update only fields supplied by the client."""
	return service.update_complaint(complaint_id, payload)


@router.post("/{complaint_id}/commit", response_model=ComplaintResponse)
def commit_complaint(
	complaint_id: int,
	payload: ComplaintUpdate,
	service: ComplaintService = Depends(get_complaint_service),
) -> Complaint:
	"""Finalize reviewed complaint data in the QMS ledger."""
	return service.commit_complaint(complaint_id, payload)


@router.delete("/{complaint_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_complaint(
	complaint_id: int,
	service: ComplaintService = Depends(get_complaint_service),
) -> None:
	"""Delete a complaint and its dependent records."""
	service.delete_complaint(complaint_id)
