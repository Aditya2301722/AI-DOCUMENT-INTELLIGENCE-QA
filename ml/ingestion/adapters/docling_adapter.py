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
    Convert a Docling TextItem into a canonical TextElement.
    """

    return TextElement(
        text=item.text,
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
        text=item.text,
        level=item.level,
        provenance=_convert_provenance(item.prov),
    )


def _convert_table_item(
    item: TableItem,
    document: DoclingDocument,
) -> TableElement:
    """
    Convert a Docling TableItem into a canonical TableElement.
    """

    dataframe = item.export_to_dataframe(doc=document)

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

    return TableElement(
        headers=headers,
        rows=rows,
        provenance=_convert_provenance(item.prov),
    )


def _convert_picture_item(
    item: PictureItem,
    item_lookup: dict[str, object],
) -> PictureElement:
    """
    Convert a Docling PictureItem into a canonical
    PictureElement.

    Picture child references are resolved using
    a lookup created from Docling's iterate_items().
    """

    extracted_text_parts = []

    for child in item.children:
        child_item = item_lookup.get(child.cref)

        if isinstance(child_item, TextItem):
            text = child_item.text.strip()

            if text:
                extracted_text_parts.append(text)

    extracted_text = None

    if extracted_text_parts:
        extracted_text = " ".join(extracted_text_parts)

    return PictureElement(
        image_reference=item.self_ref,
        extracted_text=extracted_text,
        provenance=_convert_provenance(item.prov),
    )


def _convert_body_item(
    item,
    document: DoclingDocument,
    item_lookup: dict[str, object],
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
            item_lookup=item_lookup,
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

    items = list(document.iterate_items())

    item_lookup = {
        item.self_ref: item
        for item, _level in items
    }

    elements = []

    for item, _level in items:
        element = _convert_body_item(
            item=item,
            document=document,
            item_lookup=item_lookup,
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