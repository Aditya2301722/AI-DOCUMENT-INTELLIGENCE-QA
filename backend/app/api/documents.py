from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile

from ml.ingestion.ingestion_service import DocumentIngestionService
from ml.storage.postgres import PostgresRepository


router = APIRouter(
    prefix="/documents",
    tags=["documents"],
)


UPLOAD_DIR = (
    Path(__file__).resolve().parents[3]
    / "data"
    / "raw"
    / "documents"
)


# Temporary value for our first end-to-end test.
# We will later obtain this from the authenticated user's
# actual chat session.
TEST_SESSION_ID = 1


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
):
    """
    Upload and ingest one PDF.

    The newest successfully ingested document replaces
    the previous document for the test chat session.
    """

    # ============================================================
    # 1. Validate file
    # ============================================================

    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported.",
        )

    filename = Path(
        file.filename or "document.pdf"
    ).name

    if not filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported.",
        )

    # ============================================================
    # 2. Prepare storage
    # ============================================================

    UPLOAD_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    document_id = str(uuid4())

    temporary_filename = (
        f"{document_id}_{filename}"
    )

    file_path = UPLOAD_DIR / temporary_filename

    # ============================================================
    # 3. Save uploaded PDF
    # ============================================================

    try:
        with file_path.open("wb") as destination:
            while chunk := await file.read(1024 * 1024):
                destination.write(chunk)

    except Exception as exc:
        if file_path.exists():
            file_path.unlink()

        raise HTTPException(
            status_code=500,
            detail="Failed to save the uploaded document.",
        ) from exc

    finally:
        await file.close()

    repository = PostgresRepository()

    try:
        # ========================================================
        # 4. Find current document for this session
        # ========================================================

        with repository._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        document_id,
                        filename
                    FROM documents
                    WHERE session_id = %s
                    ORDER BY created_at DESC
                    LIMIT 1;
                    """,
                    (TEST_SESSION_ID,),
                )

                old_document = cursor.fetchone()

        # ========================================================
        # 5. Ingest NEW document
        # ========================================================

        ingestion_service = DocumentIngestionService()

        ingestion_result = ingestion_service.ingest(
            file_path=file_path,
            document_id=document_id,
            filename=filename,
            mime_type="application/pdf",
            session_id=TEST_SESSION_ID,
        )

        # ========================================================
        # 6. Verify ingestion
        # ========================================================

        chunk_count = ingestion_result["chunk_count"]

        if chunk_count <= 0:
            raise RuntimeError(
                "Document was processed but no chunks were created."
            )

        # ========================================================
        # 7. Delete previous document
        # ========================================================

        if old_document is not None:
            old_document_id = old_document[0]

            if old_document_id != document_id:
                repository.delete_document(
                    old_document_id
                )

        # ========================================================
        # 8. Delete uploaded PDF from local storage
        # ========================================================

        if file_path.exists():
            file_path.unlink()

        # ========================================================
        # 9. Return result
        # ========================================================

        return {
            "status": "success",
            "document_id": document_id,
            "filename": filename,
            "session_id": TEST_SESSION_ID,
            "page_count": ingestion_result["page_count"],
            "chunk_count": chunk_count,
            "embedding_model": ingestion_result[
                "embedding_model"
            ],
            "replaced_document": (
                old_document[1]
                if old_document is not None
                else None
            ),
        }

    except HTTPException:
        if file_path.exists():
            file_path.unlink()

        raise

    except Exception as exc:

        # Remove partially inserted NEW document.
        # ON DELETE CASCADE removes its chunks.
        try:
            repository.delete_document(
                document_id
            )
        except Exception:
            pass

        if file_path.exists():
            file_path.unlink()

        raise HTTPException(
            status_code=500,
            detail=(
                "Document ingestion failed. "
                "The previous document was kept."
            ),
        ) from exc