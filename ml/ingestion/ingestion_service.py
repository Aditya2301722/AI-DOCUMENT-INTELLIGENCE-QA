from __future__ import annotations

from pathlib import Path

from docling.document_converter import DocumentConverter

from ml.embedding.ollama_embedding import OllamaEmbeddingService
from ml.ingestion.adapters.docling_adapter import (
    convert_docling_document,
)
from ml.ingestion.chunking.retrieval_text import (
    build_retrieval_text,
)
from ml.ingestion.chunking.structure_aware_chunker import (
    chunk_document,
)
from ml.storage.postgres import PostgresRepository


class DocumentIngestionService:
    """
    Orchestrates the complete PDF ingestion pipeline.

    Pipeline:

        PDF
        ↓
        Docling
        ↓
        CanonicalDocument
        ↓
        Structure-aware chunks
        ↓
        Retrieval text
        ↓
        Embeddings
        ↓
        PostgreSQL / pgvector
    """

    def __init__(self) -> None:
        self.converter = DocumentConverter()
        self.embedding_service = OllamaEmbeddingService()
        self.repository = PostgresRepository()

    def ingest(
        self,
        file_path: str | Path,
        document_id: str,
        filename: str,
        mime_type: str,
        session_id: int,
    ) -> dict:
        """
        Ingest one PDF for a specific chat session.

        The document is fully processed and verified
        before the previous document is removed.
        """

        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Document not found: {path}"
            )

        # ============================================================
        # 1. Parse PDF with Docling
        # ============================================================

        result = self.converter.convert(
            str(path)
        )

        docling_document = result.document

        # ============================================================
        # 2. Convert to canonical document
        # ============================================================

        canonical_document = convert_docling_document(
            document=docling_document,
            document_id=document_id,
            filename=filename,
            mime_type=mime_type,
        )

        # ============================================================
        # 3. Structure-aware chunking
        # ============================================================

        chunks = chunk_document(
            canonical_document
        )

        if not chunks:
            raise ValueError(
                "No chunks were produced from the document."
            )

        # ============================================================
        # 4. Build retrieval text
        # ============================================================

        retrieval_texts = [
            build_retrieval_text(chunk)
            for chunk in chunks
        ]

        # ============================================================
        # 5. Generate embeddings
        # ============================================================

        embeddings = self.embedding_service.embed_many(
            retrieval_texts
        )

        if len(embeddings) != len(chunks):
            raise RuntimeError(
                "Number of embeddings does not match "
                "number of chunks."
            )

        embedding_model = (
            self.embedding_service.model
        )

        # ============================================================
        # 6. Prepare database records
        # ============================================================

        database_chunks = []

        for chunk_index, (
            chunk,
            retrieval_text,
            embedding,
        ) in enumerate(
            zip(
                chunks,
                retrieval_texts,
                embeddings,
                strict=True,
            )
        ):
            database_chunks.append(
                {
                    "chunk_id": chunk.chunk_id,
                    "document_id": chunk.document_id,
                    "chunk_index": chunk_index,
                    "text": chunk.text,
                    "retrieval_text": retrieval_text,
                    "element_type": chunk.element_type,
                    "section": chunk.section,
                    "page_numbers": chunk.page_numbers,
                    "embedding": embedding,
                    "embedding_model": embedding_model,
                }
            )

        # ============================================================
        # 7. Store document metadata
        # ============================================================

        self.repository.insert_document(
            document_id=document_id,
            filename=filename,
            mime_type=mime_type,
            page_count=canonical_document.page_count,
            session_id=session_id,
        )

        # ============================================================
        # 8. Store chunks and embeddings
        # ============================================================

        self.repository.insert_chunks(
            database_chunks
        )

        # ============================================================
        # 9. Verify ingestion
        # ============================================================

        chunk_count = (
            self.repository.count_chunks(
                document_id
            )
        )

        if chunk_count == 0:
            self.repository.delete_document(
                document_id
            )

            raise RuntimeError(
                "Document ingestion completed without "
                "creating any database chunks."
            )

        # ============================================================
        # 10. Return result
        # ============================================================

        return {
            "document_id": document_id,
            "filename": filename,
            "mime_type": mime_type,
            "session_id": session_id,
            "page_count": canonical_document.page_count,
            "chunk_count": chunk_count,
            "embedding_model": embedding_model,
        }