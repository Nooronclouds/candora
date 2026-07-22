"""FastAPI server for Candora RAG system."""

import sys
import types as _types
try:
    import langchain_google_vertexai
    sys.modules["langchain_community.chat_models.vertexai"] = langchain_google_vertexai
except ImportError:
    # ragas imports ChatVertexAI/VertexAI purely for isinstance checks; we never
    # use Vertex AI (Gemini is called directly), so a stub satisfies the import.
    _vertexai_shim = _types.ModuleType("langchain_community.chat_models.vertexai")
    class ChatVertexAI:
        pass
    _vertexai_shim.ChatVertexAI = ChatVertexAI
    sys.modules["langchain_community.chat_models.vertexai"] = _vertexai_shim

import os
import json
import time
import logging
from pathlib import Path
from collections import Counter
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from models.schemas import QueryRequest, QueryResponse, RAGResponse
from ingestion.ocr import extract_text_from_pdf, extract_text_from_markdown
from ingestion.metadata_extractor import extract_metadata
from ingestion.chunker import chunk_document
from ingestion.indexer import VectorIndexer
from agent.graph import build_graph
from evaluation.logger import log_triplet
from evaluation.test_questions import TEST_QUESTIONS
from config import TRIPLET_LOG_PATH, LAST_EVAL_RESULTS_PATH
# NOTE: `ragas` is heavy (datasets/langchain) — imported lazily inside /evaluate
# so the app boots lean on memory-limited free hosting tiers.

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Candora RAG API", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize vector indexer
indexer = VectorIndexer()

# Compile the LangGraph workflow
rag_graph = build_graph()

# Demo dataset location (used for auto-seed on a fresh deployment)
_DEMO_DIR = Path(__file__).parent.parent / "test_data"


@app.on_event("startup")
async def seed_demo_documents_if_empty():
    """On a fresh deployment the vector store is empty; auto-ingest the demo
    dataset so the live app is usable immediately without manual seeding."""
    try:
        if indexer.get_doc_count() > 0:
            logger.info(f"Vector store already has {indexer.get_doc_count()} chunks — skipping auto-seed.")
            return
        if not _DEMO_DIR.is_dir():
            return
        logger.info("Empty vector store detected — auto-seeding demo dataset...")
        for filename in os.listdir(_DEMO_DIR):
            if filename.endswith(".md"):
                with open(_DEMO_DIR / filename, "r", encoding="utf-8") as f:
                    content = f.read()
                text = extract_text_from_markdown(content, filename)
                metadata = extract_metadata(text, filename)
                chunks = chunk_document(text, filename, metadata)
                indexer.add_chunks(chunks)
        logger.info(f"Auto-seed complete. Vector store now has {indexer.get_doc_count()} chunks.")
    except Exception as e:
        logger.error(f"Auto-seed failed (continuing anyway): {e}")


@app.post("/ingest")
async def ingest_document(file: UploadFile = File(...)):
    """Upload and ingest a document into the vector store."""
    filename = file.filename
    content_type = file.content_type
    logger.info(f"Ingesting file: {filename} ({content_type})")
    
    try:
        # Read file bytes
        file_bytes = await file.read()
        
        # Extract text based on file type
        if content_type == "application/pdf" or filename.lower().endswith(".pdf"):
            text = extract_text_from_pdf(file_bytes, filename)
        elif filename.lower().endswith((".md", ".txt", ".markdown")):
            text = extract_text_from_markdown(file_bytes.decode("utf-8", errors="ignore"), filename)
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {content_type}. Only PDF, MD, and TXT files are supported."
            )
            
        if not text.strip():
            raise HTTPException(status_code=400, detail="Extracted text is empty.")
            
        # Extract metadata using LLM
        metadata = extract_metadata(text, filename)
        
        # Chunk document
        chunks = chunk_document(text, filename, metadata)
        
        # Add chunks to vector database
        added_count = indexer.add_chunks(chunks)
        
        return {
            "success": True,
            "filename": filename,
            "chunks_added": added_count,
            "metadata": metadata.model_dump()
        }
        
    except Exception as e:
        logger.error(f"Ingestion failed for {filename}: {e}")
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")


