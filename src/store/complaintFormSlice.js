import { createSlice } from "@reduxjs/toolkit";

export const FIELD_ALIASES = {
  strength: "dosage_strength",
  product_strength: "dosage_strength",
  batch_lot_number: "batch_number",
  complaint_source: "originating_site",
  manufacturing_site: "originating_site",
};

export const INITIAL_FIELDS = {
  originating_site: "",
  manufacturing_site: "",
  customer_name: "",
  customer_location: "",
  product_name: "",
  dosage_strength: "",
  dosage_unit: "",
  batch_number: "",
  manufacturing_date: "",
  expiry_date: "",
  impacted_material: "",
  affected_quantity: "",
  product_type: "",
  complaint_category: "",
  complaint_description: "",
  structured_summary: "",
  severity: "",
  likely_root_cause: "",
  suggested_next_action: "",
  capa_priority: "",
  corrective_action: "",
  preventive_action: "",
};

const RISK_RELEVANT_FIELDS = new Set([
  "product_name",
  "complaint_category",
  "affected_quantity",
  "product_type",
]);

function normalizeFieldName(field) {
  return FIELD_ALIASES[field] || field;
}

const initialState = {
  complaintId: null,
  fields: INITIAL_FIELDS,
  riskAssessment: null,
  potentialDuplicates: [],
  recentlyUpdatedFields: [],
  completeness: { is_complete: false, missing_fields: [] },
  status: "draft",
  riskAssessmentStale: false,
  isCommitting: false,
  commitError: null,
};

const complaintFormSlice = createSlice({
  name: "complaintForm",
  initialState,
  reducers: {
    updateFieldManually(state, action) {
      const { field, value } = action.payload;
      state.fields[field] = value;
      if (RISK_RELEVANT_FIELDS.has(field) && state.riskAssessment) {
        state.riskAssessmentStale = true;
      }
    },
    applyAiPatch(state, action) {
      const { updated_fields = {}, risk_assessment, completeness, potential_duplicates, status, complaint_id } = action.payload;
      Object.entries(updated_fields).forEach(([field, value]) => {
        if (value !== null && value !== undefined && value !== "") {
          const normalized = normalizeFieldName(field);
          state.fields[normalized] = value;
        }
      });
      if (complaint_id && typeof complaint_id === "number") state.complaintId = complaint_id;
      if (risk_assessment && Object.keys(risk_assessment).length) {
        state.riskAssessment = risk_assessment;
        state.riskAssessmentStale = false;
        if (risk_assessment.severity) state.fields.severity = risk_assessment.severity;
        if (risk_assessment.likely_root_cause) state.fields.likely_root_cause = risk_assessment.likely_root_cause;
        if (risk_assessment.suggested_next_action) {
          state.fields.suggested_next_action = risk_assessment.suggested_next_action;
        }
        if (risk_assessment.capa_priority) state.fields.capa_priority = risk_assessment.capa_priority;
        if (risk_assessment.corrective_action) state.fields.corrective_action = risk_assessment.corrective_action;
        if (risk_assessment.preventive_action) state.fields.preventive_action = risk_assessment.preventive_action;
      }
      if (!state.fields.structured_summary && action.payload?.reply_message) {
        state.fields.structured_summary = action.payload.reply_message;
      }
      if (completeness) state.completeness = completeness;
      if (potential_duplicates) state.potentialDuplicates = potential_duplicates;
      if (status) state.status = status;
      state.recentlyUpdatedFields = Object.keys(updated_fields).map(normalizeFieldName);
    },
    setComplaintId(state, action) {
      state.complaintId = action.payload;
    },
    hydrateComplaint(state, action) {
      const complaint = action.payload;
      state.complaintId = complaint.id;
      Object.keys(INITIAL_FIELDS).forEach((field) => {
        if (complaint[field] !== undefined && complaint[field] !== null) state.fields[field] = complaint[field];
      });
      state.status = complaint.status || "draft";
      state.riskAssessment = complaint.risk_assessment || null;
    },
    clearRecentlyUpdated(state) {
      state.recentlyUpdatedFields = [];
    },
    setCommitState(state, action) {
      state.isCommitting = action.payload.isCommitting ?? state.isCommitting;
      state.commitError = action.payload.commitError ?? null;
    },
    resetForm() {
      return initialState;
    },
  },
});

export const {
  updateFieldManually,
  applyAiPatch,
  setComplaintId,
  hydrateComplaint,
  clearRecentlyUpdated,
  setCommitState,
  resetForm,
} = complaintFormSlice.actions;

export default complaintFormSlice.reducer;
