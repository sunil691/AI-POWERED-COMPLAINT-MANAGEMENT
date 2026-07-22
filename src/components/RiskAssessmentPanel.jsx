import { AlertTriangle, RefreshCw, ShieldCheck } from "lucide-react";

export default function RiskAssessmentPanel({ assessment, stale, onRegenerate }) {
  if (!assessment) return null;
  return (
    <section className="risk-panel">
      <div className="risk-panel__header">
        <div className="risk-panel__title"><ShieldCheck size={18} /> AI Copilot Risk Assessment</div>
        <span className={`severity severity--${(assessment.severity || "unknown").toLowerCase()}`}>{assessment.severity || "Unrated"}</span>
      </div>
      {stale && (
        <div className="stale-banner">
          <AlertTriangle size={15} /> Risk assessment may be outdated.
          <button type="button" onClick={onRegenerate}><RefreshCw size={14} /> Regenerate</button>
        </div>
      )}
      <div className="risk-grid">
        <div><small>Likely root cause</small><p>{assessment.likely_root_cause || "Not available"}</p></div>
        <div><small>Risk reasoning</small><p>{assessment.risk_reasoning || "Not available"}</p></div>
        <div><small>Suggested next action</small><p>{assessment.suggested_next_action || "Not available"}</p></div>
        <div><small>CAPA priority</small><p>{assessment.capa_priority || "Not assigned"}</p></div>
      </div>
    </section>
  );
}
