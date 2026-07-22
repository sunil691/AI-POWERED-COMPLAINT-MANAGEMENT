"""Structured copilot service boundary."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.exceptions import ResourceNotFoundError
from app.models.chat_message import ChatMessage
from app.models.complaint import Complaint
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.langgraph_service import run_complaint_graph


class ChatService:
    """Persist conversation context and expose the future AI processing boundary."""

    def __init__(self, database: Session) -> None:
        self.database = database

    def process_message(self, request: ChatRequest) -> ChatResponse:
        """Store the conversation and run the structured complaint copilot."""
        complaint = None
        if request.complaint_id is not None:
            complaint = self.database.get(Complaint, request.complaint_id)
            if complaint is None:
                raise ResourceNotFoundError("Complaint", request.complaint_id)

        message = ChatMessage(
            complaint_id=request.complaint_id,
            role="user",
            content=request.message,
        )
        self.database.add(message)
        self.database.commit()

        current_form_state = self._form_state(complaint)
        result = run_complaint_graph(
            request.complaint_id,
            request.message,
            current_form_state,
            self.database,
        )
        assistant_message = ChatMessage(
            complaint_id=request.complaint_id,
            role="assistant",
            content=result["reply_message"],
        )
        self.database.add(assistant_message)
        self.database.commit()
        return ChatResponse(**result)

    @staticmethod
    def _form_state(complaint: Complaint | None) -> dict[str, object]:
        if complaint is None:
            return {}
        return {
            "customer_name": complaint.customer_name,
            "product_name": complaint.product_name,
            "product_strength": complaint.dosage_strength,
            "batch_lot_number": complaint.batch_number,
            "affected_quantity": complaint.affected_quantity,
            "manufacturing_date": complaint.manufacturing_date,
            "expiry_date": complaint.expiry_date,
            "product_type": complaint.product_type,
            "complaint_source": complaint.originating_site,
            "complaint_category": complaint.complaint_category,
            "complaint_description": complaint.complaint_description,
            "severity": complaint.severity,
            "risk_assessment": complaint.risk_assessment,
            "suggested_next_action": complaint.suggested_next_action,
            "status": complaint.status,
        }