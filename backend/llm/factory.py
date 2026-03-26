"""Factory for creating LLM provider instances."""

import logging

from llm.base import LLMProvider

logger = logging.getLogger(__name__)


def get_provider(provider_name: str = None) -> LLMProvider:
    """Create and return an LLM provider by name.

    Args:
        provider_name: "openai" or "gemini". Defaults to config setting.

    Returns:
        LLMProvider instance
    """
    if provider_name is None:
        from config import settings
        provider_name = settings.LLM_PROVIDER

    provider_name = provider_name.lower().strip()

    if provider_name == "openai":
        from llm.openai_provider import OpenAIProvider
        return OpenAIProvider()
    elif provider_name == "gemini":
        from llm.gemini_provider import GeminiProvider
        return GeminiProvider()
    elif provider_name == "openrouter":
        from llm.openrouter_provider import OpenRouterProvider
        return OpenRouterProvider()
    else:
        raise ValueError(f"Unknown LLM provider: {provider_name}. Supported: 'openai', 'gemini', 'openrouter'")
