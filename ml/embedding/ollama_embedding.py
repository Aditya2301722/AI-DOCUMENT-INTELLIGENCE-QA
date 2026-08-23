from __future__ import annotations

from typing import Sequence

import ollama


class OllamaEmbeddingService:
    """
    Embedding service backed by a local Ollama model.

    The rest of the application does not need to know
    how Ollama works internally.
    """

    def __init__(
        self,
        model: str = "qwen3-embedding:0.6b",
    ) -> None:
        self.model = model

    def embed(self, text: str) -> list[float]:
        """
        Convert one piece of text into an embedding vector.
        """

        if not text or not text.strip():
            raise ValueError("Cannot embed empty text.")

        response = ollama.embed(
            model=self.model,
            input=text,
        )

        embeddings = response["embeddings"]

        if not embeddings:
            raise RuntimeError("Ollama returned no embeddings.")

        return embeddings[0]

    def embed_many(
        self,
        texts: Sequence[str],
    ) -> list[list[float]]:
        """
        Convert multiple texts into embedding vectors.
        """

        if not texts:
            return []

        cleaned_texts = [
            text.strip()
            for text in texts
            if text and text.strip()
        ]

        if not cleaned_texts:
            raise ValueError("No valid texts provided.")

        response = ollama.embed(
            model=self.model,
            input=cleaned_texts,
        )

        embeddings = response["embeddings"]

        if len(embeddings) != len(cleaned_texts):
            raise RuntimeError(
                "Number of embeddings returned by Ollama "
                "does not match number of input texts."
            )

        return embeddings