"""Logger for recording RAG evaluation triplets."""

import json
import logging
from datetime import datetime
from config import TRIPLET_LOG_PATH
from models.schemas import EvalTriplet

logger = logging.getLogger(__name__)


def log_triplet(
    question: str,
    context_chunks: list[str],
    answer: str,
    reference: str | None = None,
    mode: str = "self_correcting",
    response_type: str = "confident",
    duration_ms: float | None = None,
) -> str:
    """Record a query-context-response triplet for evaluation.

    Args:
        question: User query
        context_chunks: Text snippets retrieved
        answer: Generated system answer
        reference: Ground truth reference answer if available
        mode: baseline or self_correcting
        response_type: confident, low_confidence, or conflict
        duration_ms: Wall-clock time the query took, in milliseconds

    Returns:
        JSON string of the logged triplet
    """
    triplet = EvalTriplet(
        question=question,
        context_chunks=context_chunks,
        answer=answer,
        reference=reference,
        mode=mode,
        response_type=response_type,
        duration_ms=duration_ms,
    )
    
    try:
        with open(TRIPLET_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(triplet.model_dump_json() + "\n")
        logger.info(f"Successfully logged triplet for query: '{question[:40]}...' [mode={mode}]")
    except Exception as e:
        logger.error(f"Failed to log triplet: {e}")
        
    return triplet.model_dump_json()
