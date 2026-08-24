from __future__ import annotations

import asyncio

from app.services.rag_core import answer_question


async def async_answer_query(
    session_id: int | None,
    message: str,
) -> dict:
    """
    Async adapter used by FastAPI.

    The actual RAG pipeline is synchronous, so we execute it
    in a worker thread to avoid blocking FastAPI's event loop.
    """

    if session_id is None:
        raise ValueError("session_id is required for RAG queries.")

    return await asyncio.to_thread(
        answer_question,
        message,
        session_id,
    )