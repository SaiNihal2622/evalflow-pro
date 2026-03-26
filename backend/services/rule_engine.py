"""Deterministic rule engine for response validation.

Detects hallucination patterns, contradictions, and incomplete answers
without relying on LLM evaluation.
"""

import re
import logging
from dataclasses import dataclass, field
from typing import List, Tuple

logger = logging.getLogger(__name__)


@dataclass
class RuleResult:
    """Result from the rule engine evaluation."""
    issues: List[str] = field(default_factory=list)
    rule_score: float = 1.0  # 1.0 = perfect, 0.0 = worst
    details: List[str] = field(default_factory=list)


class RuleEngine:
    """Deterministic validation rules for AI response evaluation."""

    # Hedging phrases that often indicate hallucination
    HALLUCINATION_PATTERNS = [
        r"\bas far as I (?:know|recall|remember)\b",
        r"\bI (?:think|believe|assume)\b.*\b(?:approximately|roughly|around)\b",
        r"\baccording to (?:some|various|multiple) (?:sources|studies|reports)\b",
        r"\bresearch (?:suggests|shows|indicates) that approximately \d+%\b",
        r"\bstudies have (?:found|shown) that\b(?!.*\b(?:doi|arxiv|journal|university)\b)",
        r"\bexperts (?:say|agree|believe) that\b",
        r"\bit is (?:widely|generally|commonly) (?:known|accepted|believed)\b",
        r"\bstatistics show that (?:approximately |about )?\d+",
        r"\bin (?:a |the )?(?:recent|latest|new) (?:study|survey|report)\b(?!.*\b(?:doi|arxiv|published)\b)",
    ]

    # Contradiction indicators
    CONTRADICTION_PAIRS = [
        (r"\balways\b", r"\bnever\b"),
        (r"\bincreases?\b", r"\bdecreases?\b"),
        (r"\bmore\b", r"\bless\b"),
        (r"\bhigher\b", r"\blower\b"),
        (r"\bbetter\b", r"\bworse\b"),
        (r"\byes\b", r"\bno\b"),
        (r"\btrue\b", r"\bfalse\b"),
        (r"\bcorrect\b", r"\bincorrect\b"),
        (r"\bpossible\b", r"\bimpossible\b"),
        (r"\bsafe\b", r"\bdangerous\b"),
    ]

    # Vague filler phrases
    VAGUE_PATTERNS = [
        r"\bkind of\b",
        r"\bsort of\b",
        r"\bmore or less\b",
        r"\bto some extent\b",
        r"\bin some ways?\b",
        r"\bit depends\b(?!\s+on\b)",
        r"\bthere are (?:many|several|various) (?:factors|reasons|aspects)\b",
    ]

    def evaluate(self, prompt: str, response: str) -> RuleResult:
        """Run all deterministic rules against the prompt-response pair."""
        result = RuleResult()
        penalties = []

        # Run all checks
        hallucination_penalty = self._check_hallucination_patterns(response, result)
        penalties.append(hallucination_penalty)

        contradiction_penalty = self._check_contradictions(response, result)
        penalties.append(contradiction_penalty)

        completeness_penalty = self._check_completeness(prompt, response, result)
        penalties.append(completeness_penalty)

        vagueness_penalty = self._check_vagueness(response, result)
        penalties.append(vagueness_penalty)

        repetition_penalty = self._check_repetition(response, result)
        penalties.append(repetition_penalty)

        # Calculate composite score
        total_penalty = sum(penalties)
        result.rule_score = max(0.0, min(1.0, 1.0 - total_penalty))

        return result

    def _check_hallucination_patterns(self, response: str, result: RuleResult) -> float:
        """Detect patterns commonly associated with hallucinated content."""
        matches = 0
        for pattern in self.HALLUCINATION_PATTERNS:
            found = re.findall(pattern, response, re.IGNORECASE)
            if found:
                matches += len(found)
                result.details.append(f"Hallucination pattern: '{found[0]}'")

        if matches > 0:
            result.issues.append("hallucination")
            return min(0.4, matches * 0.1)  # Cap at 0.4 penalty
        return 0.0

    def _check_contradictions(self, response: str, result: RuleResult) -> float:
        """Detect contradictory statements within the response."""
        sentences = re.split(r'[.!?]+', response)
        contradiction_count = 0

        for i, sent_a in enumerate(sentences):
            for sent_b in sentences[i + 1:]:
                for pos_pattern, neg_pattern in self.CONTRADICTION_PAIRS:
                    has_pos_a = re.search(pos_pattern, sent_a, re.IGNORECASE)
                    has_neg_b = re.search(neg_pattern, sent_b, re.IGNORECASE)
                    has_neg_a = re.search(neg_pattern, sent_a, re.IGNORECASE)
                    has_pos_b = re.search(pos_pattern, sent_b, re.IGNORECASE)

                    # Check if same topic is discussed with opposing terms
                    if (has_pos_a and has_neg_b) or (has_neg_a and has_pos_b):
                        # Check for topic overlap (shared significant words)
                        words_a = set(re.findall(r'\b\w{4,}\b', sent_a.lower()))
                        words_b = set(re.findall(r'\b\w{4,}\b', sent_b.lower()))
                        overlap = words_a & words_b
                        if len(overlap) >= 2:
                            contradiction_count += 1
                            result.details.append(
                                f"Potential contradiction between: '{sent_a.strip()[:60]}...' and '{sent_b.strip()[:60]}...'"
                            )

        if contradiction_count > 0:
            result.issues.append("contradiction")
            return min(0.3, contradiction_count * 0.15)
        return 0.0

    def _check_completeness(self, prompt: str, response: str, result: RuleResult) -> float:
        """Check if the response adequately addresses the prompt."""
        prompt_words = len(prompt.split())
        response_words = len(response.split())

        # Very short response to a substantive prompt
        if prompt_words > 20 and response_words < 15:
            result.issues.append("incomplete")
            result.details.append(f"Response ({response_words} words) too short for prompt ({prompt_words} words)")
            return 0.3

        if prompt_words > 10 and response_words < 8:
            result.issues.append("incomplete")
            result.details.append(f"Response ({response_words} words) appears incomplete")
            return 0.25

        # Check if question words in prompt are addressed
        question_words = re.findall(r'\b(?:what|why|how|when|where|which|who)\b', prompt, re.IGNORECASE)
        if len(question_words) > 2:
            # Multi-part question — check response length is proportional
            expected_min_words = len(question_words) * 15
            if response_words < expected_min_words:
                result.issues.append("incomplete")
                result.details.append(f"Multi-part question ({len(question_words)} parts) may not be fully addressed")
                return 0.15

        return 0.0

    def _check_vagueness(self, response: str, result: RuleResult) -> float:
        """Detect vague or non-committal responses."""
        matches = 0
        for pattern in self.VAGUE_PATTERNS:
            found = re.findall(pattern, response, re.IGNORECASE)
            matches += len(found)

        response_words = len(response.split())
        if response_words > 0:
            vague_ratio = matches / (response_words / 20)  # Per ~20 words
            if vague_ratio > 0.5:
                result.issues.append("vague")
                result.details.append(f"High vagueness ratio: {matches} vague phrases in {response_words} words")
                return min(0.2, matches * 0.05)

        return 0.0

    def _check_repetition(self, response: str, result: RuleResult) -> float:
        """Detect excessive repetition in the response."""
        sentences = [s.strip().lower() for s in re.split(r'[.!?]+', response) if s.strip()]
        if len(sentences) < 2:
            return 0.0

        # Check for near-duplicate sentences
        duplicates = 0
        for i, sent_a in enumerate(sentences):
            for sent_b in sentences[i + 1:]:
                if sent_a == sent_b:
                    duplicates += 1
                elif len(sent_a) > 20 and len(sent_b) > 20:
                    # Simple similarity: shared word ratio
                    words_a = set(sent_a.split())
                    words_b = set(sent_b.split())
                    if words_a and words_b:
                        similarity = len(words_a & words_b) / max(len(words_a), len(words_b))
                        if similarity > 0.8:
                            duplicates += 1

        if duplicates > 0:
            result.details.append(f"Found {duplicates} near-duplicate sentence(s)")
            return min(0.2, duplicates * 0.1)

        return 0.0


# Singleton instance
rule_engine = RuleEngine()
