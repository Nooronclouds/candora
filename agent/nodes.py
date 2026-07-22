"""Core node functions for the LangGraph self-correcting RAG workflow."""

import json
import logging
from agent.llm_client import generate_text
from agent.state import RAGState
from agent.prompts import (
    SUFFICIENCY_CHECK_PROMPT,
    QUERY_REFINEMENT_PROMPT,
    CONFLICT_DETECTION_PROMPT,
    ANSWER_GENERATION_PROMPT,
    LOW_CONFIDENCE_PROMPT,
)
from config import LLM_TEMPERATURE, TOP_K_RESULTS
from models.schemas import (
    ConflictReport,
    RAGResponse,
    ResponseType,
    Citation,
)

logger = logging.getLogger(__name__)

# Lazy-loaded indexer (avoid circular imports and startup cost)
_indexer = None

def _get_indexer():
    global _indexer
    if _indexer is None:
        from ingestion.indexer import VectorIndexer
        _indexer = VectorIndexer()
    return _indexer


def retrieve_context(state: RAGState) -> dict:
    """Retrieve relevant document chunks from ChromaDB.
    
    Uses the current query (original or refined) to search the vector store.
    """
    query = state.get("current_query") or state["query"]
    steps = list(state.get("processing_steps") or [])
    steps.append(f"🔍 Retrieving context for: '{query[:80]}...'")
    
    indexer = _get_indexer()
    results = indexer.search(query=query, top_k=TOP_K_RESULTS)
    
    chunk_texts = results["documents"][0] if results["documents"] and results["documents"][0] else []
    chunk_metadatas = results["metadatas"][0] if results["metadatas"] and results["metadatas"][0] else []
    chunk_distances = results["distances"][0] if results.get("distances") and results["distances"][0] else []

    steps.append(f"📄 Retrieved {len(chunk_texts)} chunks")

    return {
        "retrieved_chunks": results,
        "chunk_texts": chunk_texts,
        "chunk_metadatas": chunk_metadatas,
        "chunk_distances": chunk_distances,
        "processing_steps": steps,
    }


def check_sufficiency(state: RAGState) -> dict:
    """Evaluate if retrieved context is sufficient to answer the query.
    
    Sends chunks + query to Gemini and asks for a structured verdict:
    SUFFICIENT, INSUFFICIENT, or CONFLICTING.
    """
    query = state["query"]
    chunk_texts = state.get("chunk_texts", [])
    steps = list(state.get("processing_steps") or [])
    
    if state.get("mode") == "baseline":
        steps.append("⚠️ Baseline mode: skipping self-correction")
        return {
            "sufficiency_status": "SUFFICIENT",
            "sufficiency_reason": "Baseline mode requested.",
            "processing_steps": steps,
        }

    
    if not chunk_texts:
        steps.append("⚠️ No context retrieved — marking as INSUFFICIENT")
        return {
            "sufficiency_status": "INSUFFICIENT",
            "sufficiency_reason": "No documents were retrieved from the knowledge base.",
            "refined_query": query,  # retry with same query
            "processing_steps": steps,
        }
    
    # Format context for the prompt
    context_str = _format_chunks_for_prompt(chunk_texts, state.get("chunk_metadatas", []))
    
    prompt = SUFFICIENCY_CHECK_PROMPT.format(
        query=query,
        context=context_str
    )
    
    steps.append("🧠 Running sufficiency check...")
    
    try:
        response_text = generate_text(prompt, temperature=0.0, json_mode=True)

        result = json.loads(response_text)
        status = result.get("status", "INSUFFICIENT")
        reason = result.get("reason", "No reason provided")
        
        steps.append(f"✅ Sufficiency verdict: {status}")
        
        update = {
            "sufficiency_status": status,
            "sufficiency_reason": reason,
            "processing_steps": steps,
        }
        
        if status == "INSUFFICIENT":
            update["refined_query"] = result.get("refined_query", query)
        elif status == "CONFLICTING":
            update["conflict_report"] = {
                "conflicting_snippets": result.get("conflicting_snippets", [])
            }
        
        return update
        
    except Exception as e:
        logger.error(f"Sufficiency check failed: {e}")
        steps.append(f"❌ Sufficiency check error: {e}")
        return {
            "sufficiency_status": "SUFFICIENT",  # Fail-open: proceed with answer
            "sufficiency_reason": f"Sufficiency check failed ({e}), proceeding with available context",
            "processing_steps": steps,
        }


