"""Abstract base class for LLM evaluation providers."""

from abc import ABC, abstractmethod
from typing import Dict, Any


class LLMProvider(ABC):
    """Base class for LLM evaluation providers."""

    EVALUATION_SYSTEM_PROMPT = """You are a strict AI evaluation system. Your job is to evaluate an AI model's response to a given prompt.

You MUST respond with ONLY a valid JSON object with these exact fields:
{
    "accuracy": "correct" or "incorrect",
    "issues": ["list of issues found, e.g. hallucination, irrelevant, incomplete, contradiction, vague, off-topic"],
    "confidence": 0.0 to 1.0 (your confidence in the evaluation),
    "severity": "low" or "medium" or "high",
    "reasoning": "Brief explanation of your evaluation"
}

Evaluation criteria:
1. FACTUAL CORRECTNESS: Is the response factually accurate? Does it contain made-up information?
2. RELEVANCE: Does the response directly address the prompt?
3. COMPLETENESS: Does the response fully answer all aspects of the prompt?
4. REASONING QUALITY: Is the logic sound? Are there contradictions?

Issue types to detect:
- "hallucination": Response contains fabricated facts, made-up statistics, or invented references
- "irrelevant": Response does not address the prompt
- "incomplete": Response misses key aspects of the prompt
- "contradiction": Response contains self-contradictory statements
- "vague": Response is too vague or generic to be useful
- "off-topic": Response discusses unrelated topics

Rules:
- Be strict. If unsure, lean toward "incorrect"
- An empty issues array means the response is perfect
- Confidence should reflect YOUR certainty in the evaluation, not the quality of the response
- NEVER include any text outside the JSON object
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
