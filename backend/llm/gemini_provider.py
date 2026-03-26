"""Google Gemini LLM provider for evaluation."""

import asyncio
import logging
from typing import Dict, Any

import google.generativeai as genai

from config import settings
from llm.base import LLMProvider

logger = logging.getLogger(__name__)


class GeminiProvider(LLMProvider):
    """Google Gemini-based evaluation provider with retry logic."""

    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model_name = settings.GEMINI_MODEL
        self.max_retries = 3

    async def evaluate(self, prompt: str, response: str) -> Dict[str, Any]:
        """Evaluate using Gemini with exponential backoff retry."""
        last_error = None

        for attempt in range(self.max_retries):
            try:
                model = genai.GenerativeModel(
                    self.model_name,
                    generation_config=genai.GenerationConfig(
                        temperature=0.1,
                        max_output_tokens=1000,
                        response_mime_type="application/json",
                    ),
                )

                full_prompt = f"{self.EVALUATION_SYSTEM_PROMPT}\n\n{self._build_user_message(prompt, response)}"

                # Run sync Gemini call in executor to avoid blocking
                loop = asyncio.get_event_loop()
                gen_response = await loop.run_in_executor(
                    None,
                    lambda: model.generate_content(full_prompt),
                )

                raw_content = gen_response.text
                if not raw_content:
                    raise ValueError("Empty response from Gemini")

                return self._parse_evaluation(raw_content)

            except Exception as e:
                last_error = e
                logger.warning(f"Gemini evaluation attempt {attempt + 1}/{self.max_retries} failed: {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)

        logger.error(f"Gemini evaluation failed after {self.max_retries} attempts: {last_error}")
        return self._fallback_result(f"Gemini evaluation failed: {str(last_error)}")
