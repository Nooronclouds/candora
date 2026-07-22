import type { EvaluationResults } from "../../lib/types";
import "./ScoreTable.css";

const METRIC_LABELS: Record<string, string> = {
  faithfulness: "Faithfulness",
  answer_relevancy: "Answer Relevance",
  context_precision: "Context Precision",
};

export function ScoreTable({ results }: { results: EvaluationResults }) {
  const metricKeys = new Set<string>();
  for (const mode of Object.values(results)) {
    if (mode.scores) Object.keys(mode.scores).forEach((k) => metricKeys.add(k));
  }
  const modes = Object.keys(results);

  return (
    <table className="score-table">
      <thead>
        <tr>
          <th>Metric</th>
          {modes.map((mode) => (
            <th key={mode}>{mode === "self_correcting" ? "Self-Correcting" : "Baseline"}</th>
          ))}
        </tr>
      </thead>
      <tbody>
        {Array.from(metricKeys).map((key) => (
          <tr key={key}>
            <td>{METRIC_LABELS[key] ?? key}</td>
            {modes.map((mode) => {
              const value = results[mode]?.scores?.[key];
              return (
                <td key={mode} className="mono score-cell">
                  {value !== undefined ? value.toFixed(3) : "—"}
                </td>
              );
            })}
          </tr>
        ))}
        <tr className="score-table-count">
          <td>Sample count</td>
          {modes.map((mode) => (
            <td key={mode} className="mono">
              {results[mode]?.count ?? 0}
            </td>
          ))}
        </tr>
      </tbody>
    </table>
  );
}
