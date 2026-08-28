from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass
class EvaluationResult:
    matched: int
    total: int
    score: float


def evaluate_against_golden(output_text: str, golden_phrases: Iterable[str]) -> EvaluationResult:
    phrases = list(golden_phrases)
    matched = sum(1 for phrase in phrases if phrase.lower() in output_text.lower())
    total = len(phrases)
    score = matched / total if total else 0.0
    return EvaluationResult(matched=matched, total=total, score=score)
