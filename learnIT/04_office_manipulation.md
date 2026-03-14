# Office Document Manipulation

## 1. Concept: What is it?
Modern Microsoft Office files (`.docx`, `.xlsx`, `.pptx`) are actually renamed ZIP archives containing formatted XML files. Like images, they contain "Core Properties" (metadata like Author, Title, Subject, Last Modified By).
These fields can be manipulated to spoof authorship, hide small staging payloads, or conduct phishing campaigns by altering template references.

## 2. Implementation: How does it work?
In `office_handler.py`, the `OfficeHandler` leverages the `python-docx`, `openpyxl`, and `python-pptx` libraries to interface natively with the Office Open XML standard.

Instead of writing raw XML, it cleanly accesses the `core_properties` attribute of the document object.
1. Determine the document format.
2. Load it with the appropriate engine.
3. Overwrite the chosen property (e.g., `doc.core_properties.author = "Spoofed Admin"`).
4. Save the package.

This guarantees the resulting document remains entirely valid and won't trigger MS Word repair errors, which often happen when manually packing ZIP/XML structures.

## 3. Usage
**CLI Command:**
```bash
# View metadata
python3 hider.py office invoice.docx --mode view

# Spoof an Author or hide data in the Subject line
python3 hider.py office invoice.docx --mode edit --key Author --value "IT Administrator"
python3 hider.py office invoice.docx --mode edit --key Subject --value "powershell -c calc"
```
