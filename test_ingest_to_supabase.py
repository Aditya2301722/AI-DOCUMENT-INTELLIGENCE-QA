from docling.document_converter import DocumentConverter

from ml.embedding.ollama_embedding import OllamaEmbeddingService
from ml.ingestion.adapters.docling_adapter import convert_docling_document
from ml.ingestion.chunking.retrieval_text import build_retrieval_text
from ml.ingestion.chunking.structure_aware_chunker import chunk_document
from ml.storage.postgres import PostgresRepository


DOCUMENT_PATH = "data/raw/documents/rag_phase2_test_document.pdf"
DOCUMENT_ID = "test-001"
FILENAME = "rag_phase2_test_document.pdf"
MIME_TYPE = "application/pdf"
EMBEDDING_MODEL = "qwen3-embedding:0.6b"


def main() -> None:
    # 1. Convert PDF with Docling
    print("1. Converting document...")

    document = (
        DocumentConverter()
        .convert(DOCUMENT_PATH)
        .document
    )

    # 2. Convert to our canonical representation
    print("2. Creating canonical document...")

    canonical = convert_docling_document(
        document,
        DOCUMENT_ID,
        FILENAME,
        MIME_TYPE,
    )

    # 3. Chunk the document
    print("3. Creating chunks...")

    chunks = chunk_document(canonical)

    print(f"   Chunks created: {len(chunks)}")

    # 4. Build retrieval text
    print("4. Building retrieval text...")

    retrieval_texts = [
        build_retrieval_text(chunk)
        for chunk in chunks
    ]

    # 5. Generate embeddings
    print("5. Generating embeddings...")

    embedding_service = OllamaEmbeddingService()

    embeddings = embedding_service.embed_many(
        retrieval_texts
    )

    print(f"   Embeddings created: {len(embeddings)}")

    # 6. Prepare document record
    document_record = {
        "document_id": canonical.document_id,
        "filename": canonical.filename,
        "mime_type": canonical.mime_type,
        "page_count": canonical.page_count,
    }

    # 7. Prepare chunk records
    chunk_records = []

    for index, (chunk, retrieval_text, embedding) in enumerate(
        zip(chunks, retrieval_texts, embeddings)
    ):
        chunk_records.append(
            {
                "chunk_id": chunk.chunk_id,
                "document_id": chunk.document_id,
                "chunk_index": index,
                "text": chunk.text,
                "retrieval_text": retrieval_text,
                "element_type": chunk.element_type,
                "section": chunk.section,
                "page_numbers": chunk.page_numbers,
                "embedding": embedding,
                "embedding_model": EMBEDDING_MODEL,
            }
        )

    # 8. Store everything in PostgreSQL
    print("6. Inserting document into Supabase...")

    repository = PostgresRepository()

    repository.insert_document(
        document_id=document_record["document_id"],
        filename=document_record["filename"],
        mime_type=document_record["mime_type"],
        page_count=document_record["page_count"],
    )

    print("7. Inserting chunks and embeddings...")

    repository.insert_chunks(chunk_records)

    # 9. Verify
    count = repository.count_chunks(DOCUMENT_ID)

    print()
    print("========================================")
    print("INGESTION COMPLETE")
    print("========================================")
    print(f"Document ID: {DOCUMENT_ID}")
    print(f"Chunks stored: {count}")
    print("Embedding model:", EMBEDDING_MODEL)
    print("Embedding dimension:", len(embeddings[0]))
    print("========================================")


if __name__ == "__main__":
    main()