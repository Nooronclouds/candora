import { Routes, Route } from "react-router-dom";
import { AppShell } from "./components/layout/AppShell";
import { ModeProvider } from "./context/ModeContext";
import { DashboardPage } from "./pages/DashboardPage";
import { AskPage } from "./pages/AskPage";
import { DocumentsPage } from "./pages/DocumentsPage";
import { EvaluationsPage } from "./pages/EvaluationsPage";

export default function App() {
  return (
    <ModeProvider>
      <AppShell>
        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/ask" element={<AskPage />} />
          <Route path="/documents" element={<DocumentsPage />} />
          <Route path="/evaluations" element={<EvaluationsPage />} />
        </Routes>
      </AppShell>
    </ModeProvider>
  );
}
