"""Abstract base class for LLM evaluation providers."""

from abc import ABC, abstractmethod
from typing import Dict, Any


class LLMProvider(ABC):
    """Base class for LLM evaluation providers."""

    EVALUATION_SYSTEM_PROMPT = """You are a STRICT AI evaluation judge. Your ONLY job is to determine if an AI response is factually correct.

CRITICAL RULES:
1. CHECK EVERY FACTUAL CLAIM. If the response says "X is Y", verify that claim. For example:
   - "The capital of France is Paris" → CORRECT
   - "The capital of France is Dubai" → INCORRECT (hallucination)
   - "Einstein invented the internet" → INCORRECT (hallucination)
2. If ANY factual claim is wrong, accuracy MUST be "incorrect"
3. If the response contains made-up statistics, fake percentages, or invented studies, that is a "hallucination"
4. If the response contradicts itself, that is a "contradiction"
5. If the response barely answers the question, that is "incomplete"
6. If the response uses filler words like "kind of", "sort of", "it depends" without substance, that is "vague"
7. NEVER use "unknown" for accuracy. You MUST decide: "correct" or "incorrect"
8. Be STRICT. When in doubt, mark as "incorrect"

Respond with ONLY this JSON (no other text):
{
    "accuracy": "correct" or "incorrect",
    "issues": ["hallucination", "incomplete", "contradiction", "vague", "irrelevant", "off-topic"],
    "confidence": 0.0 to 1.0,
    "severity": "low" or "medium" or "high",
    "reasoning": "One sentence explaining your judgment"
}

Only include applicable issues in the array. Empty array = perfect response.
"""

    @abstractmethod
    async def evaluate(self, prompt: str, response: str) -> Dict[str, Any]:
        """Evaluate a response against a prompt.

        Returns:
            Dict with keys: accuracy, issues, confidence, severity, reasoning
        """
        pass

    def _build_user_message(self, prompt: str, response: str) -> str:
        return f"""Evaluate the following AI response:

PROMPT: {prompt}

RESPONSE: {response}

Provide your evaluation as a JSON object."""

    def _parse_evaluation(self, raw_text: str) -> Dict[str, Any]:
        """Parse and validate the LLM evaluation response."""
        import json

        # Strip markdown code blocks if present
        text = raw_text.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            lines = lines[1:]  # Remove opening ```json
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]  # Remove closing ```
            text = "\n".join(lines)

        try:
            result = json.loads(text)
        except json.JSONDecodeError:
            # Fallback: try to extract JSON from the text
            import re
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
            else:
                return self._fallback_result("Failed to parse LLM response as JSON")

        return self._validate_result(result)

    def _validate_result(self, result: dict) -> Dict[str, Any]:
        """Validate and normalize the evaluation result."""
        validated = {}

        # accuracy
        accuracy = result.get("accuracy", "unknown")
        validated["accuracy"] = accuracy if accuracy in ("correct", "incorrect") else "unknown"

        # issues
        issues = result.get("issues", [])
        valid_issues = {"hallucination", "irrelevant", "incomplete", "contradiction", "vague", "off-topic"}
        validated["issues"] = [i for i in issues if isinstance(i, str) and i.lower() in valid_issues] if isinstance(issues, list) else []

        # confidence
        try:
            confidence = float(result.get("confidence", 0.5))
            validated["confidence"] = max(0.0, min(1.0, confidence))
        except (TypeError, ValueError):
            validated["confidence"] = 0.5

        # severity
        severity = result.get("severity", "medium")
        validated["severity"] = severity if severity in ("low", "medium", "high") else "medium"

        # reasoning
        validated["reasoning"] = result.get("reasoning", "No reasoning provided")

        return validated

    def _fallback_result(self, reason: str = "LLM evaluation failed") -> Dict[str, Any]:
        """Return a safe fallback result when evaluation fails."""
        return {
            "accuracy": "unknown",
            "issues": ["evaluation_error"],
            "confidence": 0.0,
            "severity": "high",
            "reasoning": reason,
        }
