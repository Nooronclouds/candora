# Candora — Submission

**Track:** AI Engineer · **Problem statement:** Self-Correcting Trustworthy RAG System

---

## Short description (for the submission form)

**Candora is a self-correcting RAG system that refuses to guess.** Standard RAG pipelines answer confidently even when the retrieved context is insufficient or when documents contradict each other — silently hallucinating or averaging conflicting policies. Candora adds an agentic verification loop (built with LangGraph) that runs *before* it answers: it checks whether the retrieved context is actually sufficient, refines its own search query and retries up to twice when it isn't, and detects contradictions between sources. It then returns one of three honest, structured responses — a **confident answer** with cited sources and real relevance scores, a **low-confidence answer** that states exactly what's missing, or a **conflict-detected** response that halts and shows the contradicting sources side-by-side for a human to arbitrate.

We measured it: on questions the document set cannot answer, a baseline RAG hallucinated a confident answer **100%** of the time, while Candora refused **100%** of them (0% hallucination rate). Context-precision also improved (0.50 → 0.57 on RAGAS).

The whole system runs on **free infrastructure** — Groq (Llama 3.1) for reasoning and local on-device embeddings (ChromaDB) — with no per-token cost, and deploys as a single Docker container.

**Stack:** LangGraph · FastAPI · Groq (llama-3.1-8b-instant) · ChromaDB + local MiniLM embeddings · RAGAS · React + TypeScript.

---

## One-liner

> A trustworthy RAG agent that verifies its own context, surfaces document conflicts instead of hiding them, and proves a 100% → 0% drop in hallucinations on unanswerable questions.

---

## Submission checklist

| Item | Where |
|---|---|
| GitHub repository | *(add link after push)* |
| Working application / live link | *(add Render link after deploy — see docs/DEPLOY.md)* |
| Project description | This file + [README.md](../README.md) |
| Technical documentation | [README.md](../README.md) (architecture, stack, decisions) |
| Evaluation results (hallucination eval) | [docs/EVALUATION.md](EVALUATION.md) |
| Demo video | Script in [docs/DEMO_SCRIPT.md](DEMO_SCRIPT.md) |

---

## Key talking points for judges (offline round)

1. **The core insight:** trustworthiness in RAG is a *behavioural* property, not just an accuracy number. The win isn't "more faithful answers" — it's *knowing when not to answer.*
2. **Fail-loud conflict handling:** we surface disagreement even when one document claims precedence, because a human should decide — not the model, silently.
3. **Measured, not claimed:** the 100%→0% hallucination-rate result is reproducible via `python -m evaluation.run_full_eval`.
4. **Cost-engineered:** migrated off a rate-limited paid API to Groq + local embeddings mid-build, keeping the whole pipeline free and reproducible for judges — a real engineering decision under constraint.
5. **Model-agnostic:** one env var (`LLM_MODEL`) swaps the reasoning model; nothing else changes.
