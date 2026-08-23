from ml.embedding.ollama_embedding import OllamaEmbeddingService
from ml.generation.prompt_builder import build_rag_prompt
from ml.retrieval.bge_reranker import BGEReranker
from ml.storage.postgres import PostgresRepository


QUESTION = "How long can damaged products be returned?"


def main() -> None:
    print("QUESTION:")
    print(QUESTION)

    # 1. Embed question
    embedding_service = OllamaEmbeddingService()

    print("\nCreating query embedding...")
    query_embedding = embedding_service.embed(QUESTION)

    # 2. Vector retrieval
    repository = PostgresRepository()

    print("Searching pgvector...")
    candidates = repository.search_similar_chunks(
        query_embedding=query_embedding,
        top_k=20,
    )

    # 3. Reranking
    print("Loading BGE reranker...")
    reranker = BGEReranker()

    print("Reranking candidates...")
    reranked = reranker.rerank(
        query=QUESTION,
        candidates=candidates,
        top_k=5,
    )

    # 4. Build final RAG prompt
    system_prompt, user_prompt = build_rag_prompt(
        question=QUESTION,
        candidates=reranked,
    )

    # 5. Display exactly what will go to the LLM
    print("\n" + "=" * 80)
    print("SYSTEM PROMPT")
    print("=" * 80)
    print(system_prompt)

    print("\n" + "=" * 80)
    print("USER PROMPT")
    print("=" * 80)
    print(user_prompt)


if __name__ == "__main__":
    main()