from __future__ import annotations

import re

from ml.ingestion.schemas.canonical import (
    CanonicalDocument,
    HeadingElement,
    PictureElement,
    Provenance,
    TableElement,
    TextElement,
)
from ml.ingestion.schemas.chunk import Chunk, ChunkProvenance


DEFAULT_TARGET_WORDS = 350
DEFAULT_MAX_WORDS = 500


def _normalize_text(text: str) -> str:
    """Normalize whitespace without changing the meaning."""
    return re.sub(r"\s+", " ", text).strip()


def _word_count(text: str) -> int:
    """Return a simple word-count approximation."""
    return len(text.split())


def _split_sentences(text: str) -> list[str]:
    """Split text approximately at sentence boundaries."""
    text = _normalize_text(text)

    if not text:
        return []

    sentences = re.split(r"(?<=[.!?])\s+", text)

    return [
        sentence.strip()
        for sentence in sentences
        if sentence.strip()
    ]


def _split_oversized_text(
    text: str,
    max_words: int,
) -> list[str]:
    """
    Split oversized text.

    First preference:
        sentence boundaries

    Fallback:
        word boundaries if one sentence itself is too large.
    """

    sentences = _split_sentences(text)

    if not sentences:
        return []

    chunks: list[str] = []

    current_sentences: list[str] = []
    current_words = 0

    for sentence in sentences:

        sentence_words = _word_count(sentence)

        # ---------------------------------------------------------------
        # One sentence itself is larger than max_words.
        # ---------------------------------------------------------------

        if sentence_words > max_words:

            if current_sentences:
                chunks.append(
                    " ".join(current_sentences)
                )

                current_sentences = []
                current_words = 0

            words = sentence.split()

            for start in range(
                0,
                len(words),
                max_words,
            ):
                chunks.append(
                    " ".join(
                        words[start:start + max_words]
                    )
                )

            continue

        # ---------------------------------------------------------------
        # Sentence fits into current chunk.
        # ---------------------------------------------------------------

        if (
            current_words + sentence_words
            <= max_words
        ):
            current_sentences.append(sentence)
            current_words += sentence_words

        # ---------------------------------------------------------------
        # Adding sentence would exceed max_words.
        # ---------------------------------------------------------------

        else:

            if current_sentences:
                chunks.append(
                    " ".join(current_sentences)
                )

            current_sentences = [sentence]
            current_words = sentence_words

    if current_sentences:
        chunks.append(
            " ".join(current_sentences)
        )

    return chunks


def _provenance_to_chunk_provenance(
    provenance: Provenance | None,
) -> list[ChunkProvenance]:
    """Convert canonical provenance into chunk provenance."""

    if provenance is None:
        return []

    if provenance.page_number is None:
        return []

    return [
        ChunkProvenance(
            page_number=provenance.page_number,
            bbox=provenance.bbox,
        )
    ]


def _table_to_text(
    element: TableElement,
) -> str:
    """
    Convert a structured table into a retrieval-friendly text form.

    The canonical table remains structured.
    This is only the text representation used by the chunk.
    """

    lines: list[str] = []

    if element.headers:
        lines.append(
            " | ".join(element.headers)
        )

    for row in element.rows:
        lines.append(
            " | ".join(row)
        )

    return "\n".join(lines)


def _picture_to_text(
    element: PictureElement,
) -> str:
    """
    Convert picture information into retrieval text.

    If Docling extracted text from the picture,
    use that text.

    If not, use a small descriptive fallback.
    """

    if element.extracted_text:
        return _normalize_text(
            element.extracted_text
        )

    return "[Picture with no extracted text]"


