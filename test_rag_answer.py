from ml.embedding.ollama_embedding import OllamaEmbeddingService
from ml.generation.ollama_generator import OllamaGenerator
from ml.generation.prompt_builder import build_rag_prompt
from ml.retrieval.answerability import AnswerabilityChecker
from ml.retrieval.bge_reranker import BGEReranker
from ml.storage.postgres import PostgresRepository


QUESTION = "What is the CEO's annual salary?"


def main() -> None:
    print("=" * 80)
    print("PRODUCTION RAG — END-TO-END TEST")
    print("=" * 80)

    # ---------------------------------------------------------
    # 1. Create query embedding
    # ---------------------------------------------------------

    print("\n[1/6] Creating query embedding...")

    embedding_service = OllamaEmbeddingService()

    query_embedding = embedding_service.embed(QUESTION)

    print(
        f"Query embedding dimensions: {len(query_embedding)}"
    )

    # ---------------------------------------------------------
    # 2. Retrieve candidates
    # ---------------------------------------------------------

    print("\n[2/6] Searching pgvector...")

    repository = PostgresRepository()

    candidates = repository.search_similar_chunks(
        query_embedding=query_embedding,
        top_k=20,
    )

    print(
        f"Candidates retrieved: {len(candidates)}"
    )

    # ---------------------------------------------------------
    # 3. Rerank candidates
    # ---------------------------------------------------------

    print("\n[3/6] Reranking with BGE...")

    reranker = BGEReranker()

    reranked = reranker.rerank(
        query=QUESTION,
        candidates=candidates,
        top_k=5,
    )

    print(
        f"Candidates after reranking: {len(reranked)}"
    )

    # ---------------------------------------------------------
    # 4. Check answerability
    # ---------------------------------------------------------

    print("\n[4/6] Checking answerability...")

    answerability_checker = AnswerabilityChecker(
        minimum_score=0.50,
    )

    decision = answerability_checker.check(reranked)

    print(
        f"Top reranker score: {decision.top_score:.4f}"
    )

    print(
        f"Answerable: {decision.answerable}"
    )

    print(
        f"Reason: {decision.reason}"
    )

    # ---------------------------------------------------------
    # 5. Abstain if evidence is insufficient
    # ---------------------------------------------------------

    if not decision.answerable:
        print()
        print("=" * 80)
        print("FINAL ANSWER")
        print("=" * 80)
        print()
        print(
            "I don't have enough information in the provided "
            "documents to answer this question."
        )
        print()
        print("=" * 80)
        return

    # ---------------------------------------------------------
    # 6. Build prompt and generate answer
    # ---------------------------------------------------------

    print("\n[5/6] Building grounded prompt...")

    system_prompt, user_prompt = build_rag_prompt(
        question=QUESTION,
        candidates=reranked,
    )

    print("\n[6/6] Generating answer with Qwen3:8b...")

    generator = OllamaGenerator(
        model="qwen3:8b",
    )

    answer = generator.generate(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
    )

    # ---------------------------------------------------------
    # Final answer
    # ---------------------------------------------------------

    print()
    print("=" * 80)
    print("FINAL ANSWER")
    print("=" * 80)
    print()
    print(answer)
    print()
    print("=" * 80)


if __name__ == "__main__":
    main()