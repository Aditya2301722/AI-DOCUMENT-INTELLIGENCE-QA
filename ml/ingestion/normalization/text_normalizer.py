import re
import unicodedata


def normalize_text(text: str) -> str:
    """
    Safely normalize extracted text.

    Performs deterministic, meaning-preserving cleanup:
    - Unicode normalization
    - whitespace normalization
    - leading/trailing whitespace removal
    """

    if not text:
        return ""

    # Normalize Unicode representation.
    text = unicodedata.normalize("NFC", text)

    # Replace consecutive whitespace characters
    # with a single space.
    text = re.sub(r"\s+", " ", text)

    # Remove leading and trailing whitespace.
    text = text.strip()

    return text


def normalize_table_cell(value) -> str:
    """
    Normalize the content of one table cell.

    The table structure itself is not changed.
    """

    if value is None:
        return ""

    return normalize_text(str(value))


def normalize_table_headers(headers: list) -> list[str]:
    """
    Normalize table headers while preserving
    their original order and number.
    """

    return [
        normalize_table_cell(header)
        for header in headers
    ]


def normalize_table_rows(rows: list) -> list[list[str]]:
    """
    Normalize table cells while preserving:
    - row order
    - column order
    - number of rows
    - number of columns
    """

    return [
        [
            normalize_table_cell(cell)
            for cell in row
        ]
        for row in rows
    ]


def normalize_picture_text(text: str | None) -> str | None:
    """
    Normalize text extracted from pictures,
    diagrams, charts, or OCR.

    This performs only safe formatting cleanup.
    It does NOT attempt semantic correction.
    """

    if not text:
        return None

    normalized = normalize_text(text)

    return normalized if normalized else None