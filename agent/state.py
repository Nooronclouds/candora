"""LangGraph state definition for the self-correcting RAG agent."""

from typing import TypedDict, Optional


class RAGState(TypedDict, total=False):
    """State that flows through the LangGraph self-correcting RAG workflow.
    
    Attributes:
        query: The original user question
        current_query: The query currently being searched (may be refined)
        retrieved_chunks: Raw retrieved chunk data from ChromaDB
        chunk_texts: List of chunk text contents for LLM context
        chunk_metadatas: List of chunk metadata dicts
        sufficiency_status: SUFFICIENT | INSUFFICIENT | CONFLICTING
        sufficiency_reason: Explanation of the sufficiency verdict  
        refined_query: Re-formulated query for retry attempts
        retry_count: Current retry attempt number (max 2)
        conflict_report: Conflict details if contradictions detected
        final_response: The structured RAGResponse dict
        mode: 'baseline' or 'self_correcting'
        processing_steps: Log of steps taken by the agent
        error: Error message if something went wrong
    """
    query: str
    current_query: str
    retrieved_chunks: dict
    chunk_texts: list[str]
    chunk_metadatas: list[dict]
    chunk_distances: list[float]
    sufficiency_status: str
    sufficiency_reason: str
    refined_query: str
    retry_count: int
    conflict_report: Optional[dict]
    final_response: Optional[dict]
    mode: str
    processing_steps: list[str]
    error: Optional[str]
