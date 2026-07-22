export type ResponseType = "confident" | "low_confidence" | "conflict";

export type Mode = "self_correcting" | "baseline";

export interface Citation {
  doc_name: string;
  section: string | null;
  effective_date: string | null;
  snippet: string;
  relevance_score: number | null;
}

export interface ConflictReport {
  snippet_a: string;
  source_a: string;
  date_a: string | null;
  snippet_b: string;
  source_b: string;
  date_b: string | null;
  explanation: string;
  field_of_conflict: string;
}

export interface RAGResponse {
  response_type: ResponseType;
  answer: string;
  confidence_score: number;
  citations: Citation[];
  conflict_report: ConflictReport | null;
  retry_trace: string[];
  missing_info: string | null;
  processing_steps: string[];
}

export interface QueryResponse {
  success: boolean;
  data?: RAGResponse;
  error?: string;
}

export interface DocumentMetadata {
  title: string;
  effective_date: string | null;
  doc_id: string | null;
  version: string | null;
  doc_type: string | null;
  summary: string | null;
}

export interface IngestResult {
  success: boolean;
  filename: string;
  chunks_added: number;
  metadata: DocumentMetadata;
}

export interface DocumentsResponse {
  success: boolean;
  documents: string[];
  total_chunks: number;
}

export interface TestQuestion {
  question: string;
  reference: string;
  category: string;
}

export interface RagasScores {
  [metric: string]: number;
}

export interface EvaluationModeResult {
  scores?: RagasScores;
  count: number;
  error?: string;
}

export interface EvaluationResults {
  [mode: string]: EvaluationModeResult;
}

export interface StatsResponse {
  success: boolean;
  total_queries: number;
  confident_pct: number;
  conflict_count: number;
  low_confidence_count: number;
  avg_duration_ms: number;
}
