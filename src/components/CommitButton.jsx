import { ArrowRight, CheckCircle2, LoaderCircle } from "lucide-react";
import { useDispatch, useSelector } from "react-redux";
import { commitComplaint } from "../api/complaintsApi";
import { setCommitState, hydrateComplaint } from "../store/complaintFormSlice";
import { useNavigate } from "react-router-dom";

export default function CommitButton() {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { complaintId, fields, riskAssessment, status, isCommitting, commitError } = useSelector((state) => state.complaintForm);
  const REQUIRED_FIELDS = [
    "product_name",
    "batch_number",
    "originating_site",
    "complaint_category",
    "complaint_description",
    "structured_summary",
    "severity",
    "suggested_next_action",
  ];
  const hasAllRequiredFields = REQUIRED_FIELDS.every(field => Boolean(fields[field]?.trim())) && Boolean(riskAssessment);
  const canCommit = Boolean(complaintId) && hasAllRequiredFields && !isCommitting;

  async function handleCommit() {
    if (!canCommit) return;
    dispatch(setCommitState({ isCommitting: true, commitError: null }));
    try {
      const committed = await commitComplaint(complaintId, fields, riskAssessment);
      dispatch(hydrateComplaint(committed));
      dispatch(setCommitState({ isCommitting: false }));
      navigate(`/complaints/${committed.id}`);
    } catch (error) {
      dispatch(setCommitState({ isCommitting: false, commitError: error.message }));
    }
  }

  return (
    <div className="commit-area">
      {commitError && <p className="error-text">{commitError}</p>}
      <button className="commit-button" type="button" onClick={handleCommit} disabled={!canCommit}>
        {isCommitting ? <LoaderCircle className="spin" size={18} /> : status === "committed" ? <CheckCircle2 size={18} /> : <ArrowRight size={18} />}
        {isCommitting ? "Committing..." : "Commit to QMS Ledger"}
      </button>
      {!complaintId && <small>Send a message to create a complaint draft first.</small>}
      {complaintId && !hasAllRequiredFields && <small>Complete the required fields to enable commit.</small>}
    </div>
  );
}
