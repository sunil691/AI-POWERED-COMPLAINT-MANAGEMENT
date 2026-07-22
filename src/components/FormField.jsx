export default function FormField({ label, value, onChange, highlighted, placeholder, type = "text", options, multiline = false }) {
  const className = `form-control${highlighted ? " form-control--updated" : ""}`;
  return (
    <label className="form-field">
      <span>{label}</span>
      {multiline ? (
        <textarea className={className} value={value ?? ""} onChange={(event) => onChange(event.target.value)} placeholder={placeholder} rows={3} />
      ) : options ? (
        <select className={className} value={value ?? ""} onChange={(event) => onChange(event.target.value)}>
          <option value="">Select...</option>
          {options.map((option) => <option key={option} value={option}>{option}</option>)}
        </select>
      ) : (
        <input className={className} type={type} value={value ?? ""} onChange={(event) => onChange(event.target.value)} placeholder={placeholder} />
      )}
    </label>
  );
}