@app.post("/ingest_demo")
async def ingest_demo_documents():
    """Ingest the synthetic test documents from the test_data folder."""
    demo_dir = r"c:\Users\Noor Laiba Maheen\Desktop\projects\candora\test_data"
    logger.info(f"Ingesting demo files from {demo_dir}")
    
    if not os.path.exists(demo_dir):
        raise HTTPException(status_code=404, detail=f"Demo directory {demo_dir} not found.")
        
    ingested_files = []
    try:
        for filename in os.listdir(demo_dir):
            if filename.endswith(".md"):
                file_path = os.path.join(demo_dir, filename)
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                text = extract_text_from_markdown(content, filename)
                metadata = extract_metadata(text, filename)
                chunks = chunk_document(text, filename, metadata)
                added_count = indexer.add_chunks(chunks)
                
                ingested_files.append({
                    "filename": filename,
                    "chunks_added": added_count,
                    "metadata": metadata.model_dump()
                })
        
        return {
            "success": True,
            "message": f"Successfully ingested {len(ingested_files)} demo files.",
            "files": ingested_files
        }
    except Exception as e:
        logger.error(f"Demo Ingestion failed: {e}")
        raise HTTPException(status_code=500, detail=f"Demo Ingestion failed: {str(e)}")



@app.post("/query", response_model=QueryResponse)
async def query_rag(request: QueryRequest):
    """Query the self-correcting RAG system."""
    question = request.question
    mode = request.mode
    top_k = request.top_k
    
    logger.info(f"Query request: '{question}' | Mode: {mode} | Top K: {top_k}")
    
    try:
        # Check if we have documents in database
        if indexer.get_doc_count() == 0:
            return QueryResponse(
                success=False,
                error="The knowledge base is empty. Please upload some documents first."
            )
            
        # Run through LangGraph
        initial_state = {
            "query": question,
            "current_query": question,
            "mode": mode,
            "retry_count": 0,
            "processing_steps": [],
        }

        # Invoke LangGraph
        started_at = time.perf_counter()
        result_state = rag_graph.invoke(initial_state)
        duration_ms = (time.perf_counter() - started_at) * 1000
        
        final_response_dict = result_state.get("final_response")
        if not final_response_dict:
            return QueryResponse(
                success=False,
                error="Agent did not produce a final response."
            )
            
        # Try to find a reference answer from our curated test questions
        reference = None
        for tq in TEST_QUESTIONS:
            if tq["question"].lower().strip() == question.lower().strip():
                reference = tq["reference"]
                break
                
        # Log triplet for RAGAS evaluation
        chunk_texts = result_state.get("chunk_texts", [])
        answer = final_response_dict.get("answer", "")
        response_type = final_response_dict.get("response_type", "confident")
        
        log_triplet(
            question=question,
            context_chunks=chunk_texts,
            answer=answer,
            reference=reference,
            mode=mode,
            response_type=response_type,
            duration_ms=duration_ms,
        )
        
        # Validate final response as RAGResponse
        rag_response = RAGResponse(**final_response_dict)
        return QueryResponse(success=True, data=rag_response)
        
    except Exception as e:
        logger.error(f"Query execution failed: {e}")
        return QueryResponse(success=False, error=f"Query failed: {str(e)}")


@app.post("/evaluate")
async def evaluate_rag():
    """Run RAGAS evaluation on the log triplets and cache the results."""
    logger.info("Starting RAGAS evaluation...")
    try:
        from evaluation.ragas_eval import run_evaluation  # lazy: heavy import
        eval_results = run_evaluation()
        with open(LAST_EVAL_RESULTS_PATH, "w", encoding="utf-8") as f:
            json.dump(eval_results, f, default=str, indent=2)
        return {"success": True, "results": eval_results}
    except Exception as e:
        logger.error(f"Evaluation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")