def refine_query(state: RAGState) -> dict:
    """Generate a refined search query based on what information is missing."""
    query = state["query"]
    previous_query = state.get("current_query") or query
    reason = state.get("sufficiency_reason", "Unknown")
    retry_count = state.get("retry_count") or 0
    steps = list(state.get("processing_steps") or [])
    
    prompt = QUERY_REFINEMENT_PROMPT.format(
        query=query,
        previous_query=previous_query,
        reason=reason,
        missing_info=state.get("refined_query", "Not specified")
    )
    
    steps.append(f"🔄 Refining query (attempt {retry_count + 1})...")
    
    try:
        response_text = generate_text(prompt, temperature=0.3)

        refined = response_text.strip().strip('"')
        steps.append(f"🔄 Refined query: '{refined[:80]}...'")
        
        return {
            "current_query": refined,
            "refined_query": refined,
            "retry_count": retry_count + 1,
            "processing_steps": steps,
        }
    except Exception as e:
        logger.error(f"Query refinement failed: {e}")
        steps.append(f"❌ Query refinement failed: {e}")
        return {
            "retry_count": retry_count + 1,
            "processing_steps": steps,
        }


def detect_conflicts(state: RAGState) -> dict:
    """Analyze retrieved chunks for contradictions and produce a conflict report."""
    query = state["query"]
    chunk_texts = state.get("chunk_texts", [])
    steps = list(state.get("processing_steps") or [])
    
    context_str = _format_chunks_for_prompt(chunk_texts, state.get("chunk_metadatas", []))
    conflicting_snippets = state.get("conflict_report", {}).get("conflicting_snippets", [])
    
    prompt = CONFLICT_DETECTION_PROMPT.format(
        query=query,
        context=context_str,
        conflicting_snippets=json.dumps(conflicting_snippets, indent=2)
    )
    
    steps.append("🔴 Analyzing conflicts...")
    
    try:
        response_text = generate_text(prompt, temperature=0.0, json_mode=True)

        conflict_data = json.loads(response_text)
        steps.append(f"🔴 Conflict detected: {conflict_data.get('field_of_conflict', 'Unknown')}")
        
        return {
            "conflict_report": conflict_data,
            "processing_steps": steps,
        }
    except Exception as e:
        logger.error(f"Conflict detection failed: {e}")
        steps.append(f"❌ Conflict detection error: {e}")
        return {
            "conflict_report": {
                "snippet_a": conflicting_snippets[0] if conflicting_snippets else "Unknown",
                "source_a": "Unknown",
                "snippet_b": conflicting_snippets[1] if len(conflicting_snippets) > 1 else "Unknown",
                "source_b": "Unknown",
                "explanation": f"Conflict analysis failed: {e}",
                "field_of_conflict": "Unknown",
            },
            "processing_steps": steps,
        }


