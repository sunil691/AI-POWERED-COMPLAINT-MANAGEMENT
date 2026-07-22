import { AlertCircle } from "lucide-react";

export default function CompletenessBanner({ completeness }) {
  if (!completeness || completeness.is_complete || !completeness.missing_fields?.length) return null;
  return (
    <div className="completeness-banner">
      <AlertCircle size={17} />
      <div>
        <strong>More information needed</strong>
        <span>{completeness.missing_fields.join(", ")}</span>
      </div>
    </div>
  );
}
