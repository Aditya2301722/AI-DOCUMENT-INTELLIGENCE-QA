from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Sequence


@dataclass(frozen=True)
class AnswerabilityDecision:
    """
    Result of the retrieval answerability check.
    """

    answerable: bool
    top_score: float
    reason: str


class AnswerabilityChecker:
    """
    Determines whether the retrieved evidence is strong enough
    to allow the generation model to answer.

    IMPORTANT:
    The initial threshold is a heuristic. It must be calibrated
    later using an evaluation dataset.
    """

    def __init__(
        self,
        minimum_score: float = 0.50,
    ) -> None:
        self.minimum_score = minimum_score

    def check(
        self,
        candidates: Sequence[dict],
    ) -> AnswerabilityDecision:
        """
        Check whether the retrieved candidates contain
        sufficiently relevant evidence.
        """

        if not candidates:
            return AnswerabilityDecision(
                answerable=False,
                top_score=0.0,
                reason="No retrieval candidates were found.",
            )

        scores = [
            float(
                candidate.get(
                    "reranker_score",
                    candidate.get("score", 0.0),
                )
            )
            for candidate in candidates
        ]

        top_score = max(scores)

        if top_score < self.minimum_score:
            return AnswerabilityDecision(
                answerable=False,
                top_score=top_score,
                reason=(
                    "The retrieved evidence did not reach the "
                    "minimum relevance threshold."
                ),
            )

        return AnswerabilityDecision(
            answerable=True,
            top_score=top_score,
            reason="Strong relevant evidence was found.",
        )