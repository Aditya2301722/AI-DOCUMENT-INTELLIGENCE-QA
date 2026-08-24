from __future__ import annotations

from ml.embedding.ollama_embedding import OllamaEmbeddingService
from ml.generation.ollama_generator import OllamaGenerator
from ml.generation.prompt_builder import build_rag_prompt
from ml.retrieval.answerability import AnswerabilityChecker
from ml.retrieval.bge_reranker import BGEReranker
from ml.storage.postgres import PostgresRepository


def retrieve_and_rerank(
    question: str,
    session_id: int,
) -> list[dict]:
    """
    Retrieve relevant chunks for the current chat session
    and rerank them with BGE.
    """

    embedding_service = OllamaEmbeddingService()
    repository = PostgresRepository()
    reranker = BGEReranker()

    query_embedding = embedding_service.embed(question)

    candidates = repository.search_similar_chunks(
        query_embedding=query_embedding,
        session_id=session_id,
        top_k=20,
    )

    reranked = reranker.rerank(
        query=question,
        candidates=candidates,
        top_k=5,
    )

    return reranked


def check_answerability(
    candidates: list[dict],
) -> dict:
    """
    Determine whether the retrieved evidence is strong enough
    to answer the user's question.
    """

    checker = AnswerabilityChecker(
        minimum_score=0.50,
    )

    decision = checker.check(candidates)

    return {
        "answerable": decision.answerable,
        "top_score": decision.top_score,
        "reason": decision.reason,
    }


def answer_question(
    question: str,
    session_id: int,
) -> dict:
    """
    Execute the complete RAG pipeline for one question
    within a specific chat session.
    """

    # ---------------------------------------------------------
    # 1. Retrieve and rerank evidence
    # ---------------------------------------------------------

    candidates = retrieve_and_rerank(
        question=question,
        session_id=session_id,
    )

    # ---------------------------------------------------------
    # 2. Check whether the evidence is sufficient
    # ---------------------------------------------------------

    answerability = check_answerability(candidates)

    if not answerability["answerable"]:
        return {
            "answer": (
                "I don't have enough information in the provided "
                "documents to answer this question."
            ),
            "sources": [],
            "answerable": False,
            "retrieval_score": answerability["top_score"],
        }

    # ---------------------------------------------------------
    # 3. Build grounded prompt
    # ---------------------------------------------------------

    system_prompt, user_prompt = build_rag_prompt(
        question=question,
        candidates=candidates,
    )

    # ---------------------------------------------------------
    # 4. Generate answer
    # ---------------------------------------------------------

    generator = OllamaGenerator(
        model="qwen3:8b",
    )

    answer = generator.generate(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
    )

    # ---------------------------------------------------------
    # 5. Return answer and source metadata
    # ---------------------------------------------------------

    sources = []

    for candidate in candidates:
        sources.append(
            {
                "chunk_id": candidate["chunk_id"],
                "document_id": candidate["document_id"],
                "filename": candidate.get("filename"),
                "page_numbers": candidate.get("page_numbers"),
                "section": candidate.get("section"),
                "element_type": candidate.get("element_type"),
                "reranker_score": candidate.get("reranker_score"),
            }
        )

    return {
        "answer": answer,
        "sources": sources,
        "answerable": True,
        "retrieval_score": answerability["top_score"],
    }