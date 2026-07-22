"""Standalone smoke test for the complaint graph."""

import json

from app.services.langgraph_service import run_complaint_graph


sample_input = {
	"complaint_id": None,
	"message": "Apollo Pharmacy reported discolored capsules in Amoxicillin "
		"Capsules 500 mg. Batch number AMX240602. Manufacturing date "
		"March 2026. Expiry date February 2028. 12 capsules affected "
		"in a sealed bottle. Please log this complaint",
	"current_form_state": {},
}


if __name__ == "__main__":
	print(json.dumps(run_complaint_graph(**sample_input), indent=2))