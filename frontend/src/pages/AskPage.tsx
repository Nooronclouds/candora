import { useEffect, useState } from "react";
import { getDocuments, queryRag } from "../lib/api";
import { useMode } from "../context/ModeContext";
import type { RAGResponse } from "../lib/types";
import { Button } from "../components/ui/Button";
import { Card } from "../components/ui/Card";
import { EmptyState } from "../components/ui/EmptyState";
import { Mascot } from "../components/mascot/Mascot";
import { MascotCallout } from "../components/mascot/MascotCallout";
import { ResponseCard } from "../components/ask/ResponseCard";
import "./AskPage.css";

const QUICK_QUERIES = [
  "What is the employee vacation policy and how many days are allowed annually?",
  "What is the threshold for travel expense pre-approval?",
  "What is the standard notice period for voluntary resignation?",
];

type LoadingStage = "idle" | "retrieving" | "verifying";

export function AskPage() {
  const { mode } = useMode();
  const [question, setQuestion] = useState("");
  const [hasDocuments, setHasDocuments] = useState<boolean | null>(null);
  const [stage, setStage] = useState<LoadingStage>("idle");
  const [response, setResponse] = useState<RAGResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getDocuments()
      .then((res) => setHasDocuments(res.total_chunks > 0))
      .catch(() => setHasDocuments(false));
  }, []);

  async function handleAsk(q: string) {
    if (!q.trim() || stage !== "idle") return;
    setError(null);
    setResponse(null);
    setStage("retrieving");

    try {
      setTimeout(() => setStage((s) => (s === "retrieving" ? "verifying" : s)), 700);
      const res = await queryRag(q, mode);
      if (res.success && res.data) {
        setResponse(res.data);
      } else {
        setError(res.error ?? "Query failed for an unknown reason.");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not reach the Candora API.");
    } finally {
      setStage("idle");
    }
  }

  if (hasDocuments === false) {
    return (
      <div className="ask-page">
        <h1>Ask your documents</h1>
        <EmptyState
          mascot={<Mascot state="empty" size={88} />}
          title="Knowledge base is empty"
          description="Go to the Documents tab to upload files or load the demo dataset first."
        />
      </div>
    );
  }

  return (
    <div className="ask-page">
      <h1>Ask your documents</h1>

      <div className="ask-layout">
        <div className="ask-main">
          <Card>
            <div className="ask-input-row">
              <input
                className="ask-input"
                type="text"
                placeholder="What is the employee vacation policy?"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleAsk(question)}
              />
              <Button onClick={() => handleAsk(question)} disabled={stage !== "idle"}>
                Ask Candora 🔍
              </Button>
            </div>

            <div className="ask-quick-queries">
              <span className="ask-quick-label">Quick queries:</span>
              {QUICK_QUERIES.map((q) => (
                <button
                  key={q}
                  type="button"
                  className="ask-quick-chip"
                  onClick={() => {
                    setQuestion(q);
                    handleAsk(q);
                  }}
                >
                  {q.length > 40 ? `${q.slice(0, 40)}…` : q}
                </button>
              ))}
            </div>
          </Card>

          {stage !== "idle" && (
            <MascotCallout
              state={stage === "retrieving" ? "searching" : "reading"}
              text={
                stage === "retrieving"
                  ? "Searching for better context…"
                  : "Verifying sources and checking sufficiency…"
              }
            />
          )}

          {error && (
            <Card accent="cassis">
              <p className="ask-error">{error}</p>
            </Card>
          )}

          {response && (
            <>
              <MascotCallout
                state={
                  response.response_type === "confident"
                    ? "happy"
                    : response.response_type === "conflict"
                      ? "conflict"
                      : "thinking"
                }
                tone={
                  response.response_type === "confident"
                    ? "confident"
                    : response.response_type === "conflict"
                      ? "conflict"
                      : "low-confidence"
                }
                text={
                  response.response_type === "confident"
                    ? "Found a confident answer!"
                    : response.response_type === "conflict"
                      ? "Found a conflict between documents!"
                      : "Context is incomplete — here's a partial answer."
                }
              />
              <ResponseCard response={response} />
            </>
          )}
        </div>

        <Card className="ask-guide">
          <h3>Agent execution guide</h3>
          <ol>
            <li>
              <strong>Retrieve</strong> — looks up matching passages from ChromaDB.
            </li>
            <li>
              <strong>Sufficiency check</strong> — Gemini evaluates if the context fully answers the
              question.
            </li>
            <li>
              <strong>Refinement</strong> — if info is missing, crafts a better query and retries (up to
              2×).
            </li>
            <li>
              <strong>Conflict detection</strong> — if documents disagree, isolates the exact snippets and
              halts cleanly.
            </li>
          </ol>
        </Card>
      </div>
    </div>
  );
}
