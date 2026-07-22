"""Structured AI copilot endpoint."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService

router = APIRouter(tags=["chat"])


def get_chat_service(database: Session = Depends(get_db)) -> ChatService:
	"""Provide a chat service bound to the request database session."""
	return ChatService(database)


@router.post("/chat", response_model=ChatResponse)
def chat(
	request: ChatRequest,
	service: ChatService = Depends(get_chat_service),
) -> ChatResponse:
	"""Accept a copilot message without invoking an AI provider yet."""
	return service.process_message(request)
