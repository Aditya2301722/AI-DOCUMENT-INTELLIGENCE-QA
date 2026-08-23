from __future__ import annotations

from ml.ingestion.schemas.chunk import Chunk


def build_retrieval_text(chunk: Chunk) -> str:
    """
    Build the text that will later be sent to the embedding model.

    The original chunk.text remains unchanged.
    """

    parts: list[str] = []

    if chunk.section:
        parts.append(f"Section: {chunk.section}")

    if chunk.text:
        parts.append(chunk.text)

    return "\n\n".join(parts)