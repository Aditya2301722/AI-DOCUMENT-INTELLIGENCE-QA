from pydantic import BaseModel


class Provenance(BaseModel):
    page_number: int | None = None
    bbox: list[float] | None = None

class TextElement(BaseModel):
    text: str
    provenance: Provenance | None = None

class HeadingElement(BaseModel):
    text: str
    level: int | None = None
    provenance: Provenance | None = None

class TableElement(BaseModel):
    headers: list[str]
    rows: list[list[str]]
    provenance: Provenance | None = None

class PictureElement(BaseModel):
    image_reference: str | None = None
    extracted_text: str | None = None
    provenance: Provenance | None = None

class CanonicalDocument(BaseModel):
    document_id: str
    filename: str
    mime_type: str
    page_count: int | None = None
    elements: list[
        TextElement
        | HeadingElement
        | TableElement
        | PictureElement
    ]