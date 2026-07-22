"""LangGraph state and nodes for structured complaint copilot processing."""

from __future__ import annotations

from functools import lru_cache
from typing import TypedDict
from uuid import uuid4

from sqlalchemy.orm import Session

from app.core.config import settings
from app.services.complaint_service import ComplaintService
from app.services.groq_service import GroqService


REQUIRED_FIELDS_BY_SEVERITY = {
    "Critical": ["product_name", "batch_lot_number", "affected_quantity", "manufacturing_date", "expiry_date", "complaint_description"],
    "Major": ["product_name", "batch_lot_number", "complaint_description"],
    "Minor": ["product_name", "complaint_description"],
}


class ComplaintGraphState(TypedDict, total=False):
    """State passed between complaint copilot workflow nodes."""

    complaint_id: int | None
    message: str
    current_form_state: dict[str, object]
    database_session: Session | None
    extraction_result: dict[str, object]
    updated_fields: dict[str, object]
    risk_assessment: dict[str, object]
    completeness: dict[str, object]
    potential_duplicates: list[dict[str, object]]
    reply_message: str
    status: str


class LangGraphService:
    """Build and execute the complaint workflow."""

    @staticmethod
    @lru_cache(maxsize=1)
    def build_workflow():
        """Compile the complaint workflow."""
        try:
            from langgraph.graph import END, START, StateGraph
        except ImportError as exc:
            raise RuntimeError("LangGraph is required to build the complaint workflow") from exc

        workflow = StateGraph(ComplaintGraphState)
        workflow.add_node("extract_information", extract_information)
        workflow.add_node("merge_updated_fields", merge_updated_fields)
        workflow.add_node("completeness_check", completeness_check)
        workflow.add_node("duplicate_check", duplicate_check)
        workflow.add_node("risk_assessment", risk_assessment)
        workflow.add_node("generate_summary", generate_summary)
        workflow.add_edge(START, "extract_information")
        workflow.add_edge("extract_information", "merge_updated_fields")
        workflow.add_edge("merge_updated_fields", "completeness_check")
        workflow.add_edge("completeness_check", "duplicate_check")
        workflow.add_edge("duplicate_check", "risk_assessment")
        workflow.add_edge("risk_assessment", "generate_summary")
        workflow.add_edge("generate_summary", END)
        return workflow.compile()


def extract_information(state: ComplaintGraphState) -> dict:
    result = GroqService(settings).extract_complaint_fields(
        state["message"], state.get("current_form_state", {})
    )
    return {"extraction_result": result, "updated_fields": result.get("updated_fields", {})}


def merge_updated_fields(state: ComplaintGraphState) -> dict:
    merged = dict(state.get("current_form_state", {}))
    merged.update(state.get("updated_fields", {}))
    return {"current_form_state": merged, "updated_fields": state.get("updated_fields", {})}


def completeness_check(state: ComplaintGraphState) -> dict:
    fields = state.get("current_form_state", {})
    severity = fields.get("severity") or state.get("risk_assessment", {}).get("severity", "Critical")
    required = REQUIRED_FIELDS_BY_SEVERITY.get(severity, REQUIRED_FIELDS_BY_SEVERITY["Critical"])
    missing = [field for field in required if not fields.get(field)]
    return {"completeness": {"is_complete": not missing, "missing_fields": missing}}


def duplicate_check(state: ComplaintGraphState) -> dict:
    """Query committed complaints for deterministic potential duplicates."""
    fields = state.get("current_form_state", {})
    database = state.get("database_session")
    product_name = fields.get("product_name")
    if not product_name or database is None:
        return {"potential_duplicates": []}
    duplicates = ComplaintService(database).find_potential_duplicates(
        product_name=str(product_name),
        batch_number=fields.get("batch_number") or fields.get("batch_lot_number"),
        complaint_category=fields.get("complaint_category"),
        exclude_id=state.get("complaint_id"),
    )
    return {
        "potential_duplicates": [
            {
                "id": complaint.id,
                "complaint_number": complaint.complaint_number,
                "product_name": complaint.product_name,
                "batch_number": complaint.batch_number,
                "created_at": complaint.created_at.isoformat(),
                "status": complaint.status,
            }
            for complaint in duplicates
        ]
    }


def risk_assessment(state: ComplaintGraphState) -> dict:
    fields = state.get("current_form_state", {})
    if not fields.get("product_name"):
        return {"risk_assessment": {}}
    return {"risk_assessment": GroqService(settings).assess_risk(fields)}


def generate_summary(state: ComplaintGraphState) -> dict:
    extraction = state.get("extraction_result", {})
    message = extraction.get("reply_message") or "Complaint information updated."
    completeness = state.get("completeness", {})
    status = "ready_to_commit" if completeness.get("is_complete") else "draft"
    return {"reply_message": message, "status": status}


def run_complaint_graph(
    complaint_id: int | None,
    message: str,
    current_form_state: dict,
    database: Session | None = None,
) -> dict:
    """Run the complaint graph and return the chat response payload."""
    graph = LangGraphService.build_workflow()
    result = graph.invoke({
        "complaint_id": complaint_id,
        "message": message,
        "current_form_state": current_form_state,
        "database_session": database,
    })
    return {
        "complaint_id": complaint_id if complaint_id is not None else f"temp-{uuid4().hex[:8]}",
        "reply_message": result.get("reply_message", "Complaint information updated."),
        "updated_fields": result.get("updated_fields", {}),
        "risk_assessment": result.get("risk_assessment", {}),
        "completeness": result.get("completeness", {"is_complete": False, "missing_fields": []}),
        "potential_duplicates": result.get("potential_duplicates", []),
        "status": result.get("status", "draft"),
    }