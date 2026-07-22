import { useDispatch, useSelector } from "react-redux";
import FormField from "./FormField";
import RiskAssessmentPanel from "./RiskAssessmentPanel";
import CompletenessBanner from "./CompletenessBanner";
import DuplicateWarningBanner from "./DuplicateWarningBanner";
import { updateFieldManually } from "../store/complaintFormSlice";

const sections = [
  {
    number: "01", title: "Origin & Customer Details", fields: [
      ["originating_site", "Originating site", "e.g. Apollo Pharmacy"],
      ["customer_name", "Customer name", "Optional customer reference"],
    ],
  },
  {
    number: "02", title: "Product & Batch Identification", fields: [
      ["product_name", "Product name", "e.g. Amoxicillin Capsules"],
      ["dosage_strength", "Dosage strength", "e.g. 500 mg"],
      ["dosage_unit", "Dosage unit", "e.g. capsules"],
      ["batch_number", "Batch / lot number", "e.g. AMX240602"],
      ["manufacturing_date", "Manufacturing date", "", "date"],
      ["expiry_date", "Expiry date", "", "date"],
    ],
  },
  {
    number: "03", title: "Facility & Material Impact", fields: [
      ["impacted_material", "Impacted material", "e.g. sealed bottle"],
      ["affected_quantity", "Affected quantity", "e.g. 12 capsules"],
      ["product_type", "Product type", "", "text", ["API", "FDF"]],
    ],
  },
  {
    number: "04", title: "Defect Analysis", fields: [
      ["complaint_category", "Complaint category", "e.g. Appearance"],
      ["severity", "Severity", "", "text", ["Critical", "Major", "Minor"]],
      ["complaint_description", "Complaint description", "Describe the observed defect", "text", null, true],
      ["structured_summary", "Structured summary", "AI-generated summary appears here", "text", null, true],
      ["suggested_next_action", "Suggested next action", "", "text", null, true],
      ["capa_priority", "CAPA priority", "", "text", ["High", "Medium", "Low"]],
      ["corrective_action", "Corrective action", "", "text", null, true],
      ["preventive_action", "Preventive action", "", "text", null, true],
    ],
  },
];

export default function ComplaintForm({ onRegenerate }) {
  const dispatch = useDispatch();
  const { fields, recentlyUpdatedFields, riskAssessment, riskAssessmentStale, completeness, potentialDuplicates } = useSelector((state) => state.complaintForm);
  const setField = (field, value) => dispatch(updateFieldManually({ field, value }));

  return (
    <div className="form-stack">
      <CompletenessBanner completeness={completeness} />
      <DuplicateWarningBanner duplicates={potentialDuplicates} />
      {sections.map((section) => (
        <section className="form-section" key={section.number}>
          <div className="section-heading"><span>{section.number}</span><div><h2>{section.title}</h2><p>Capture the information needed for a clear QA record.</p></div></div>
          <div className="field-grid">
            {section.fields.map(([field, label, placeholder, type = "text", options, multiline]) => (
              <FormField key={field} label={label} value={fields[field]} onChange={(value) => setField(field, value)} highlighted={recentlyUpdatedFields.includes(field)} placeholder={placeholder} type={type} options={options} multiline={multiline} />
            ))}
          </div>
          {section.number === "04" && <RiskAssessmentPanel assessment={riskAssessment} stale={riskAssessmentStale} onRegenerate={onRegenerate} />}
        </section>
      ))}
    </div>
  );
}
