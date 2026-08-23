from ml.embedding.ollama_embedding import OllamaEmbeddingService
from ml.retrieval.bge_reranker import BGEReranker
from ml.storage.postgres import PostgresRepository


QUESTION = "How long can damaged products be returned?"


def print_results(title: str, results: list[dict]) -> None:
    print()
    print("=" * 70)
    print(title)
    print("=" * 70)

    for rank, result in enumerate(results, start=1):
        print()
        print(f"--- RESULT {rank} ---")
        print(f"Chunk ID:        {result['chunk_id']}")
        print(f"Vector score:    {result['similarity']:.4f}")

        if "reranker_score" in result:
            print(f"Reranker score:  {result['reranker_score']:.4f}")

        print(f"Section:         {result['section']}")
        print(f"Element type:    {result['element_type']}")
        print(f"Pages:           {result['page_numbers']}")
        print(f"Text:            {result['text']}")


def main() -> None:
    print("QUESTION:")
    print(QUESTION)

    # ---------------------------------------------------------
    # 1. Embed the question
    # ---------------------------------------------------------

    embedding_service = OllamaEmbeddingService()

    print()
    print("Creating query embedding...")

    query_embedding = embedding_service.embed(QUESTION)

    print(f"Query embedding dimensions: {len(query_embedding)}")

    # ---------------------------------------------------------
    # 2. Retrieve candidates from pgvector
    # ---------------------------------------------------------

    repository = PostgresRepository()

    print()
    print("Searching pgvector...")

    candidates = repository.search_similar_chunks(
        query_embedding=query_embedding,
        top_k=20,
    )

    print_results(
        "BEFORE RERANKING — PGVECTOR",
        candidates,
    )

    # ---------------------------------------------------------
    # 3. Rerank candidates with BGE
    # ---------------------------------------------------------

    print()
    print("Loading BGE reranker...")

    reranker = BGEReranker()

    print("Reranking candidates...")

    reranked = reranker.rerank(
        query=QUESTION,
        candidates=candidates,
        top_k=5,
    )

    print_results(
        "AFTER RERANKING — BGE",
        reranked,
    )


if __name__ == "__main__":
    main()