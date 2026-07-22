import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# --- Paths ---
BASE_DIR = Path(__file__).parent
CHROMA_DB_PATH = str(BASE_DIR / "chroma_db")
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)
TRIPLET_LOG_PATH = str(LOGS_DIR / "eval_triplets.jsonl")
LAST_EVAL_RESULTS_PATH = str(LOGS_DIR / "last_eval_results.json")

# --- API Keys ---
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_BASE_URL = "https://api.groq.com/openai/v1"

# --- Model Config ---
# llama-3.1-8b-instant: fast, free, generous daily token budget (~500k TPD on
# Groq's free tier). The pipeline is model-agnostic — set LLM_MODEL to any Groq
# chat model (e.g. llama-3.3-70b-versatile) for higher quality at a smaller quota.
LLM_MODEL = os.getenv("LLM_MODEL", "llama-3.1-8b-instant")
LLM_TEMPERATURE = 0.2
LLM_TEMPERATURE_EVAL = 0.0  # For evaluation/structured output

# --- Chunking Config ---
CHUNK_SIZE = 1000  # chars (approx)
CHUNK_OVERLAP = 200  # chars
MAX_CHUNKS_PER_DOC = 100

# --- Retrieval Config ---
TOP_K_RESULTS = 5
COLLECTION_NAME = "candora_docs"

# --- Agent Config ---
MAX_RETRIES = 2
