import { useEffect, useState } from "react";
import { getDocuments, ingestDemoDocuments, ingestDocument } from "../lib/api";
import type { DocumentsResponse } from "../lib/types";
import { Button } from "../components/ui/Button";
import { Card } from "../components/ui/Card";
import { EmptyState } from "../components/ui/EmptyState";
import { Mascot } from "../components/mascot/Mascot";
import { Dropzone } from "../components/documents/Dropzone";
import "./DocumentsPage.css";

type Status = { kind: "idle" } | { kind: "busy"; message: string } | { kind: "done"; message: string } | { kind: "error"; message: string };

export function DocumentsPage() {
  const [docs, setDocs] = useState<DocumentsResponse | null>(null);
  const [status, setStatus] = useState<Status>({ kind: "idle" });

  function refresh() {
    getDocuments().then(setDocs).catch(() => setDocs(null));
  }

  useEffect(refresh, []);

  async function handleUpload(file: File) {
    setStatus({ kind: "busy", message: `Processing ${file.name} with Gemini multi-modal OCR…` });
    try {
      const result = await ingestDocument(file);
      setStatus({
        kind: "done",
        message: `Ingested "${result.metadata.title}" — ${result.chunks_added} chunks added.`,
      });
      refresh();
    } catch (err) {
      setStatus({ kind: "error", message: err instanceof Error ? err.message : "Upload failed." });
    }
  }

  async function handleDemoIngest() {
    setStatus({ kind: "busy", message: "Ingesting synthetic demo files…" });
    try {
      const result = await ingestDemoDocuments();
      setStatus({ kind: "done", message: result.message });
      refresh();
    } catch (err) {
      setStatus({ kind: "error", message: err instanceof Error ? err.message : "Demo ingest failed." });
    }
  }

  return (
    <div className="documents-page">
      <h1>Document Management</h1>

      <Card>
        <h3>Upload a document</h3>
        <Dropzone onFileSelected={handleUpload} disabled={status.kind === "busy"} />
      </Card>

      <Card>
        <h3>Or load the demo dataset</h3>
        <p className="documents-demo-desc">
          Pre-loaded synthetic files with conflicting policies, a Q1 report, and a noisy scan — useful for
          exercising every response type.
        </p>
        <Button variant="secondary" onClick={handleDemoIngest} disabled={status.kind === "busy"}>
          ⚡ Ingest synthetic demo files
        </Button>
      </Card>

      {status.kind !== "idle" && (
        <Card className={`documents-status documents-status-${status.kind}`}>{status.message}</Card>
      )}

      <Card>
        <h3>Ingested documents</h3>
        <p className="documents-count">
          Total unique documents: <span className="mono">{docs?.documents.length ?? 0}</span> · Total
          chunks: <span className="mono">{docs?.total_chunks ?? 0}</span>
        </p>
        {!docs || docs.documents.length === 0 ? (
          <EmptyState
            mascot={<Mascot state="empty" size={72} />}
            title="No documents yet"
            description="Upload your first document to get started."
          />
        ) : (
          <table className="documents-table">
            <thead>
              <tr>
                <th>Source document</th>
              </tr>
            </thead>
            <tbody>
              {docs.documents.map((doc) => (
                <tr key={doc}>
                  <td>{doc}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </Card>
    </div>
  );
}
