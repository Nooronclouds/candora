"""PDF and text extraction for document ingestion.

Real PDF text is extracted locally via pypdf (fast, free, no rate limits).
This handles text-based PDFs; it does not perform OCR on scanned/image-only
pages — the demo dataset is markdown and doesn't exercise that path.
"""

import io
import logging
from pypdf import PdfReader

logger = logging.getLogger(__name__)


def extract_text_from_pdf(pdf_bytes: bytes, filename: str = "document.pdf") -> str:
    """Extract text content from PDF bytes.

    Args:
        pdf_bytes: Raw PDF file bytes
        filename: Original filename for logging

    Returns:
        Extracted text content as a string
    """
    logger.info(f"Extracting text from PDF: {filename} ({len(pdf_bytes)} bytes)")

    try:
        reader = PdfReader(io.BytesIO(pdf_bytes))
        pages = [page.extract_text() or "" for page in reader.pages]
        extracted_text = "\n\n".join(pages).strip()
        logger.info(f"Successfully extracted {len(extracted_text)} characters from {filename}")
        return extracted_text

    except Exception as e:
        logger.error(f"PDF extraction failed for {filename}: {e}")
        raise RuntimeError(f"Failed to extract text from PDF '{filename}': {e}") from e


def extract_text_from_markdown(content: str, filename: str = "document.md") -> str:
    """Pass-through for markdown/text files (no OCR needed)."""
    logger.info(f"Loading text file: {filename} ({len(content)} characters)")
    return content
