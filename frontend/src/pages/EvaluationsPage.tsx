import { useEffect, useState } from "react";
import { getLatestEvaluation, getTestQuestions, runEvaluation } from "../lib/api";
import type { EvaluationResults, TestQuestion } from "../lib/types";
import { Button } from "../components/ui/Button";
import { Card } from "../components/ui/Card";
import { MascotCallout } from "../components/mascot/MascotCallout";
import { ScoreTable } from "../components/evaluations/ScoreTable";
import "./EvaluationsPage.css";

export function EvaluationsPage() {
  const [results, setResults] = useState<EvaluationResults | null>(null);
  const [questions, setQuestions] = useState<TestQuestion[]>([]);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getLatestEvaluation()
      .then((res) => setResults(res.results))
      .catch(() => setResults(null));
    getTestQuestions()
      .then((res) => setQuestions(res.questions))
      .catch(() => setQuestions([]));
  }, []);

  async function handleRun() {
    setRunning(true);
    setError(null);
    try {
      const res = await runEvaluation();
      setResults(res.results);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Evaluation failed.");
    } finally {
      setRunning(false);
    }
  }

  return (
    <div className="evaluations-page">
      <h1>RAGAS Evaluation</h1>

      <Card>
        <p className="evaluations-intro">
          Evaluate the quality of retrieved contexts and generated answers. We measure:
        </p>
        <ul className="evaluations-metrics">
          <li>
            <strong>Faithfulness</strong> — is the answer fully grounded in the retrieved documents?
          </li>
          <li>
            <strong>Answer Relevance</strong> — does the answer directly address the question?
          </li>
          <li>
            <strong>Context Precision</strong> — did the system retrieve relevant chunks first?
          </li>
        </ul>
        <Button onClick={handleRun} disabled={running}>
          🚀 {running ? "Running…" : "Run RAGAS Evaluation"}
        </Button>
        {running && (
          <MascotCallout state="thinking" text="Scoring every logged query with Gemini — about a minute…" />
        )}
        {error && <p className="evaluations-error">{error}</p>}
      </Card>

      {results && (
        <Card>
          <h3>Results</h3>
          <ScoreTable results={results} />
        </Card>
      )}

      <Card>
        <h3>Curated test questions</h3>
        <p className="evaluations-intro">
          These questions are designed to test the limits of OCR, sufficiency loops, and conflicting
          documents:
        </p>
        <table className="evaluations-questions-table">
          <thead>
            <tr>
              <th>Question</th>
              <th>Category</th>
            </tr>
          </thead>
          <tbody>
            {questions.map((q) => (
              <tr key={q.question}>
                <td>{q.question}</td>
                <td>
                  <span className="evaluations-category">{q.category.replace(/_/g, " ")}</span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>
    </div>
  );
}
