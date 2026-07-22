# Candora — Demo Video Script (~3 minutes)

> Target length: 2.5–3 min. Record screen + voiceover. Keep energy up, show the product doing the thing.

---

## 0:00 – 0:25 · The Problem (hook)

> "Standard RAG systems have a trust problem. When documents are messy or contradict each other, they don't tell you — they just answer confidently, even when they're wrong. If an old policy says 15 vacation days and a new addendum says 20, a normal RAG picks one at random and never mentions the conflict."

*(On screen: title card "Candora — Trust is the Metric", then the Ask page.)*

---

## 0:25 – 0:45 · The Solution (one sentence)

> "Candora is a self-correcting RAG agent. Before it answers, it checks whether it actually has enough context. If it doesn't, it refines its own search and retries. If two documents disagree, it stops and shows you both. It gives one of three honest answers instead of one confident guess."

*(On screen: briefly show the "Agent execution guide" panel on the Ask page.)*

---

## 0:45 – 1:45 · Live Demo — the three response types

**1. Confident answer (0:45–1:05)**
- Ask: *"What is the Q1 revenue and net income for 2024?"*
- Point out: the confident badge, the answer, and **expand the citations** — show real document names, sections, and the relevance scores pulled from the vector search.

> "It answers, and every claim is cited back to a source with a real relevance score."

**2. Conflict detection (1:05–1:30)**
- Ask: *"What is the threshold for travel expense pre-approval?"*
- Point out: the **Conflict Detected** state, the two sources shown side-by-side with their dates.

> "Here the v1 policy and the addendum disagree on the dollar threshold. Instead of guessing, Candora halts and shows both sources so a human decides."

**3. Low-confidence (1:30–1:45)**
- Ask: *"What is the maternity leave duration for part-time contractors?"*
- Point out: the **Low-Confidence** badge and the "what's missing" note.

> "The documents only cover full-time staff. Rather than inventing a policy, it says what it can't answer — and you can see it tried refining the query twice first, in the agent steps."

---

## 1:45 – 2:20 · The Evaluation (proof it works)

*(On screen: the Evaluations page / the RAGAS results table.)*

> "We measured this. Same ten questions, two modes. A baseline RAG answered all ten confidently — including three it had no basis for. The self-correcting agent flagged the conflict and marked the unanswerable ones as low-confidence. On RAGAS, faithfulness improved from [BASELINE] to [SELF-CORRECTING] — meaning fewer hallucinations, measurably."

*(Fill [BASELINE]/[SELF-CORRECTING] with your final numbers.)*

---

## 2:20 – 2:50 · Architecture (engineering credibility)

> "Under the hood: a LangGraph state machine drives the sufficiency-check, query-refinement, and conflict-detection loop. Reasoning runs on Groq's Llama 3.1; embeddings run locally with ChromaDB, so the whole thing is free and reproducible — no paid API. FastAPI serves both the API and the React frontend as a single container on Hugging Face Spaces."

*(On screen: the architecture diagram from the README, or the repo structure.)*

---

## 2:50 – 3:00 · Close

> "Candora — a RAG system that earns trust by refusing to guess. Thanks for watching."

*(On screen: the live URL + GitHub link.)*

---

## Recording checklist

- [ ] Backend running and seeded (all three demo questions produce their intended response type — test them once before recording)
- [ ] Browser zoom ~110% so text is legible on video
- [ ] Close other tabs / notifications
- [ ] Have the final RAGAS numbers on screen for the eval section
- [ ] Mention the live URL and GitHub repo at the end
- [ ] Export at 1080p
