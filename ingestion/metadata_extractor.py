"""Structured metadata extraction from documents via the LLM."""

import logging
from agent.llm_client import generate_text
from models.schemas import DocumentMetadata

logger = logging.getLogger(__name__)


def extract_metadata(text: str, filename: str = "document") -> DocumentMetadata:
    """Extract structured metadata from document text using the LLM.

    Uses JSON-mode output to reliably extract:
    - Document title
    - Effective date
    - Policy/Document ID
    - Version number
    - Document type
    - Brief summary

    Args:
        text: Extracted document text
        filename: Source filename for context

    Returns:
        DocumentMetadata Pydantic model
    """
    # Use first 3000 chars for metadata (titles/headers are at the top)
    text_sample = text[:3000]

    prompt = f"""Analyze this document text and extract structured metadata.
The document filename is: {filename}

Document text (first section):
---
{text_sample}
---

Return ONLY a JSON object with these fields:
{{
  "title": "The document's title or name",
  "effective_date": "When this document takes effect (ISO format YYYY-MM-DD if possible, otherwise descriptive, else null)",
  "doc_id": "Any policy number, document ID, or reference number, else null",
  "version": "Version number if mentioned (e.g. '1.0', 'v2', 'Rev. 3'), else null",
  "doc_type": "Classification (policy, report, memo, addendum, guideline, etc.)",
  "summary": "A one-sentence summary of what this document covers"
}}

If a field cannot be determined, use null."""

    try:
        response_text = generate_text(prompt, temperature=0.0, json_mode=True)
        metadata = DocumentMetadata.model_validate_json(response_text)
        logger.info(f"Extracted metadata for '{filename}': title='{metadata.title}', type='{metadata.doc_type}'")
        return metadata

    except Exception as e:
        logger.warning(f"Structured metadata extraction failed for {filename}: {e}. Using fallback.")
        return _fallback_metadata(text, filename)


def _fallback_metadata(text: str, filename: str) -> DocumentMetadata:
    """Heuristic fallback when structured extraction fails."""
    lines = text.strip().split("\n")
    title = lines[0].strip("# ").strip() if lines else filename

    return DocumentMetadata(
        title=title[:200],
        doc_type="unknown",
        summary=f"Document from file: {filename}"
    )
