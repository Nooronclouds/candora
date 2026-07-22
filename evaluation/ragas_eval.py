"""Evaluation runner using RAGAS to measure faithfulness, answer relevancy, and context precision."""

import sys
import types as _types
try:
    import langchain_google_vertexai
    sys.modules["langchain_community.chat_models.vertexai"] = langchain_google_vertexai
except ImportError:
    # ragas imports ChatVertexAI/VertexAI purely for isinstance checks; we never
    # use Vertex AI (Groq is called directly), so a stub satisfies the import.
    _vertexai_shim = _types.ModuleType("langchain_community.chat_models.vertexai")
    class ChatVertexAI:
        pass
    _vertexai_shim.ChatVertexAI = ChatVertexAI
    sys.modules["langchain_community.chat_models.vertexai"] = _vertexai_shim

import os
import json
import pandas as pd
import logging
from datasets import Dataset
from openai import OpenAI
from ragas import evaluate
from ragas.metrics import Faithfulness, AnswerRelevancy, ContextPrecision
from ragas.llms import llm_factory
from ragas.embeddings import BaseRagasEmbedding
from config import GROQ_API_KEY, GROQ_BASE_URL, TRIPLET_LOG_PATH, LLM_MODEL
from ingestion.indexer import VectorIndexer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LocalEmbeddings(BaseRagasEmbedding):
    """Wraps our local ONNX MiniLM embedding function (offline, free) for RAGAS."""

    def __init__(self):
        super().__init__()
        self._ef = VectorIndexer()._embedding_fn

    def embed_text(self, text: str, **kwargs) -> list[float]:
        return self._ef([text])[0]

    async def aembed_text(self, text: str, **kwargs) -> list[float]:
        return self.embed_text(text)


def run_evaluation() -> dict:
    """Run RAGAS evaluation on the logged triplets.

    Returns:
        A dict containing summary scores and comparisons
    """
    if not os.path.exists(TRIPLET_LOG_PATH):
        logger.warning(f"No evaluation log file found at {TRIPLET_LOG_PATH}")
        return {"error": f"No logs found at {TRIPLET_LOG_PATH}. Please run some queries first."}

    # Read logged triplets
    triplets = []
    with open(TRIPLET_LOG_PATH, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                try:
                    triplets.append(json.loads(line))
                except Exception as e:
                    logger.error(f"Failed to parse line: {line}. Error: {e}")

    if not triplets:
        return {"error": "No valid logs found in log file."}

    df = pd.DataFrame(triplets)
    logger.info(f"Loaded {len(df)} logged triplets for evaluation.")

    # Group by mode and run RAGAS
    modes = df["mode"].unique()
    results = {}

    # Initialize RAGAS evaluator against Groq (OpenAI-compatible)
    groq_client = OpenAI(api_key=GROQ_API_KEY, base_url=GROQ_BASE_URL)
    evaluator_llm = llm_factory(model=LLM_MODEL, provider="openai", client=groq_client)
    embeddings = LocalEmbeddings()

    metrics = [
        Faithfulness(llm=evaluator_llm),
        AnswerRelevancy(llm=evaluator_llm, embeddings=embeddings),
        ContextPrecision(llm=evaluator_llm)
    ]

    for mode in modes:
        mode_df = df[df["mode"] == mode]
        if len(mode_df) == 0:
            continue

        logger.info(f"Evaluating {len(mode_df)} samples for mode: {mode}")

        # Prepare HuggingFace Dataset
        data = {
            "question": mode_df["question"].tolist(),
            "answer": mode_df["answer"].tolist(),
            "contexts": mode_df["context_chunks"].tolist(),
        }

        # Map reference to ground_truth if present
        if "reference" in mode_df.columns:
            data["ground_truth"] = mode_df["reference"].fillna("").tolist()
        else:
            data["ground_truth"] = [""] * len(mode_df)

        dataset = Dataset.from_dict(data)

        try:
            eval_result = evaluate(
                dataset=dataset,
                metrics=metrics
            )
            # Aggregate per-metric mean scores from the results DataFrame.
            # (EvaluationResult in ragas 0.4.x is not dict-iterable; to_pandas is stable.)
            scores_df = eval_result.to_pandas()
            metric_names = ["faithfulness", "answer_relevancy", "context_precision"]
            scores = {}
            for name in metric_names:
                if name in scores_df.columns:
                    mean_val = scores_df[name].dropna().mean()
                    if pd.notna(mean_val):
                        scores[name] = round(float(mean_val), 4)

            results[mode] = {
                "scores": scores,
                "count": len(mode_df)
            }
            logger.info(f"Evaluation completed for {mode}: {scores}")
        except Exception as e:
            logger.error(f"RAGAS evaluation failed for mode '{mode}': {e}")
            results[mode] = {"error": str(e), "count": len(mode_df)}

    return results


if __name__ == "__main__":
    res = run_evaluation()
    print(json.dumps(res, indent=2, default=str))
