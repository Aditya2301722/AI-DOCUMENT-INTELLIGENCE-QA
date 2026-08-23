from __future__ import annotations

from typing import Sequence

from FlagEmbedding import FlagReranker


class BGEReranker:
    """
    Local BGE cross-encoder reranker.

    Takes a user query and retrieved candidate chunks,
    then scores each query/chunk pair for relevance.
    """

    def __init__(
        self,
        model_name: str = "BAAI/bge-reranker-v2-m3",
        use_fp16: bool = False,
    ) -> None:
        self.model_name = model_name

        self.reranker = FlagReranker(
            model_name,
            use_fp16=use_fp16,
        )

    def rerank(
        self,
        query: str,
        candidates: Sequence[dict],
        top_k: int = 5,
    ) -> list[dict]:
        """
        Rerank retrieved candidates.

        Each candidate must contain at least:
            text

        Returns candidates ordered by reranker score.
        """

        if not candidates:
            return []

        pairs = [
            [query, candidate["text"]]
            for candidate in candidates
        ]

        scores = self.reranker.compute_score(
            pairs,
            normalize=True,
        )

        if isinstance(scores, float):
            scores = [scores]

        reranked = []

        for candidate, score in zip(candidates, scores):
            result = dict(candidate)
            result["reranker_score"] = float(score)
            reranked.append(result)

        reranked.sort(
            key=lambda item: item["reranker_score"],
            reverse=True,
        )

        return reranked[:top_k]