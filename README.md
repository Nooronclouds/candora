# Candora — Self-Correcting Trustworthy RAG

> **Trust is the metric.** A retrieval-augmented generation system that refuses to guess — it verifies whether it has enough context, retries when it doesn't, and halts loudly when documents contradict each other.

**Domain:** AI Engineer · **Problem statement:** Self-Correcting Trustworthy RAG System

---

## The Problem

Standard RAG pipelines fail silently in three ways when documents are messy or conflicting:

1. **Confident hallucination** — the model answers even when the retrieved context is insufficient.
2. **Silent conflict resolution** — when an old policy and a new addendum disagree, the LLM quietly averages them or picks one at random.
3. **No trust signal** — the user can't tell a well-grounded answer from a fabricated one.

Candora addresses all three with an **agentic self-correction loop** built on LangGraph.

---

## How It Works

Every query flows through a LangGraph state machine that gates the answer behind a verification step:

```
          ┌──────────────┐
Query ──▶ │  Retrieve    │ (ChromaDB + local MiniLM embeddings)
          └──────┬───────┘
                 ▼
          ┌──────────────┐      SUFFICIENT ───────────────▶ Confident Answer (with citations)
          │ Sufficiency  │
          │   Check      │──── INSUFFICIENT ──▶ Refine query ──▶ Re-retrieve (max 2×)
          └──────┬───────┘                              │
                 │                                       └─▶ still insufficient ─▶ Low-Confidence Response
                 └──── CONFLICTING ──▶ Conflict Analysis ─▶ HALT ─▶ Conflict-Detected Response
```

The system emits exactly one of **three structured response types**:

| Response type | When | What the user sees |
|---|---|---|
| **Confident** | Context fully answers the query | Answer + explicit `[Doc, Section, Date]` citations + per-chunk relevance scores |
| **Low-Confidence** | Still insufficient after 2 refine-and-retry loops | Partial answer, explicitly marked gaps, "what's missing" note |
| **Conflict-Detected** | Two sources contradict each other | System halts; shows both snippets side-by-side with sources/dates and asks the user to arbitrate |

---

## Evaluation Results (RAGAS)

The headline deliverable for the AI-Engineer track: a measured **hallucination / faithfulness comparison** between a standard baseline RAG and the self-correcting agent, over the same 10-question test set (matched pairs, both modes).

**Hallucination rate on questions the corpus cannot answer** (the metric that matters most):

| Mode | Hallucination rate | RAGAS Context Precision |
|---|---|---|
| Baseline RAG | **100%** (3/3 answered anyway) | 0.500 |
| Self-Correcting | **0%** (0/3, all refused) | **0.567** |

Full breakdown — per-category behaviour, conflict-detection rate, and RAGAS faithfulness — is in [docs/EVALUATION.md](docs/EVALUATION.md).

**Hallucination rate on unanswerable questions** — the headline metric. Three test questions have *no supporting information* in the corpus (part-time-contractor maternity leave, a Q4 auditor never named, IP-violation penalties):

| Mode | Answered confidently (= hallucinated) | Hallucination rate |
|---|---|---|
| **Baseline RAG** | 3 / 3 | **100%** |
| **Self-Correcting** | 0 / 3 | **0%** |

**Behavioural comparison** over the full 10-question set:

| Mode | Confident | Conflict flagged | Low-confidence |
|---|---|---|---|
| **Baseline RAG** | 10 / 10 | 0 | 0 |
| **Self-Correcting** | 3 / 10 | 2 | 5 |

The baseline answers **everything** confidently — including the three unanswerable questions and the three conflicting-policy questions, where it silently picks one value. The self-correcting agent refuses the unanswerable ones (low-confidence) and surfaces the policy conflicts (travel-expense $500-vs-$250, remote-work 4-vs-2 office days) instead of guessing. **That gap is the product.**

Reproduce with:

```bash
python -m evaluation.run_full_eval   # server must be running on :8000
```

---

## Tech Stack

