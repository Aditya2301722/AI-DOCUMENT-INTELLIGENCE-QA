from ml.embedding.ollama_embedding import OllamaEmbeddingService
from ml.retrieval.answerability import AnswerabilityChecker
from ml.retrieval.bge_reranker import BGEReranker
from ml.storage.postgres import PostgresRepository


QUESTIONS = [
    "How long can damaged products be returned?",
    "What is the CEO's annual salary?",
]


def retrieve_and_rerank(question: str) -> list[dict]:
    embedding_service = OllamaEmbeddingService()
    repository = PostgresRepository()
    reranker = BGEReranker()

    query_embedding = embedding_service.embed(question)

    candidates = repository.search_similar_chunks(
        query_embedding=query_embedding,
        top_k=20,
    )

    return reranker.rerank(
        query=question,
        candidates=candidates,
        top_k=5,
    )


def main() -> None:
    checker = AnswerabilityChecker(
        minimum_score=0.50,
    )

    for question in QUESTIONS:
        print()
        print("=" * 80)
        print(f"QUESTION: {question}")
        print("=" * 80)

        candidates = retrieve_and_rerank(question)

        decision = checker.check(candidates)

        print()
        print(f"Top reranker score: {decision.top_score:.4f}")
        print(f"Answerable:         {decision.answerable}")
        print(f"Reason:             {decision.reason}")

        print()
        print("RERANKED RESULTS:")

        for rank, candidate in enumerate(candidates, start=1):
            print(
                f"{rank}. "
                f"{candidate['chunk_id']} "
                f"→ {candidate['reranker_score']:.4f}"
            )


if __name__ == "__main__":
    main()