import { AlertTriangle } from "lucide-react";

function relativeDate(value) {
  if (!value) return "recently";
  const days = Math.max(0, Math.floor((Date.now() - new Date(value).getTime()) / 86_400_000));
  if (days === 0) return "today";
  if (days === 1) return "yesterday";
  return `${days} days ago`;
}

export default function DuplicateWarningBanner({ duplicates }) {
  if (!duplicates?.length) return null;
  return (
    <div className="duplicate-banner">
      <AlertTriangle size={17} />
      <div>
        <strong>Possible duplicate complaint</strong>
        {duplicates.slice(0, 3).map((duplicate) => (
          <p key={duplicate.id}>
            Possible duplicate of Complaint #{duplicate.complaint_number} (same product/batch, filed {relativeDate(duplicate.created_at)})
          </p>
        ))}
      </div>
    </div>
  );
}