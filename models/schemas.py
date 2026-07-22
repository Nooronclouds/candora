"""Pydantic data models for the Candora RAG system."""

from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class SufficiencyStatus(str, Enum):
    """Possible outcomes of the sufficiency check."""
    SUFFICIENT = "SUFFICIENT"
    INSUFFICIENT = "INSUFFICIENT"
    CONFLICTING = "CONFLICTING"


class ResponseType(str, Enum):
    """Types of responses the system can produce."""
    CONFIDENT = "confident"
    LOW_CONFIDENCE = "low_confidence"
    CONFLICT = "conflict"


class DocumentMetadata(BaseModel):
    """Metadata extracted from a document by Gemini."""
    title: str = Field(default="Unknown", description="Document title")
    effective_date: Optional[str] = Field(default=None, description="Effective date (ISO format or descriptive)")
    doc_id: Optional[str] = Field(default=None, description="Policy or document ID")
    version: Optional[str] = Field(default=None, description="Document version")
    doc_type: Optional[str] = Field(default=None, description="Type: policy, report, memo, addendum, etc.")
    summary: Optional[str] = Field(default=None, description="Brief one-line summary")


class DocumentChunk(BaseModel):
    """A semantic chunk of a document with metadata."""
    chunk_id: str = Field(description="Unique chunk identifier")
    content: str = Field(description="Chunk text content")
    source_doc: str = Field(description="Original document filename")
    page_number: Optional[int] = Field(default=None, description="Page number in source")
    section_title: Optional[str] = Field(default=None, description="Section header if available")
    metadata: DocumentMetadata = Field(default_factory=DocumentMetadata)
    char_start: Optional[int] = Field(default=None, description="Character offset start in original")
    char_end: Optional[int] = Field(default=None, description="Character offset end in original")


class SufficiencyResult(BaseModel):
    """Result of the sufficiency check performed by the LLM."""
    status: SufficiencyStatus = Field(description="SUFFICIENT, INSUFFICIENT, or CONFLICTING")
    reason: str = Field(description="Explanation of why this verdict was reached")
    missing_info: Optional[str] = Field(default=None, description="What information is missing (if INSUFFICIENT)")
    refined_query: Optional[str] = Field(default=None, description="Suggested refined query (if INSUFFICIENT)")
    conflicting_snippets: Optional[list[str]] = Field(default=None, description="The contradictory passages (if CONFLICTING)")


class Citation(BaseModel):
    """A source citation for an answer."""
    doc_name: str = Field(description="Source document name")
    section: Optional[str] = Field(default=None, description="Section or page reference")
    effective_date: Optional[str] = Field(default=None, description="Document effective date")
    snippet: str = Field(description="Relevant text excerpt")
    relevance_score: Optional[float] = Field(default=None, description="Cosine similarity to the query, 0-1")


class ConflictReport(BaseModel):
    """Report detailing a detected conflict between documents."""
    snippet_a: str = Field(description="First conflicting passage")
    source_a: str = Field(description="Source of first passage")
    date_a: Optional[str] = Field(default=None, description="Effective date of first source")
    snippet_b: str = Field(description="Second conflicting passage")
    source_b: str = Field(description="Source of second passage")
    date_b: Optional[str] = Field(default=None, description="Effective date of second source")
    explanation: str = Field(description="Explanation of the contradiction")
    field_of_conflict: str = Field(description="The topic or field where the conflict exists")


class RAGResponse(BaseModel):
    """Unified response object from the RAG system."""
    response_type: ResponseType = Field(description="Type of response")
    answer: str = Field(description="The generated answer text")
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Confidence level")
    citations: list[Citation] = Field(default_factory=list, description="Source citations")
    conflict_report: Optional[ConflictReport] = Field(default=None, description="Conflict details if detected")
    retry_trace: list[str] = Field(default_factory=list, description="Log of retry attempts")
    missing_info: Optional[str] = Field(default=None, description="What info is still missing")
    processing_steps: list[str] = Field(default_factory=list, description="Steps taken by the agent")


class EvalTriplet(BaseModel):
    """Evaluation triplet for RAGAS scoring."""
    question: str
    context_chunks: list[str]
    answer: str
    reference: Optional[str] = None
    mode: str = Field(description="'baseline' or 'self_correcting'")
    response_type: str = Field(default="confident")
    duration_ms: Optional[float] = Field(default=None, description="Wall-clock time for the query in milliseconds")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class IngestRequest(BaseModel):
    """API request for document ingestion."""
    filename: str
    content_type: str = "application/pdf"


class QueryRequest(BaseModel):
    """API request for querying the RAG system."""
    question: str
    mode: str = Field(default="self_correcting", description="'baseline' or 'self_correcting'")
    top_k: int = Field(default=5, ge=1, le=20)


class QueryResponse(BaseModel):
    """API response wrapper."""
    success: bool
    data: Optional[RAGResponse] = None
    error: Optional[str] = None