class StructureAwareChunker:
    """
    Structure-aware adaptive chunker.

    Main strategy:

    1. Preserve document order.
    2. Headings establish section context.
    3. Normal text is accumulated.
    4. Tables remain atomic.
    5. Pictures remain atomic.
    6. Oversized text is split at sentence boundaries.
    7. Provenance is preserved.
    8. Chunk IDs are deterministic.
    """

    def __init__(
        self,
        target_words: int = DEFAULT_TARGET_WORDS,
        max_words: int = DEFAULT_MAX_WORDS,
    ) -> None:

        if target_words <= 0:
            raise ValueError(
                "target_words must be greater than 0."
            )

        if max_words <= 0:
            raise ValueError(
                "max_words must be greater than 0."
            )

        if target_words > max_words:
            raise ValueError(
                "target_words cannot be greater than max_words."
            )

        self.target_words = target_words
        self.max_words = max_words

    def chunk_document(
        self,
        document: CanonicalDocument,
    ) -> list[Chunk]:

        chunks: list[Chunk] = []

        current_section: str | None = None

        text_buffer: list[str] = []

        text_provenance: list[
            ChunkProvenance
        ] = []

        text_pages: set[int] = set()

        # ---------------------------------------------------------------
        # Flush accumulated normal text.
        # ---------------------------------------------------------------

        def flush_text_buffer() -> None:

            nonlocal text_buffer
            nonlocal text_provenance
            nonlocal text_pages

            if not text_buffer:
                return

            combined_text = _normalize_text(
                " ".join(text_buffer)
            )

            if not combined_text:
                text_buffer = []
                text_provenance = []
                text_pages = set()
                return

            pieces = _split_oversized_text(
                text=combined_text,
                max_words=self.max_words,
            )

            for piece in pieces:

                chunks.append(
                    self._create_chunk(
                        document=document,
                        text=piece,
                        element_type="text",
                        section=current_section,
                        page_numbers=sorted(
                            text_pages
                        ),
                        provenance=list(
                            text_provenance
                        ),
                    )
                )

            text_buffer = []
            text_provenance = []
            text_pages = set()

        # ---------------------------------------------------------------
        # Process document elements in order.
        # ---------------------------------------------------------------

        for element in document.elements:

            # ===========================================================
            # HEADING
            # ===========================================================

            if isinstance(
                element,
                HeadingElement,
            ):

                flush_text_buffer()

                current_section = (
                    _normalize_text(
                        element.text
                    )
                )

                continue

            # ===========================================================
            # NORMAL TEXT
            # ===========================================================

            if isinstance(
                element,
                TextElement,
            ):

                text = _normalize_text(
                    element.text
                )

                if not text:
                    continue

                text_words = _word_count(text)

                current_words = _word_count(
                    " ".join(text_buffer)
                )

                # -------------------------------------------------------
                # If this text would push the current chunk beyond
                # the target size, flush the current chunk first.
                # -------------------------------------------------------

                if (
                    text_buffer
                    and current_words + text_words
                    > self.target_words
                ):

                    flush_text_buffer()

                # -------------------------------------------------------
                # If this individual text element is already larger
                # than the hard maximum, split it directly.
                # -------------------------------------------------------

                if text_words > self.max_words:

                    flush_text_buffer()

                    pieces = _split_oversized_text(
                        text=text,
                        max_words=self.max_words,
                    )

                    provenance = (
                        _provenance_to_chunk_provenance(
                            element.provenance
                        )
                    )

                    pages = sorted(
                        {
                            p.page_number
                            for p in provenance
                        }
                    )

                    for piece in pieces:

                        chunks.append(
                            self._create_chunk(
                                document=document,
                                text=piece,
                                element_type="text",
                                section=current_section,
                                page_numbers=pages,
                                provenance=provenance,
                            )
                        )

                    continue

                # -------------------------------------------------------
                # Add normal text to buffer.
                # -------------------------------------------------------

                text_buffer.append(text)

                provenance = (
                    _provenance_to_chunk_provenance(
                        element.provenance
                    )
                )

                text_provenance.extend(
                    provenance
                )

                text_pages.update(
                    p.page_number
                    for p in provenance
                )

                continue

            # ===========================================================
            # TABLE
            # ===========================================================

            if isinstance(
                element,
                TableElement,
            ):

                flush_text_buffer()

                table_text = _table_to_text(
                    element
                )

                chunks.append(
                    self._create_chunk(
                        document=document,
                        text=table_text,
                        element_type="table",
                        section=current_section,
                        page_numbers=self._page_numbers(
                            element.provenance
                        ),
                        provenance=(
                            _provenance_to_chunk_provenance(
                                element.provenance
                            )
                        ),
                    )
                )

                continue

            # ===========================================================
            # PICTURE
            # ===========================================================

            if isinstance(
                element,
                PictureElement,
            ):

                flush_text_buffer()

                picture_text = _picture_to_text(
                    element
                )

                chunks.append(
                    self._create_chunk(
                        document=document,
                        text=picture_text,
                        element_type="picture",
                        section=current_section,
                        page_numbers=self._page_numbers(
                            element.provenance
                        ),
                        provenance=(
                            _provenance_to_chunk_provenance(
                                element.provenance
                            )
                        ),
                    )
                )

                continue

            # ===========================================================
            # UNKNOWN ELEMENT
            # ===========================================================

            flush_text_buffer()

        # ---------------------------------------------------------------
        # Flush anything remaining at the end.
        # ---------------------------------------------------------------

        flush_text_buffer()

        # ---------------------------------------------------------------
        # Assign deterministic IDs.
        # ---------------------------------------------------------------

        return self._assign_chunk_ids(
            document=document,
            chunks=chunks,
        )

    @staticmethod
    def _page_numbers(
        provenance: Provenance | None,
    ) -> list[int]:

        if provenance is None:
            return []

        if provenance.page_number is None:
            return []

        return [provenance.page_number]

    @staticmethod
    def _create_chunk(
        document: CanonicalDocument,
        text: str,
        element_type: str,
        section: str | None,
        page_numbers: list[int],
        provenance: list[ChunkProvenance],
    ) -> Chunk:

        return Chunk(
            chunk_id="",
            document_id=document.document_id,
            text=text,
            element_type=element_type,
            section=section,
            page_numbers=page_numbers,
            provenance=provenance,
            parent_id=None,
        )

    @staticmethod
    def _assign_chunk_ids(
        document: CanonicalDocument,
        chunks: list[Chunk],
    ) -> list[Chunk]:

        for index, chunk in enumerate(
            chunks,
            start=1,
        ):

            chunk.chunk_id = (
                f"{document.document_id}"
                f"-chunk-{index:04d}"
            )

        return chunks


def chunk_document(
    document: CanonicalDocument,
    target_words: int = DEFAULT_TARGET_WORDS,
    max_words: int = DEFAULT_MAX_WORDS,
) -> list[Chunk]:
    """
    Convenience function for chunking a CanonicalDocument.
    """

    chunker = StructureAwareChunker(
        target_words=target_words,
        max_words=max_words,
    )

    return chunker.chunk_document(document)