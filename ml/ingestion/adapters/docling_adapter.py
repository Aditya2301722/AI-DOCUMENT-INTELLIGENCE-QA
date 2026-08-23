from docling_core.types.doc import DoclingDocument

from docling_core.types.doc.items.text import (
    SectionHeaderItem,
    TextItem,
)

from docling_core.types.doc.items.table.table import (
    TableItem,
)

from docling_core.types.doc.items.picture.picture import (
    PictureItem,
)

from ml.ingestion.normalization.text_normalizer import (
    normalize_text,
    normalize_table_headers,
    normalize_table_rows,
    normalize_picture_text,
)

from ml.ingestion.schemas.canonical import (
    CanonicalDocument,
    HeadingElement,
    PictureElement,
    Provenance,
    TableElement,
    TextElement,
)


def _convert_provenance(
    provenance_items,
) -> Provenance | None:
    """
    Convert Docling provenance information into
    our canonical provenance model.
    """

    if not provenance_items:
        return None

    item = provenance_items[0]
    bbox = item.bbox

    return Provenance(
        page_number=item.page_no,
        bbox=[
            bbox.l,
            bbox.t,
            bbox.r,
            bbox.b,
        ],
    )


def _convert_text_item(
    item: TextItem,
) -> TextElement:
    """
    Convert a Docling TextItem into
    a canonical TextElement.
    """

    return TextElement(
        text=normalize_text(item.text),
        provenance=_convert_provenance(item.prov),
    )


def _convert_heading_item(
    item: SectionHeaderItem,
) -> HeadingElement:
    """
    Convert a Docling SectionHeaderItem into
    a canonical HeadingElement.
    """

    return HeadingElement(
        text=normalize_text(item.text),
        level=item.level,
        provenance=_convert_provenance(item.prov),
    )


def _convert_table_item(
    item: TableItem,
    document: DoclingDocument,
) -> TableElement:
    """
    Convert a Docling TableItem into
    a canonical TableElement.

    Table structure is preserved while
    individual cell content is normalized.
    """

    dataframe = item.export_to_dataframe(
        doc=document
    )

    headers = [
        str(column)
        for column in dataframe.columns
    ]

    rows = [
        [
            str(value)
            for value in row
        ]
        for row in dataframe.fillna("").values.tolist()
    ]

    # Normalize table content while preserving
    # row order, column order, and structure.
    headers = normalize_table_headers(headers)
    rows = normalize_table_rows(rows)

    return TableElement(
        headers=headers,
        rows=rows,
        provenance=_convert_provenance(item.prov),
    )


def _convert_picture_item(
    item: PictureItem,
    document: DoclingDocument,
) -> PictureElement:
    """
    Convert a Docling PictureItem into
    a canonical PictureElement.

    Text items whose parent is this picture
    are treated as text extracted from the visual.
    """

    extracted_text_parts = []

    for text_item in document.texts:

        if not isinstance(text_item, TextItem):
            continue

        if text_item.parent is None:
            continue

        if text_item.parent.cref != item.self_ref:
            continue

        text = normalize_picture_text(
            text_item.text
        )

        if text:
            extracted_text_parts.append(text)

    extracted_text = None

    if extracted_text_parts:
        extracted_text = " ".join(
            extracted_text_parts
        )

    return PictureElement(
        image_reference=item.self_ref,
        extracted_text=extracted_text,
        provenance=_convert_provenance(item.prov),
    )


def _convert_body_item(
    item,
    document: DoclingDocument,
):
    """
    Convert one Docling document item into
    the appropriate canonical element.
    """

    if isinstance(item, SectionHeaderItem):
        return _convert_heading_item(item)

    if isinstance(item, TextItem):
        return _convert_text_item(item)

    if isinstance(item, TableItem):
        return _convert_table_item(
            item=item,
            document=document,
        )

    if isinstance(item, PictureItem):
        return _convert_picture_item(
            item=item,
            document=document,
        )

    return None


def convert_docling_document(
    document: DoclingDocument,
    document_id: str,
    filename: str,
    mime_type: str,
) -> CanonicalDocument:
    """
    Convert a DoclingDocument into our internal
    CanonicalDocument.

    The adapter translates parser-specific structures
    into our stable internal representation.
    """

    items = list(
        document.iterate_items()
    )

    elements = []

    for item, _level in items:

        element = _convert_body_item(
            item=item,
            document=document,
        )

        if element is not None:
            elements.append(element)

    return CanonicalDocument(
        document_id=document_id,
        filename=filename,
        mime_type=mime_type,
        page_count=document.num_pages(),
        elements=elements,
    )