import { NavLink } from "react-router-dom";
import { Mascot } from "../mascot/Mascot";
import { useMode } from "../../context/ModeContext";
import { DashboardIcon, AskIcon, DocumentsIcon, EvaluationsIcon } from "../ui/Icons";
import "./Sidebar.css";

const NAV_ITEMS = [
  { to: "/", label: "Dashboard", icon: DashboardIcon, end: true },
  { to: "/ask", label: "Ask", icon: AskIcon, end: false },
  { to: "/documents", label: "Documents", icon: DocumentsIcon, end: false },
  { to: "/evaluations", label: "Evaluations", icon: EvaluationsIcon, end: false },
];

export function Sidebar() {
  const { mode, setMode } = useMode();

  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <span className="sidebar-logo">CANDORA</span>
        <span className="sidebar-tagline">Trust is the metric</span>
      </div>

      <div className="sidebar-mascot">
        <Mascot state="hello" size={64} />
      </div>

      <nav className="sidebar-nav">
        {NAV_ITEMS.map(({ to, label, icon: Icon, end }) => (
          <NavLink
            key={to}
            to={to}
            end={end}
            className={({ isActive }) => `sidebar-link${isActive ? " sidebar-link-active" : ""}`}
          >
            <Icon />
            {label}
          </NavLink>
        ))}
      </nav>

      <div className="sidebar-section">
        <span className="sidebar-section-label">Retrieval mode</span>
        <select
          className="sidebar-select"
          value={mode}
          onChange={(e) => setMode(e.target.value as typeof mode)}
        >
          <option value="self_correcting">Self-Correcting (Agentic)</option>
          <option value="baseline">Baseline (Standard)</option>
        </select>
      </div>
    </aside>
  );
}
