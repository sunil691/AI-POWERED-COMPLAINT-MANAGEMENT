"""Standalone smoke test for deterministic duplicate complaint detection."""

from datetime import datetime, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.database.database import Base
from app.models.complaint import Complaint
from app.services.langgraph_service import duplicate_check


def main() -> None:
    """Seed complaint history and verify the graph duplicate node output."""
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as database:
        database.add(
            Complaint(
                complaint_number="CMP-DUPLICATE-SMOKE",
                product_name="Amoxicillin",
                batch_number="AMX240602",
                complaint_category="Appearance",
                status="committed",
                created_at=datetime.now(timezone.utc),
            )
        )
        database.commit()
        result = duplicate_check(
            {
                "complaint_id": None,
                "current_form_state": {
                    "product_name": "amoxicillin",
                    "batch_number": "amx240602",
                    "complaint_category": "Appearance",
                },
                "database_session": database,
            }
        )
        assert result["potential_duplicates"][0]["complaint_number"] == "CMP-DUPLICATE-SMOKE"
        print(result)


if __name__ == "__main__":
    main()
