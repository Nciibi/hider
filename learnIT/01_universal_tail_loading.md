# Universal Tail Loading

## 1. Concept: What is it?
"Tail loading" is a crude but highly effective universal steganography technique. It relies on the fact that most file format parsers (like PDF readers, Image viewers, or Video players) stop reading a file once they hit a specific "End of File" marker (e.g., `%%EOF` in PDF, `FF D9` in JPEG). 

Any arbitrary data appended *after* this marker is completely ignored by the legitimate application, but remains retrievable by someone who knows it's there.

## 2. Implementation: How does it work?
In `universal_engine.py`, the `UniversalEngine.hide_data` method implements this. 
1. It reads the target cover file.
2. It optionally encrypts the secret payload using `EncryptionEngine`.
3. It appends a unique signature (a 16-byte random separator) to the end of the legitimate file.
4. It appends the payload after the separator.
5. To extract, it reads the file backwards to find the signature, slicing off the payload.

```python
# Pseudo-code implementation
with open(cover_file, 'rb') as f:
    original_data = f.read()

separator = os.urandom(16)
stego_content = original_data + separator + secret_payload + separator
```

## 3. Usage
**CLI Command:**
```bash
# Hide data in any file format
python3 hider.py universal secret.pdf --mode hide --data "SENSITIVE_INFO" --out hidden_secret.pdf

# Extract data
python3 hider.py universal hidden_secret.pdf --mode extract
```
