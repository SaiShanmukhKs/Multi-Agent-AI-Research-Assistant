"""
Gemini LLM wrapper for the Multi-Agent Research Assistant.

Provides a singleton-style accessor for the Gemini model so that all
agents share the same instance and configuration.
"""

from langchain_google_genai import ChatGoogleGenerativeAI

import config


def get_llm(temperature: float | None = None, max_tokens: int | None = None) -> ChatGoogleGenerativeAI:
    """
    Return a configured Gemini Chat LLM instance.

    Args:
        temperature: Override the default temperature (0.3).
        max_tokens: Override the default max output tokens.

    Returns:
        A ChatGoogleGenerativeAI instance ready for .invoke() calls.
    """
    return ChatGoogleGenerativeAI(
        model=config.GEMINI_MODEL,
        google_api_key=config.GOOGLE_API_KEY,
        temperature=temperature if temperature is not None else config.GEMINI_TEMPERATURE,
        max_output_tokens=max_tokens or config.GEMINI_MAX_TOKENS,
        max_retries=1,
    )
