"""OpenRouter LLM provider for evaluation.

OpenRouter provides a unified API to access multiple LLM models.
Uses OpenAI-compatible API format with a different base URL.
"""

import asyncio
import logging
from typing import Dict, Any

from openai import AsyncOpenAI

from config import settings
from llm.base import LLMProvider

logger = logging.getLogger(__name__)


class OpenRouterProvider(LLMProvider):
    """OpenRouter-based evaluation provider with retry logic."""

    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.OPENROUTER_API_KEY,
            base_url="https://openrouter.ai/api/v1",
        )
        self.model = settings.OPENROUTER_MODEL
        self.max_retries = 3

    async def evaluate(self, prompt: str, response: str) -> Dict[str, Any]:
        """Evaluate using OpenRouter with exponential backoff retry."""
        last_error = None

        for attempt in range(self.max_retries):
            try:
                completion = await self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": self.EVALUATION_SYSTEM_PROMPT},
                        {"role": "user", "content": self._build_user_message(prompt, response)},
                    ],
                    temperature=0.1,
                    max_tokens=1000,
                )

                raw_content = completion.choices[0].message.content
                if not raw_content:
                    raise ValueError("Empty response from OpenRouter")

                return self._parse_evaluation(raw_content)

            except Exception as e:
                last_error = e
                logger.warning(f"OpenRouter evaluation attempt {attempt + 1}/{self.max_retries} failed: {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)

        logger.error(f"OpenRouter evaluation failed after {self.max_retries} attempts: {last_error}")
        return self._fallback_result(f"OpenRouter evaluation failed: {str(last_error)}")
