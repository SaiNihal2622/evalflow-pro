"""OpenAI LLM provider for evaluation."""

import asyncio
import logging
from typing import Dict, Any

from openai import AsyncOpenAI

from config import settings
from llm.base import LLMProvider

logger = logging.getLogger(__name__)


class OpenAIProvider(LLMProvider):
    """OpenAI-based evaluation provider with retry logic."""

    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
        self.max_retries = 3

    async def evaluate(self, prompt: str, response: str) -> Dict[str, Any]:
        """Evaluate using OpenAI with exponential backoff retry."""
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
                    response_format={"type": "json_object"},
                )

                raw_content = completion.choices[0].message.content
                if not raw_content:
                    raise ValueError("Empty response from OpenAI")

                return self._parse_evaluation(raw_content)

            except Exception as e:
                last_error = e
                logger.warning(f"OpenAI evaluation attempt {attempt + 1}/{self.max_retries} failed: {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff

        logger.error(f"OpenAI evaluation failed after {self.max_retries} attempts: {last_error}")
        return self._fallback_result(f"OpenAI evaluation failed: {str(last_error)}")
