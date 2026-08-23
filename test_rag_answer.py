from ml.embedding.ollama_embedding import OllamaEmbeddingService
from ml.generation.ollama_generator import OllamaGenerator
from ml.generation.prompt_builder import build_rag_prompt
from ml.retrieval.bge_reranker import BGEReranker
from ml.storage.postgres import PostgresRepository


QUESTION = "How long can damaged products be returned?"


def main() -> None:
    print("=" * 80)
    print("PRODUCTION RAG — END-TO-END TEST")
    print("=" * 80)

    # ---------------------------------------------------------
    # 1. Embed the user question
    # ---------------------------------------------------------

    print("\n[1/5] Creating query embedding...")

    embedding_service = OllamaEmbeddingService()

    query_embedding = embedding_service.embed(QUESTION)

    print(
        f"Query embedding dimensions: {len(query_embedding)}"
    )

    # ---------------------------------------------------------
    # 2. Retrieve candidates from PostgreSQL + pgvector
    # ---------------------------------------------------------

    print("\n[2/5] Searching pgvector...")

    repository = PostgresRepository()

    candidates = repository.search_similar_chunks(
        query_embedding=query_embedding,
        top_k=20,
    )

    print(f"Candidates retrieved: {len(candidates)}")

    # ---------------------------------------------------------
    # 3. Rerank candidates
    # ---------------------------------------------------------

    print("\n[3/5] Reranking with BGE...")

    reranker = BGEReranker()

    reranked = reranker.rerank(
        query=QUESTION,
        candidates=candidates,
        top_k=5,
    )

    print(f"Candidates after reranking: {len(reranked)}")

    # ---------------------------------------------------------
    # 4. Build grounded prompt
    # ---------------------------------------------------------

    print("\n[4/5] Building grounded prompt...")

    system_prompt, user_prompt = build_rag_prompt(
        question=QUESTION,
        candidates=reranked,
    )

    # ---------------------------------------------------------
    # 5. Generate answer with Qwen3:8b
    # ---------------------------------------------------------

    print("\n[5/5] Generating answer with Qwen3:8b...")

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