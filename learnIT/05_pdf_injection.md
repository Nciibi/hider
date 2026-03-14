# PDF JavaScript Injection

## 1. Concept: What is it?
The Portable Document Format (PDF) supports embedded JavaScript for form validation and interactive features. Specifically, the `OpenAction` dictionary specifies an action to be performed when the document is opened.

By injecting a `/JS` (JavaScript) object into the `/OpenAction` dictionary, an attacker can force arbitrary JavaScript to execute immediately upon the user opening the PDF. This can be used to harvest NTLM hashes (via SMB requests), trigger browser vulnerabilities, or launch Phishing prompts.

## 2. Implementation: How does it work?
In `pdf_handler.py`, the `PDFHandler` class uses the `pypdf` library to parse and manipulate the PDF's internal object tree (the cross-reference table).

To evade basic static analysis (like `strings` or naive AV signatures), the handler implements an `--obfuscate` flag:
1. It reads the user's raw JavaScript payload.
2. It converts the payload into a Hex-encoded string wrapper (e.g., `eval(unescape('%61%6C%65%72%74...'))`).
3. It creates a new `/Action` dictionary in the PDF catalog.
4. It sets `/S` to `/JavaScript` and `/JS` to the obfuscated payload.
5. It overwrites the document's `/OpenAction` pointer to reference this new dictionary.

## 3. Usage
**CLI Command:**
```bash
# Basic JS alert injection
python3 hider.py pdf report.pdf --mode open-action --value "app.alert('Hello');"

# Obfuscated JS injection (evades static signatures)
python3 hider.py pdf report.pdf --mode open-action --value "app.alert('Obfuscated');" --obfuscate
```
