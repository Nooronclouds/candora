"""LLM prompt templates for the self-correcting RAG agent."""

SUFFICIENCY_CHECK_PROMPT = """You are a critical information analyst. Your task is to evaluate whether the retrieved context chunks contain SUFFICIENT information to fully answer the user's question.

USER QUESTION:
{query}

RETRIEVED CONTEXT CHUNKS:
{context}

---

Analyze the context and determine ONE of three verdicts:

1. **SUFFICIENT** — The context contains all the information needed to comprehensively answer the question, from a SINGLE consistent source or multiple sources that fully agree. There are no significant gaps and no contradictions.

2. **INSUFFICIENT** — The context is missing key information needed to answer the question properly. Identify what is missing and suggest a refined search query that might retrieve the missing information.

3. **CONFLICTING** — Two or more chunks give DIFFERENT answers to the same question (e.g. different numbers, thresholds, dates, or rules for the same policy field). This is a CONFLICT even if one document claims to "take precedence," "supersede," or be "newer" — a trustworthy system SURFACES the disagreement for a human to verify rather than silently applying a precedence rule. If the retrieved chunks state two different values for the field the user asked about, you MUST return CONFLICTING.

Decision priority: if a genuine contradiction exists, prefer CONFLICTING over SUFFICIENT. Only choose SUFFICIENT when the sources agree.

Respond with a JSON object:
{{
    "status": "SUFFICIENT" | "INSUFFICIENT" | "CONFLICTING",
    "reason": "Detailed explanation of your verdict",
    "missing_info": "What specific information is missing (only for INSUFFICIENT)",
    "refined_query": "A better search query to find the missing info (only for INSUFFICIENT)",
    "conflicting_snippets": ["Exact quote from chunk A", "Exact quote from chunk B"]
}}"""


QUERY_REFINEMENT_PROMPT = """You are a search query specialist. The initial search for information failed to retrieve sufficient context.

ORIGINAL QUESTION: {query}
PREVIOUS SEARCH QUERY: {previous_query}
FAILURE REASON: {reason}
MISSING INFORMATION: {missing_info}

Generate ONE refined search query that is:
1. More specific about the missing information
2. Uses different keywords or synonyms  
3. Targets the exact gap in the retrieved context

Respond with ONLY the refined query text, nothing else."""


CONFLICT_DETECTION_PROMPT = """You are a document conflict analyst. You have identified contradictory information in the retrieved context.

USER QUESTION: {query}

CONTEXT CHUNKS:
{context}

PREVIOUSLY IDENTIFIED CONFLICTING SNIPPETS:
{conflicting_snippets}

Perform a detailed conflict analysis:

1. Identify the EXACT contradictory statements from different source documents
2. Note the source document name and effective date for each
3. Explain WHY these statements conflict
4. Identify the specific field/topic where the conflict exists

Respond with a JSON object:
{{
    "snippet_a": "Exact text of the first conflicting statement",
    "source_a": "Source document name",
    "date_a": "Effective date of source A",
    "snippet_b": "Exact text of the second conflicting statement",
    "source_b": "Source document name",  
    "date_b": "Effective date of source B",
    "explanation": "Clear explanation of the contradiction",
    "field_of_conflict": "The topic/policy area where the conflict exists"
}}"""


ANSWER_GENERATION_PROMPT = """You are a precise, trustworthy document analyst. Generate a comprehensive answer to the user's question based ONLY on the provided context.

USER QUESTION: {query}

CONTEXT CHUNKS:
{context}

Rules:
1. Answer ONLY based on the provided context. Do NOT use prior knowledge.
2. Include explicit source citations in the format [DocName, Section, Date] after each claim.
3. If the context only partially answers the question, state clearly what you CAN answer and what remains unknown.
4. Use clear, professional language.
5. Structure the answer with headings if the response is long.

Generate your answer:"""


LOW_CONFIDENCE_PROMPT = """You are a precise, trustworthy document analyst. The system was unable to retrieve fully sufficient context after multiple search attempts.

USER QUESTION: {query}

AVAILABLE CONTEXT (may be incomplete):
{context}

MISSING INFORMATION: {missing_info}
SEARCH ATTEMPTS: {retry_count}

Rules:
1. Provide whatever partial answer you CAN from the available context.
2. Clearly mark uncertain or incomplete sections with ⚠️.
3. Explicitly state what information is missing and what additional documents might be needed.
4. Include citations for any claims you DO make.
5. Do NOT guess or hallucinate information to fill gaps.

Generate your partial answer:"""