# A committed snapshot of results so a fresh deployment shows real numbers
# without re-running RAGAS (which would consume API tokens on every cold start).
_COMMITTED_EVAL_RESULTS = Path(__file__).parent.parent / "evaluation" / "eval_results.json"


@app.get("/evaluate/latest")
async def get_latest_evaluation():
    """Return the most recent RAGAS evaluation without recomputing it.

    Prefers the live run cache; falls back to the committed snapshot so the
    deployed demo displays real numbers out of the box.
    """
    for path in (LAST_EVAL_RESULTS_PATH, _COMMITTED_EVAL_RESULTS):
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return {"success": True, "results": json.load(f)}
            except Exception as e:
                logger.error(f"Failed to read evaluation results at {path}: {e}")
    return {"success": True, "results": None}


@app.get("/stats")
async def get_stats():
    """Aggregate real usage stats from the logged query triplets."""
    if not os.path.exists(TRIPLET_LOG_PATH):
        return {
            "success": True,
            "total_queries": 0,
            "confident_pct": 0,
            "conflict_count": 0,
            "low_confidence_count": 0,
            "avg_duration_ms": 0,
        }

    triplets = []
    with open(TRIPLET_LOG_PATH, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                try:
                    triplets.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

    total = len(triplets)
    if total == 0:
        return {
            "success": True,
            "total_queries": 0,
            "confident_pct": 0,
            "conflict_count": 0,
            "low_confidence_count": 0,
            "avg_duration_ms": 0,
        }

    type_counts = Counter(t.get("response_type", "confident") for t in triplets)
    durations = [t["duration_ms"] for t in triplets if t.get("duration_ms") is not None]

    return {
        "success": True,
        "total_queries": total,
        "confident_pct": round(100 * type_counts.get("confident", 0) / total, 1),
        "conflict_count": type_counts.get("conflict", 0),
        "low_confidence_count": type_counts.get("low_confidence", 0),
        "avg_duration_ms": round(sum(durations) / len(durations), 0) if durations else 0,
    }


@app.get("/test_questions")
async def get_test_questions():
    """Return the curated evaluation question set for display in the UI."""
    return {"success": True, "questions": TEST_QUESTIONS}


@app.get("/documents")
async def get_documents():
    """Get list of all unique ingested source documents."""
    try:
        docs = indexer.get_all_docs()
        return {"success": True, "documents": docs, "total_chunks": indexer.get_doc_count()}
    except Exception as e:
        logger.error(f"Failed to get documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/reset")
async def reset_database():
    """Delete and recreate the ChromaDB collection."""
    try:
        indexer.delete_collection()
        return {"success": True, "message": "Vector store reset successfully."}
    except Exception as e:
        logger.error(f"Reset failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Liveness probe for deployment platforms."""
    return {"status": "ok"}


# --- Static frontend (single-service deployment) ---
# When the React app has been built, FastAPI serves it directly so one
# container hosts both the API and the UI. API routes above take precedence;
# everything else falls through to the SPA's index.html for client routing.
_FRONTEND_DIST = Path(__file__).parent.parent / "frontend" / "dist"

if _FRONTEND_DIST.is_dir():
    app.mount("/assets", StaticFiles(directory=_FRONTEND_DIST / "assets"), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """Serve a static asset if it exists, else the SPA entrypoint."""
        candidate = _FRONTEND_DIST / full_path
        if full_path and candidate.is_file():
            return FileResponse(candidate)
        return FileResponse(_FRONTEND_DIST / "index.html")

    logger.info(f"Serving built frontend from {_FRONTEND_DIST}")
else:
    logger.info("No frontend build found — running API-only (dev mode).")


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("api.main:app", host="0.0.0.0", port=port, reload=False)
