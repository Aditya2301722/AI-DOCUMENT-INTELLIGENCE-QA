from docling.document_converter import DocumentConverter

pdf_path = "data/raw/documents/rag_phase2_test_document.pdf"

converter = DocumentConverter()
result = converter.convert(pdf_path)

document = result.document

print("\n=== DOCUMENT INFO ===")
print("Name:", document.name)
print("Pages:", document.num_pages)

print("\n=== TEXT ELEMENTS ===")
for i, text in enumerate(document.texts):
    print(f"\nTEXT {i}")
    print("Type:", type(text))
    print("Text:", getattr(text, "text", None))

print("\n=== TABLE ELEMENTS ===")
for i, table in enumerate(document.tables):
    print(f"\nTABLE {i}")
    print("Type:", type(table))
    print("Data:")
    print(table.export_to_dataframe())

print("\n=== PICTURE ELEMENTS ===")
for i, picture in enumerate(document.pictures):
    print(f"\nPICTURE {i}")
    print("Type:", type(picture))
    print("Picture:", picture)

print("\n=== FIRST TEXT ITEM ===")

if document.texts:
    text_item = document.texts[0]

    print("Type:", type(text_item))
    print("Text:", text_item.text)
    print("Provenance:", text_item.prov)