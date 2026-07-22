import { useEffect, useState } from "react";
import { getDocuments, getLatestEvaluation, getStats } from "../lib/api";
import type { DocumentsResponse, EvaluationResults, StatsResponse } from "../lib/types";
import { KpiCard } from "../components/dashboard/KpiCard";
import { ModeComparisonChart } from "../components/dashboard/ModeComparisonChart";
import { Card } from "../components/ui/Card";
import { EmptyState } from "../components/ui/EmptyState";
import { Mascot } from "../components/mascot/Mascot";
import "./DashboardPage.css";

export function DashboardPage() {
  const [stats, setStats] = useState<StatsResponse | null>(null);
  const [docs, setDocs] = useState<DocumentsResponse | null>(null);
  const [evalResults, setEvalResults] = useState<EvaluationResults | null>(null);

  useEffect(() => {
    getStats().then(setStats).catch(() => setStats(null));
    getDocuments().then(setDocs).catch(() => setDocs(null));
    getLatestEvaluation()
      .then((res) => setEvalResults(res.results))
      .catch(() => setEvalResults(null));
  }, []);

  return (
    <div className="dashboard-page">
      <h1>Dashboard</h1>

      <div className="kpi-grid">
        <KpiCard label="Total Queries" value={stats?.total_queries ?? "—"} />
        <KpiCard
          label="Confident Answers"
          value={stats ? `${stats.confident_pct}%` : "—"}
          accentColor="var(--color-sage)"
        />
        <KpiCard
          label="Conflicts Detected"
          value={stats?.conflict_count ?? "—"}
          accentColor="var(--color-topaze)"
        />
        <KpiCard
          label="Avg Response Time"
          value={stats?.avg_duration_ms ? `${(stats.avg_duration_ms / 1000).toFixed(1)}s` : "—"}
          accentColor="var(--color-cassis)"
        />
      </div>

      <div className="dashboard-body">
        <Card className="dashboard-chart-card">
          <h3>Self-Correcting vs Baseline (RAGAS)</h3>
          {evalResults ? (
            <ModeComparisonChart results={evalResults} />
          ) : (
            <EmptyState
              mascot={<Mascot state="empty" size={72} />}
              title="No evaluations yet"
              description="Run a RAGAS evaluation from the Evaluations tab to compare baseline vs self-correcting quality."
            />
          )}
        </Card>

        <Card className="dashboard-docs-card">
          <h3>Top Documents</h3>
          <p className="dashboard-docs-count">
            Total chunks in database: <span className="mono">{docs?.total_chunks ?? 0}</span>
          </p>
          {!docs || docs.documents.length === 0 ? (
            <EmptyState
              mascot={<Mascot state="empty" size={72} />}
              title="No documents yet"
              description="Upload your first document to get started."
            />
          ) : (
            <ul className="dashboard-doc-list">
              {docs.documents.slice(0, 5).map((doc) => (
                <li key={doc}>
                  <span className="dashboard-doc-name">{doc}</span>
                  <span className="dashboard-doc-status">Ingested</span>
                </li>
              ))}
            </ul>
          )}
        </Card>
      </div>
    </div>
  );
}
