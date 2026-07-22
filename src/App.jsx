import { Navigate, Route, Routes } from "react-router-dom";
import ComplaintFormPage from "./pages/ComplaintFormPage";
import ComplaintDashboard from "./pages/ComplaintDashboard";
import ComplaintDetailPage from "./pages/ComplaintDetailPage";

export default function App() {
  return <Routes><Route path="/" element={<ComplaintFormPage />} /><Route path="/dashboard" element={<ComplaintDashboard />} /><Route path="/complaints/:complaintId" element={<ComplaintDetailPage />} /><Route path="*" element={<Navigate to="/" replace />} /></Routes>;
}
