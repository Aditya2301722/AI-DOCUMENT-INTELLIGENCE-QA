from __future__ import annotations

import os
from collections.abc import Sequence

import psycopg
from dotenv import load_dotenv


load_dotenv()


class PostgresRepository:
    """
    PostgreSQL repository for the RAG pipeline.

    Responsible only for storing and retrieving
    documents, chunks, and embeddings.
    """

    def __init__(self, database_url: str | None = None) -> None:
        self.database_url = database_url or os.getenv("DATABASE_URL")

        if not self.database_url:
            raise RuntimeError("DATABASE_URL is not set.")

    def _connect(self) -> psycopg.Connection:
        """Create a new PostgreSQL connection."""
        return psycopg.connect(self.database_url)

    def insert_document(
        self,
        document_id: str,
        filename: str,
        mime_type: str,
        page_count: int | None,
    ) -> None:
        """Insert one document."""

        query = """
            INSERT INTO documents (
                document_id,
                filename,
                mime_type,
                page_count
            )
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (document_id)
            DO UPDATE SET
                filename = EXCLUDED.filename,
                mime_type = EXCLUDED.mime_type,
                page_count = EXCLUDED.page_count;
        """

        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    query,
                    (
                        document_id,
                        filename,
                        mime_type,
                        page_count,
                    ),
                )

            connection.commit()

    def insert_chunks(
        self,
        chunks: Sequence[dict],
    ) -> None:
        """
        Insert multiple chunks and their embeddings.

        Each chunk dictionary must contain:

            chunk_id
            document_id
            chunk_index
            text
            retrieval_text
            element_type
            section
            page_numbers
            embedding
            embedding_model
        """

        query = """
            INSERT INTO chunks (
                chunk_id,
                document_id,
                chunk_index,
                text,
                retrieval_text,
                element_type,
                section,
                page_numbers,
                embedding,
                embedding_model
            )
            VALUES (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s::vector,
                %s
            )
            ON CONFLICT (chunk_id)
            DO UPDATE SET
                document_id = EXCLUDED.document_id,
                chunk_index = EXCLUDED.chunk_index,
                text = EXCLUDED.text,
                retrieval_text = EXCLUDED.retrieval_text,
                element_type = EXCLUDED.element_type,
                section = EXCLUDED.section,
                page_numbers = EXCLUDED.page_numbers,
                embedding = EXCLUDED.embedding,
                embedding_model = EXCLUDED.embedding_model;
        """

        rows = []

        for chunk in chunks:
            embedding = chunk["embedding"]

            embedding_string = (
                "[" + ",".join(str(value) for value in embedding) + "]"
            )

            rows.append(
                (
                    chunk["chunk_id"],
                    chunk["document_id"],
                    chunk["chunk_index"],
                    chunk["text"],
                    chunk["retrieval_text"],
                    chunk["element_type"],
                    chunk.get("section"),
                    chunk.get("page_numbers"),
                    embedding_string,
                    chunk["embedding_model"],
                )
            )

        if not rows:
            return

        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.executemany(query, rows)

            connection.commit()

    def count_chunks(self, document_id: str) -> int:
        """Return the number of chunks belonging to a document."""

        query = """
            SELECT COUNT(*)
            FROM chunks
            WHERE document_id = %s;
        """

        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (document_id,))
                result = cursor.fetchone()

        return int(result[0])

    def search_similar_chunks(
        self,
        query_embedding: Sequence[float],
        top_k: int = 20,
    ) -> list[dict]:
        """
        Search chunks using cosine distance.

        The documents table is joined so that retrieval results
        include the original filename for source attribution.
        """

        query = """
            SELECT
                c.chunk_id,
                c.document_id,
                d.filename,
                c.text,
                c.retrieval_text,
                c.element_type,
                c.section,
                c.page_numbers,
                c.embedding_model,
                1 - (c.embedding <=> %s::vector) AS similarity
            FROM chunks AS c
            INNER JOIN documents AS d
                ON c.document_id = d.document_id
            ORDER BY c.embedding <=> %s::vector
            LIMIT %s;
        """

        embedding_string = (
            "[" + ",".join(str(value) for value in query_embedding) + "]"
        )

        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    query,
                    (
                        embedding_string,
                        embedding_string,
                        top_k,
                    ),
                )

                rows = cursor.fetchall()

        return [
            {
                "chunk_id": row[0],
                "document_id": row[1],
                "filename": row[2],
                "text": row[3],
                "retrieval_text": row[4],
                "element_type": row[5],
                "section": row[6],
                "page_numbers": row[7],
                "embedding_model": row[8],
                "similarity": float(row[9]),
            }
            for row in rows
        ]

    def delete_document(
        self,
        document_id: str,
    ) -> None:
        """Delete a document and its chunks."""

        query = """
            DELETE FROM documents
            WHERE document_id = %s;
        """

        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (document_id,))

            connection.commit()