from pydantic import BaseModel, Field


class ChunkProvenance(BaseModel):
    """
    Location information for a chunk.

    A chunk can contain content from more than one
    source element, so we keep a list of provenance
    records.
    """

    page_number: int
    bbox: list[float] | None = None


class Chunk(BaseModel):
    """
    Canonical representation of a retrieval chunk.

    This object is created after document parsing,
    canonicalization, and chunking.

    It does not contain embeddings or vector database
    information.
    """

    chunk_id: str = Field(
        description="Unique identifier for this chunk."
    )

    document_id: str = Field(
        description="Identifier of the source document."
    )

    text: str = Field(
        description="Text representation used for retrieval."
    )

    element_type: str = Field(
        description=(
            "Primary content type represented by the chunk, "
            "for example text, table, or picture."
        )
    )

    section: str | None = Field(
        default=None,
        description="Current document section or heading."
    )

    page_numbers: list[int] = Field(
        default_factory=list,
        description="Pages containing content from this chunk."
    )

    provenance: list[ChunkProvenance] = Field(
        default_factory=list,
        description="Source locations contributing to this chunk."
    )

    parent_id: str | None = Field(
        default=None,
        description=(
            "Optional parent chunk identifier for future "
            "parent-child retrieval."
        )
    )
    