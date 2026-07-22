const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, options);
  if (!response.ok) {
    let detail = `Request failed with status ${response.status}`;
    try {
      const payload = await response.json();
      detail = payload.detail || detail;
    } catch {
      // Keep the HTTP error when the server did not return JSON.
    }
    throw new Error(detail);
  }
  if (response.status === 204) return null;
  return response.json();
}

export function createComplaint(fields = {}) {
  return request("/complaints", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(fields),
  });
}

export function sendComplaintMessage(payload) {
  return request("/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export function uploadComplaintPdf(file, complaintId) {
  const formData = new FormData();
  formData.append("file", file);
  if (complaintId) formData.append("complaint_id", complaintId);
  return request("/upload", { method: "POST", body: formData });
}

export function commitComplaint(complaintId, fields, riskAssessment) {
  const backendFields = [
    "customer_name", "product_name", "dosage_strength", "dosage_unit", "batch_number",
    "affected_quantity", "manufacturing_date", "expiry_date", "product_type",
    "originating_site", "impacted_material", "complaint_category",
    "complaint_description", "structured_summary", "severity",
    "suggested_next_action", "capa_priority", "corrective_action",
    "preventive_action",
  ].reduce((payload, field) => ({ ...payload, [field]: fields[field] }), {});
  return request(`/complaints/${complaintId}/commit`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ...backendFields, risk_assessment: riskAssessment }),
  });
}

export function listComplaints(skip = 0, limit = 100) {
  return request(`/complaints?skip=${skip}&limit=${limit}`);
}

export function getComplaint(complaintId) {
  return request(`/complaints/${complaintId}`);
}
