"""Structured copilot service boundary."""

from __future__ import annotations

import json
from datetime import datetime, timezone

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

        if complaint is not None and "current_form_state" in result:
            self._update_complaint_model(complaint, result["current_form_state"], result.get("risk_assessment"))
            self.database.commit()

        assistant_message = ChatMessage(
            complaint_id=request.complaint_id,
            role="assistant",
            content=result["reply_message"],
        )
        self.database.add(assistant_message)
        self.database.commit()
        return ChatResponse(**result)

    @staticmethod
    def _update_complaint_model(
        complaint: Complaint,
        merged_state: dict[str, object],
        risk_assessment: dict[str, object] | None = None,
    ) -> None:
        db_field_map = {
            "customer_name": "customer_name",
            "customer_location": "customer_location",
            "product_name": "product_name",
            "dosage_strength": "dosage_strength",
            "product_strength": "dosage_strength",
            "dosage_unit": "dosage_unit",
            "batch_number": "batch_number",
            "batch_lot_number": "batch_number",
            "affected_quantity": "affected_quantity",
            "manufacturing_date": "manufacturing_date",
            "expiry_date": "expiry_date",
            "product_type": "product_type",
            "originating_site": "originating_site",
            "complaint_source": "originating_site",
            "manufacturing_site": "manufacturing_site",
            "impacted_material": "impacted_material",
            "complaint_category": "complaint_category",
            "complaint_description": "complaint_description",
            "structured_summary": "structured_summary",
            "severity": "severity",
            "likely_root_cause": "likely_root_cause",
            "suggested_next_action": "suggested_next_action",
            "capa_priority": "capa_priority",
            "corrective_action": "corrective_action",
            "preventive_action": "preventive_action",
        }
        for key, value in merged_state.items():
            attr = db_field_map.get(key)
            if attr and hasattr(complaint, attr) and value is not None and value != "":
                setattr(complaint, attr, value)

        if risk_assessment and isinstance(risk_assessment, dict) and risk_assessment:
            complaint.risk_assessment = json.dumps(risk_assessment)
            if risk_assessment.get("severity"):
                complaint.severity = str(risk_assessment["severity"])
            if risk_assessment.get("likely_root_cause"):
                complaint.likely_root_cause = str(risk_assessment["likely_root_cause"])
            if risk_assessment.get("suggested_next_action"):
                complaint.suggested_next_action = str(risk_assessment["suggested_next_action"])
            if risk_assessment.get("capa_priority"):
                complaint.capa_priority = str(risk_assessment["capa_priority"])
            if risk_assessment.get("corrective_action"):
                complaint.corrective_action = str(risk_assessment["corrective_action"])
            if risk_assessment.get("preventive_action"):
                complaint.preventive_action = str(risk_assessment["preventive_action"])

        complaint.updated_at = datetime.now(timezone.utc)

    @staticmethod
    def _form_state(complaint: Complaint | None) -> dict[str, object]:
        if complaint is None:
            return {}
        return {
            "customer_name": complaint.customer_name or "",
            "customer_location": complaint.customer_location or "",
            "product_name": complaint.product_name or "",
            "dosage_strength": complaint.dosage_strength or "",
            "product_strength": complaint.dosage_strength or "",
            "dosage_unit": complaint.dosage_unit or "",
            "batch_number": complaint.batch_number or "",
            "batch_lot_number": complaint.batch_number or "",
            "affected_quantity": complaint.affected_quantity or "",
            "manufacturing_date": complaint.manufacturing_date or "",
            "expiry_date": complaint.expiry_date or "",
            "product_type": complaint.product_type or "",
            "originating_site": complaint.originating_site or "",
            "complaint_source": complaint.originating_site or "",
            "manufacturing_site": complaint.manufacturing_site or complaint.originating_site or "",
            "impacted_material": complaint.impacted_material or "",
            "complaint_category": complaint.complaint_category or "",
            "complaint_description": complaint.complaint_description or "",
            "structured_summary": complaint.structured_summary or "",
            "severity": complaint.severity or "",
            "likely_root_cause": complaint.likely_root_cause or "",
            "risk_assessment": complaint.risk_assessment or "",
            "suggested_next_action": complaint.suggested_next_action or "",
            "capa_priority": complaint.capa_priority or "",
            "corrective_action": complaint.corrective_action or "",
            "preventive_action": complaint.preventive_action or "",
            "status": complaint.status or "draft",
        }