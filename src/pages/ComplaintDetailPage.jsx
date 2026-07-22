import { useEffect, useState } from "react";
import { ArrowLeft, CheckCircle2, FileCheck2 } from "lucide-react";
import { Link, useParams } from "react-router-dom";
import { getComplaint } from "../api/complaintsApi";

export default function ComplaintDetailPage() {
  const { complaintId } = useParams();
  const [complaint, setComplaint] = useState(null);
  const [error, setError] = useState(null);
  useEffect(() => { getComplaint(complaintId).then(setComplaint).catch((requestError) => setError(requestError.message)); }, [complaintId]);
  if (error) return <main className="detail-page"><p className="error-text">{error}</p></main>;
  if (!complaint) return <main className="detail-page"><p>Loading complaint...</p></main>;
  return <main className="detail-page"><header className="topbar"><div className="brand"><div className="brand-symbol"><FileCheck2 size={19} /></div><div><span className="eyebrow">QMS ledger / committed record</span><h1>{complaint.complaint_number}</h1></div></div><Link className="quiet-button" to="/dashboard"><ArrowLeft size={16} /> Back to ledger</Link></header><section className="detail-card"><div className="detail-success"><CheckCircle2 size={22} /><div><strong>Complaint committed</strong><span>This record is now in the QMS ledger.</span></div><span className="table-status table-status--committed">committed</span></div><div className="detail-grid">{Object.entries(complaint).filter(([key]) => !["id", "complaint_number", "created_at", "updated_at", "committed_at"].includes(key)).map(([key, value]) => <div key={key}><small>{key.replaceAll("_", " ")}</small><p>{typeof value === "object" ? JSON.stringify(value) : value || "—"}</p></div>)}</div></section></main>;
}
