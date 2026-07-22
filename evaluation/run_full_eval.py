"""Generate a clean baseline-vs-self-correcting evaluation dataset, then run RAGAS.

Runs every curated test question through BOTH retrieval modes against the live
API, so the logged triplets form a matched comparison set. Then invokes the
RAGAS harness and writes the cached results file the dashboard reads.

Usage (server must be running on :8000):
    python -m evaluation.run_full_eval
"""

import json
import os
import time
import logging
import requests

from evaluation.test_questions import TEST_QUESTIONS
from config import TRIPLET_LOG_PATH, LAST_EVAL_RESULTS_PATH

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

API_URL = "http://127.0.0.1:8000"
PACING_SECONDS = 2.0  # stay well under Groq free-tier RPM


def _clear_triplet_log() -> None:
    if os.path.exists(TRIPLET_LOG_PATH):
        os.remove(TRIPLET_LOG_PATH)
        logger.info("Cleared previous triplet log for a clean comparison run.")


def _run_question(question: str, mode: str) -> str:
    resp = requests.post(
        f"{API_URL}/query",
        json={"question": question, "mode": mode, "top_k": 5},
        timeout=120,
    )
    resp.raise_for_status()
    data = resp.json()
    if not data.get("success"):
        return f"ERROR: {data.get('error')}"
    return data["data"]["response_type"]


def generate_dataset() -> None:
    _clear_triplet_log()
    modes = ["baseline", "self_correcting"]
    total = len(TEST_QUESTIONS) * len(modes)
    done = 0

    for mode in modes:
        logger.info(f"\n=== Generating triplets for mode: {mode} ===")
        for tq in TEST_QUESTIONS:
            done += 1
            question = tq["question"]
            try:
                rtype = _run_question(question, mode)
                logger.info(f"[{done}/{total}] ({mode}) {rtype:<15} | {question[:60]}")
            except Exception as e:
                logger.error(f"[{done}/{total}] ({mode}) FAILED | {question[:60]} | {e}")
            time.sleep(PACING_SECONDS)


def run_ragas() -> None:
    logger.info("\n=== Running RAGAS evaluation (this can take a few minutes) ===")
    resp = requests.post(f"{API_URL}/evaluate", timeout=1200)
    resp.raise_for_status()
    results = resp.json().get("results", {})
    logger.info(json.dumps(results, indent=2, default=str))
    logger.info(f"\nCached results written to: {LAST_EVAL_RESULTS_PATH}")


if __name__ == "__main__":
    generate_dataset()
    run_ragas()
    logger.info("\nDONE.")
