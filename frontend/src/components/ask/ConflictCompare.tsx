import { Card } from "../ui/Card";
import type { ConflictReport } from "../../lib/types";
import "./ConflictCompare.css";

export function ConflictCompare({ report }: { report: ConflictReport }) {
  return (
    <div className="conflict-compare">
      <Card accent="topaze" className="conflict-side">
        <h4>Source A</h4>
        <p className="conflict-meta">
          <strong>{report.source_a}</strong>
          {report.date_a && <span className="mono"> · {report.date_a}</span>}
        </p>
        <blockquote>&ldquo;{report.snippet_a}&rdquo;</blockquote>
      </Card>
      <Card accent="topaze" className="conflict-side">
        <h4>Source B</h4>
        <p className="conflict-meta">
          <strong>{report.source_b}</strong>
          {report.date_b && <span className="mono"> · {report.date_b}</span>}
        </p>
        <blockquote>&ldquo;{report.snippet_b}&rdquo;</blockquote>
      </Card>
      <div className="conflict-explanation">
        <p>
          <strong>Explanation:</strong> {report.explanation}
        </p>
        <p className="conflict-field">
          Field of conflict: <span className="mono">{report.field_of_conflict}</span>
        </p>
      </div>
    </div>
  );
}
