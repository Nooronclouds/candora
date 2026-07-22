import { Badge } from "../ui/Badge";
import { Card } from "../ui/Card";
import { Expander } from "../ui/Expander";
import { ConflictCompare } from "./ConflictCompare";
import { RelevanceBar } from "./RelevanceBar";
import type { RAGResponse } from "../../lib/types";
import "./ResponseCard.css";

const TONE_BY_TYPE = {
  confident: { tone: "confident" as const, label: "Confident Answer", accent: "sage" as const },
  low_confidence: { tone: "low-confidence" as const, label: "Low Confidence Response", accent: "topaze" as const },
  conflict: { tone: "conflict" as const, label: "Conflict Detected", accent: "cassis" as const },
};

export function ResponseCard({ response }: { response: RAGResponse }) {
  const config = TONE_BY_TYPE[response.response_type];

  return (
    <Card accent={config.accent} className={`response-card response-card-${response.response_type}`}>
      <Badge tone={config.tone}>{config.label}</Badge>
      <p className="response-answer">{response.answer}</p>

      {response.response_type === "low_confidence" && response.missing_info && (
        <div className="response-missing">
          <strong>Missing information:</strong> {response.missing_info}
        </div>
      )}

      {response.response_type === "conflict" && response.conflict_report && (
        <ConflictCompare report={response.conflict_report} />
      )}

      {response.citations.length > 0 && (
        <Expander label={`Sources & citations (${response.citations.length})`}>
          {response.citations.map((cite, i) => (
            <div key={i} className="citation">
              <div className="citation-header">
                <p className="citation-meta">
                  <strong>{cite.doc_name}</strong>
                  {cite.section && ` · ${cite.section}`}
                  {cite.effective_date && <span className="mono"> · {cite.effective_date}</span>}
                </p>
                <RelevanceBar score={cite.relevance_score} />
              </div>
              <p className="citation-snippet">&ldquo;{cite.snippet}&rdquo;</p>
            </div>
          ))}
        </Expander>
      )}

      {response.processing_steps.length > 0 && (
        <Expander label="Agent processing steps">
          {response.processing_steps.map((step, i) => (
            <div key={i} className="processing-step">
              {step}
            </div>
          ))}
        </Expander>
      )}
    </Card>
  );
}
