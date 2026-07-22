import { useEffect } from "react";
import { ArrowUpRight, ClipboardList, FileCheck2, Menu, RotateCcw } from "lucide-react";
import { useDispatch, useSelector } from "react-redux";
import ComplaintForm from "../components/ComplaintForm";
import CopilotChat from "../components/CopilotChat";
import CommitButton from "../components/CommitButton";
import { clearRecentlyUpdated, resetForm } from "../store/complaintFormSlice";
import { clearChat, sendMessage } from "../store/chatSlice";
import { Link } from "react-router-dom";

export default function ComplaintFormPage() {
  const dispatch = useDispatch();
  const { recentlyUpdatedFields, status, complaintId } = useSelector((state) => state.complaintForm);

  useEffect(() => {
    if (!recentlyUpdatedFields.length) return undefined;
    const timer = setTimeout(() => dispatch(clearRecentlyUpdated()), 2100);
    return () => clearTimeout(timer);
  }, [dispatch, recentlyUpdatedFields]);

  function startNewComplaint() {
    dispatch(resetForm());
    dispatch(clearChat());
  }

  function regenerateRisk() {
    dispatch(sendMessage("Please regenerate the risk assessment using the current reviewed form values."));
  }

  return (
    <main className="app-shell">
      <section className="workspace-panel">
        <header className="topbar">
          <div className="brand"><div className="brand-symbol"><FileCheck2 size={19} /></div><div><span className="eyebrow">Quality operations</span><h1>AIVOA <em>Complaint Desk</em></h1></div></div>
          <nav><Link to="/dashboard"><ClipboardList size={16} /> Ledger</Link><button type="button" className="new-button" onClick={startNewComplaint}><RotateCcw size={15} /> New complaint</button><button className="menu-button" type="button" title="Menu"><Menu size={19} /></button></nav>
        </header>
        <div className="form-heading"><div><p className="eyebrow">Complaint intake / {complaintId ? `Draft #${complaintId}` : "New record"}</p><h2>Log customer complaint</h2><p>Build a complete, reviewable record with your copilot beside you.</p></div><span className={`status-badge status-badge--${status}`}>{status === "ready_to_commit" ? "Ready to commit" : status}</span></div>
        <ComplaintForm onRegenerate={regenerateRisk} />
        <CommitButton />
      </section>
      <CopilotChat onAiResponse={() => {}} />
    </main>
  );
}
