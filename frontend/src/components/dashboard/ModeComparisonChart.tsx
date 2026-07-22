import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { EvaluationResults } from "../../lib/types";

interface ModeComparisonChartProps {
  results: EvaluationResults;
}

const METRIC_LABELS: Record<string, string> = {
  faithfulness: "Faithfulness",
  answer_relevancy: "Answer Relevance",
  context_precision: "Context Precision",
};

export function ModeComparisonChart({ results }: ModeComparisonChartProps) {
  const metricKeys = new Set<string>();
  for (const mode of Object.values(results)) {
    if (mode.scores) Object.keys(mode.scores).forEach((k) => metricKeys.add(k));
  }

  const data = Array.from(metricKeys).map((key) => ({
    metric: METRIC_LABELS[key] ?? key,
    baseline: results.baseline?.scores?.[key],
    self_correcting: results.self_correcting?.scores?.[key],
  }));

  return (
    <ResponsiveContainer width="100%" height={280}>
      <BarChart data={data} margin={{ top: 8, right: 8, left: -12, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
        <XAxis dataKey="metric" tick={{ fontSize: 12, fill: "var(--color-text-muted)" }} />
        <YAxis domain={[0, 1]} tick={{ fontSize: 12, fill: "var(--color-text-muted)" }} />
        <Tooltip
          contentStyle={{
            background: "var(--color-surface)",
            border: "1px solid var(--color-border)",
            borderRadius: 8,
            fontSize: 13,
          }}
          formatter={(value) => (typeof value === "number" ? value.toFixed(2) : String(value ?? ""))}
        />
        <Legend wrapperStyle={{ fontSize: 13 }} />
        <Bar dataKey="baseline" name="Baseline" fill="var(--color-cool-blue)" radius={[6, 6, 0, 0]} />
        <Bar
          dataKey="self_correcting"
          name="Self-Correcting"
          fill="var(--color-prussian)"
          radius={[6, 6, 0, 0]}
        />
      </BarChart>
    </ResponsiveContainer>
  );
}