| Layer | Choice | Notes |
|---|---|---|
| Orchestration | **LangGraph** | State machine for the sufficiency/refine/conflict loop |
| LLM | **Groq — `llama-3.1-8b-instant`** | Free tier, fast, model-agnostic (`LLM_MODEL` env var swaps it) |
| Embeddings | **ChromaDB local ONNX MiniLM** | Runs offline, zero API cost, no rate limits |
| Vector store | **ChromaDB** (persistent, cosine) | |
| PDF ingestion | **pypdf** | Local text extraction |
| Evaluation | **RAGAS** | Faithfulness, Answer Relevance, Context Precision |
| API | **FastAPI** | Async, serves the built frontend as a single service |
| Frontend | **React + TypeScript + Vite** | 4-panel app: Dashboard, Ask, Documents, Evaluations |

> **Why local embeddings + Groq?** The system runs entirely on free infrastructure — no billing, no credit card, no per-token cost. Embeddings are computed on-device; only the reasoning steps call the (free) Groq API. This keeps the whole pipeline reproducible for judges without a paid key.

---

## Project Structure

```
candora/
├── api/main.py            # FastAPI app: /query, /ingest, /evaluate, /stats, serves frontend
├── agent/
│   ├── graph.py           # LangGraph wiring
│   ├── nodes.py           # retrieve / sufficiency / refine / conflict / generate
│   ├── llm_client.py      # Groq (OpenAI-compatible) wrapper
│   └── prompts.py         # Reasoning prompts
├── ingestion/
│   ├── ocr.py             # PDF (pypdf) + markdown text extraction
│   ├── metadata_extractor.py  # LLM structured metadata (title, date, version, id)
│   ├── chunker.py         # Header-aware semantic chunking
│   └── indexer.py         # ChromaDB + local embeddings
├── evaluation/
│   ├── ragas_eval.py      # RAGAS harness (Groq evaluator + local embeddings)
│   ├── run_full_eval.py   # Baseline vs self-correcting comparison runner
│   └── test_questions.py  # 10 curated questions (conflict / insufficient / sufficient)
├── models/schemas.py      # Pydantic models
├── frontend/              # React + TS + Vite SPA
├── test_data/             # Synthetic policy docs with planted conflicts
└── Dockerfile             # Single-service build (React → static, served by FastAPI)
```

---

## Running Locally

**Prerequisites:** Python 3.11, Node 20, a free [Groq API key](https://console.groq.com).

```bash
# 1. Backend
python -m venv .venv && .venv/Scripts/activate      # Windows
pip install -r requirements.txt
cp .env.example .env                                 # add your GROQ_API_KEY
uvicorn api.main:app --reload --port 8000

# 2. Frontend (dev)
cd frontend
npm install
npm run dev                                          # http://localhost:5173
```

On first launch the API auto-seeds the demo dataset (conflicting policies, a Q1 report, a noisy scan) so the app is usable immediately.

**Single-service (production) build:**

```bash
cd frontend && npm run build      # outputs frontend/dist
uvicorn api.main:app --port 8000  # FastAPI now serves the UI at /
```

---

## Deployment

Ships as a **single Docker container** — the `Dockerfile` builds the React app and serves it through FastAPI on one port, deployable to any Docker host (Render, Koyeb, Fly.io, a VM, etc.). The app binds `$PORT` and auto-seeds the demo dataset on first boot; set `GROQ_API_KEY` in the host's environment. See [docs/DEPLOY.md](docs/DEPLOY.md).

---

## Key Engineering Decisions

- **Fail-loud over fail-silent.** The conflict path *halts* rather than resolving — surfacing disagreement is more trustworthy than hiding it.
- **Every service degrades safely.** ASR/NLP/retrieval each catch their own errors and return safe fallbacks so one failure never crashes the request.
- **Real relevance, not decoration.** Citation relevance scores are computed from actual ChromaDB cosine distances, not fabricated.
- **Model-agnostic.** Swapping `LLM_MODEL` (e.g. to `llama-3.3-70b-versatile`) changes nothing else in the pipeline.
