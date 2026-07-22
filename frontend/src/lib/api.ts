import type {
  DocumentsResponse,
  EvaluationResults,
  IngestResult,
  Mode,
  QueryResponse,
  StatsResponse,
  TestQuestion,
} from "./types";

// In dev, the Vite server (5173) and API (8000) are separate origins.
// In the production build, FastAPI serves the static frontend, so the API is
// same-origin and relative paths ("") are correct.
const API_URL =
  import.meta.env.VITE_API_URL ?? (import.meta.env.DEV ? "http://127.0.0.1:8000" : "");

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, init);
  if (!res.ok) {
    throw new Error(`${path} failed with status ${res.status}`);
  }
  return res.json() as Promise<T>;
}

export function getDocuments(): Promise<DocumentsResponse> {
  return request<DocumentsResponse>("/documents");
}

export function queryRag(question: string, mode: Mode, topK = 5): Promise<QueryResponse> {
  return request<QueryResponse>("/query", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, mode, top_k: topK }),
  });
}

export function ingestDocument(file: File): Promise<IngestResult> {
  const form = new FormData();
  form.append("file", file);
  return request<IngestResult>("/ingest", { method: "POST", body: form });
}

export function ingestDemoDocuments(): Promise<{ success: boolean; message: string; files: IngestResult[] }> {
  return request("/ingest_demo", { method: "POST" });
}

export function runEvaluation(): Promise<{ success: boolean; results: EvaluationResults }> {
  return request("/evaluate", { method: "POST" });
}

export function getLatestEvaluation(): Promise<{ success: boolean; results: EvaluationResults | null }> {
  return request("/evaluate/latest");
}

export function getStats(): Promise<StatsResponse> {
  return request("/stats");
}

export function getTestQuestions(): Promise<{ success: boolean; questions: TestQuestion[] }> {
  return request("/test_questions");
}

export function resetDatabase(): Promise<{ success: boolean; message: string }> {
  return request("/reset", { method: "POST" });
}