def generate_response(state: RAGState) -> dict:
    """Generate the final response based on the agent's findings.
    
    Produces one of three response types:
    1. Confident — full answer with citations
    2. Low-Confidence — partial answer after retries exhausted
    3. Conflict — halted with conflict report
    """
    query = state["query"]
    chunk_texts = state.get("chunk_texts", [])
    chunk_metadatas = state.get("chunk_metadatas", [])
    chunk_distances = state.get("chunk_distances", [])
    status = state.get("sufficiency_status", "SUFFICIENT")
    steps = list(state.get("processing_steps") or [])
    
    context_str = _format_chunks_for_prompt(chunk_texts, chunk_metadatas)
    
    # --- CONFLICT RESPONSE ---
    if status == "CONFLICTING" and state.get("conflict_report"):
        steps.append("🔴 Generating conflict response")
        conflict = state["conflict_report"]
        
        response = RAGResponse(
            response_type=ResponseType.CONFLICT,
            answer="⚠️ **Conflict Detected** — The retrieved documents contain contradictory information. The system has halted to prevent providing inaccurate results. Please review the conflicting sources below and clarify which should take precedence.",
            confidence_score=0.0,
            conflict_report=ConflictReport(**conflict) if isinstance(conflict, dict) else None,
            processing_steps=steps,
            citations=_extract_citations(chunk_metadatas, chunk_texts, chunk_distances),
        )
        
        return {"final_response": response.model_dump(), "processing_steps": steps}
    
    # --- LOW-CONFIDENCE RESPONSE ---
    if status == "INSUFFICIENT":
        steps.append("⚠️ Generating low-confidence response (retries exhausted)")
        prompt = LOW_CONFIDENCE_PROMPT.format(
            query=query,
            context=context_str,
            missing_info=state.get("refined_query", "Not specified"),
            retry_count=state.get("retry_count", 2)
        )
        
        try:
            answer = generate_text(prompt, temperature=LLM_TEMPERATURE)
        except Exception as e:
            answer = f"Error generating low-confidence answer: {e}"
        
        response = RAGResponse(
            response_type=ResponseType.LOW_CONFIDENCE,
            answer=answer,
            confidence_score=0.3,
            processing_steps=steps,
            citations=_extract_citations(chunk_metadatas, chunk_texts, chunk_distances),
            missing_info=state.get("refined_query", "Not specified"),
            retry_trace=steps,
        )
        return {"final_response": response.model_dump(), "processing_steps": steps}
    
    # --- CONFIDENT RESPONSE ---
    steps.append("✅ Generating confident response")
    prompt = ANSWER_GENERATION_PROMPT.format(
        query=query,
        context=context_str
    )
    
    try:
        answer = generate_text(prompt, temperature=LLM_TEMPERATURE)
    except Exception as e:
        answer = f"Error generating confident answer: {e}"
        
    response = RAGResponse(
        response_type=ResponseType.CONFIDENT,
        answer=answer,
        confidence_score=0.9,
        processing_steps=steps,
        citations=_extract_citations(chunk_metadatas, chunk_texts, chunk_distances),
    )
    return {"final_response": response.model_dump(), "processing_steps": steps}


# --- Helper functions ---

def _format_chunks_for_prompt(chunk_texts: list[str], chunk_metadatas: list[dict]) -> str:
    """Format chunk content and metadata for LLM ingestion."""
    formatted = []
    for idx, (text, meta) in enumerate(zip(chunk_texts, chunk_metadatas)):
        doc_name = meta.get("source_doc", "Unknown")
        section = meta.get("section_title", "General")
        date = meta.get("effective_date", "N/A")
        doc_id = meta.get("doc_id", "N/A")
        
        formatted.append(
            f"--- Chunk {idx+1} | Source: {doc_name} | Section: {section} | Date: {date} | DocID: {doc_id} ---\n{text}"
        )
    return "\n\n".join(formatted)


def _extract_citations(
    chunk_metadatas: list[dict],
    chunk_texts: list[str],
    chunk_distances: list[float] | None = None,
) -> list[Citation]:
    """Build a list of Citation Pydantic models from the retrieved chunks.

    ChromaDB's cosine space returns a distance (0 = identical); we convert it
    to a 0-1 relevance score so the UI can show a real similarity indicator.
    """
    distances = chunk_distances or []
    citations = []
    for i, (text, meta) in enumerate(zip(chunk_texts, chunk_metadatas)):
        relevance_score = None
        if i < len(distances) and distances[i] is not None:
            relevance_score = max(0.0, min(1.0, 1.0 - distances[i]))

        citations.append(
            Citation(
                doc_name=meta.get("source_doc", "Unknown"),
                section=meta.get("section_title", "General"),
                effective_date=meta.get("effective_date", "N/A"),
                snippet=text[:200] + "..." if len(text) > 200 else text,
                relevance_score=relevance_score,
            )
        )
    return citations
