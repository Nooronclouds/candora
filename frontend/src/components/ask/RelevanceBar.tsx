import "./RelevanceBar.css";

export function RelevanceBar({ score }: { score: number | null }) {
  if (score === null) return null;
  const pct = Math.round(score * 100);
  const tone = score >= 0.8 ? "high" : score >= 0.5 ? "medium" : "low";

  return (
    <span className={`relevance-bar relevance-bar-${tone}`} title={`${pct}% relevant`}>
      <span className="relevance-bar-fill" style={{ width: `${pct}%` }} />
      <span className="relevance-bar-label mono">{score.toFixed(2)}</span>
    </span>
  );
}
