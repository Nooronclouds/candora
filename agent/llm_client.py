"""Thin LLM client wrapper around Groq's OpenAI-compatible chat completions API.

Centralizing the call here means the rest of the codebase (agent nodes,
metadata extraction) doesn't need to know which provider is behind it.
"""

import logging
from openai import OpenAI
from config import GROQ_API_KEY, GROQ_BASE_URL, LLM_MODEL

logger = logging.getLogger(__name__)

_client = OpenAI(api_key=GROQ_API_KEY, base_url=GROQ_BASE_URL)


def generate_text(prompt: str, temperature: float = 0.2, json_mode: bool = False) -> str:
    """Send a single-turn prompt to the LLM and return the text response.

    Args:
        prompt: The full prompt text (system + user context already merged).
        temperature: Sampling temperature.
        json_mode: If True, requests JSON-object output. The prompt must
            already contain the word "json" per Groq/OpenAI's requirement.

    Returns:
        The model's text response.
    """
    kwargs = {}
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    response = _client.chat.completions.create(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
        **kwargs,
    )
    return response.choices[0].message.content or ""
