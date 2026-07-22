import { useEffect, useState } from "react";
import { ArrowUpRight, ClipboardList, Plus, RefreshCw } from "lucide-react";
import { Link } from "react-router-dom";
import { listComplaints } from "../api/complaintsApi";

export default function ComplaintDashboard() {
  const [complaints, setComplaints] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  async function loadComplaints() {
    setLoading(true); setError(null);
    try { setComplaints(await listComplaints()); } catch (requestError) { setError(requestError.message); } finally { setLoading(false); }
  }
  useEffect(() => { loadComplaints(); }, []);

  return (
    <main className="dashboard-page">
      <header className="topbar topbar--dashboard"><div className="brand"><div className="brand-symbol"><ClipboardList size={19} /></div><div><span className="eyebrow">Quality operations</span><h1>AIVOA <em>Ledger</em></h1></div></div><div className="dashboard-actions"><button className="quiet-button" type="button" onClick={loadComplaints}><RefreshCw size={16} /> Refresh</button><Link className="primary-button" to="/"><Plus size={17} /> New complaint</Link></div></header>
      <section className="dashboard-content"><div className="form-heading"><div><p className="eyebrow">QMS records</p><h2>Complaint ledger</h2><p>Review the current intake and commitment state across customer complaints.</p></div><span className="record-count">{complaints.length} records</span></div>
        <div className="ledger-table-wrap"><table><thead><tr><th>Reference</th><th>Customer / site</th><th>Product</th><th>Severity</th><th>Status</th><th>Created</th><th /></tr></thead><tbody>{loading ? <tr><td colSpan="7" className="table-empty">Loading records...</td></tr> : error ? <tr><td colSpan="7" className="table-empty error-text">{error}</td></tr> : complaints.length ? complaints.map((complaint) => <tr key={complaint.id}><td><Link to={`/complaints/${complaint.id}`} className="table-link">{complaint.complaint_number}</Link></td><td>{complaint.originating_site || "—"}</td><td>{complaint.product_name || "—"}</td><td><span className={`severity severity--${(complaint.severity || "unknown").toLowerCase()}`}>{complaint.severity || "Unrated"}</span></td><td><span className={`table-status table-status--${complaint.status}`}>{complaint.status}</span></td><td>{complaint.created_at ? new Date(complaint.created_at).toLocaleDateString() : "—"}</td><td><Link to={`/complaints/${complaint.id}`} title="Open complaint"><ArrowUpRight size={17} /></Link></td></tr>) : <tr><td colSpan="7" className="table-empty">No complaints have been logged yet.</td></tr>}</tbody></table></div>
      </section>
    </main>
  );
}
