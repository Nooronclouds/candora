"""Semantic document chunking with markdown awareness."""

import re
import logging
import hashlib
from typing import Optional
from models.schemas import DocumentChunk, DocumentMetadata
from config import CHUNK_SIZE, CHUNK_OVERLAP, MAX_CHUNKS_PER_DOC

logger = logging.getLogger(__name__)


def chunk_document(
    text: str,
    source_doc: str,
    metadata: DocumentMetadata,
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP
) -> list[DocumentChunk]:
    """Split document text into semantic chunks.
    
    Strategy:
    1. Split by markdown headers (##, ###) to preserve section boundaries
    2. Within sections, split by paragraph boundaries (double newlines)
    3. Enforce max chunk size with overlap
    4. Never split within tables (lines starting with |)
    5. Each chunk retains source metadata
    
    Args:
        text: Full document text
        source_doc: Source document filename
        metadata: Extracted document metadata
        chunk_size: Target chunk size in characters
        chunk_overlap: Overlap between consecutive chunks
    
    Returns:
        List of DocumentChunk objects
    """
    if not text.strip():
        logger.warning(f"Empty text for {source_doc}, returning empty chunks")
        return []
    
    # Step 1: Split into sections by markdown headers
    sections = _split_by_headers(text)
    
    # Step 2: Split large sections into paragraph-level chunks
    raw_chunks = []
    for section_title, section_text in sections:
        if len(section_text) <= chunk_size:
            raw_chunks.append((section_title, section_text))
        else:
            sub_chunks = _split_by_paragraphs(section_text, chunk_size, chunk_overlap)
            for sub in sub_chunks:
                raw_chunks.append((section_title, sub))
    
    # Step 3: Build DocumentChunk objects
    chunks = []
    for i, (section_title, content) in enumerate(raw_chunks[:MAX_CHUNKS_PER_DOC]):
        chunk_id = _generate_chunk_id(source_doc, i, content)
        chunk = DocumentChunk(
            chunk_id=chunk_id,
            content=content.strip(),
            source_doc=source_doc,
            section_title=section_title,
            metadata=metadata
        )
        chunks.append(chunk)
    
    logger.info(f"Chunked '{source_doc}' into {len(chunks)} chunks")
    return chunks


def _split_by_headers(text: str) -> list[tuple[Optional[str], str]]:
    """Split text by markdown headers, preserving section titles."""
    # Match lines starting with # (any level)
    header_pattern = re.compile(r'^(#{1,4})\s+(.+)$', re.MULTILINE)
    
    sections = []
    last_end = 0
    current_title = None
    
    for match in header_pattern.finditer(text):
        # Save content before this header
        content = text[last_end:match.start()].strip()
        if content:
            sections.append((current_title, content))
        
        current_title = match.group(2).strip()
        last_end = match.end()
    
    # Don't forget the last section
    remaining = text[last_end:].strip()
    if remaining:
        sections.append((current_title, remaining))
    
    # If no headers found, return entire text as one section
    if not sections:
        sections = [(None, text.strip())]
    
    return sections


def _split_by_paragraphs(
    text: str,
    chunk_size: int,
    overlap: int
) -> list[str]:
    """Split text by paragraph boundaries with overlap."""
    # Split on double newlines (paragraph boundaries)
    paragraphs = re.split(r'\n\s*\n', text)
    
    chunks = []
    current_chunk = []
    current_size = 0
    
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        
        para_size = len(para)
        
        # Check if adding this paragraph exceeds chunk size
        if current_size + para_size > chunk_size and current_chunk:
            # Save current chunk
            chunks.append("\n\n".join(current_chunk))
            
            # Start new chunk with overlap from the end of the previous
            overlap_text = "\n\n".join(current_chunk[-1:])  # Last paragraph as overlap
            if len(overlap_text) <= overlap:
                current_chunk = [overlap_text] if overlap_text else []
                current_size = len(overlap_text)
            else:
                current_chunk = []
                current_size = 0
        
        current_chunk.append(para)
        current_size += para_size
    
    # Don't forget the last chunk
    if current_chunk:
        chunks.append("\n\n".join(current_chunk))
    
    return chunks


def _generate_chunk_id(source_doc: str, index: int, content: str) -> str:
    """Generate a deterministic chunk ID."""
    hash_input = f"{source_doc}:{index}:{content[:100]}"
    return hashlib.sha256(hash_input.encode()).hexdigest()[:16]
