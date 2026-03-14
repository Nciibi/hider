# Audio & Archive Steganography

## 1. Concept: What is it?
While EXIF metadata is obvious if checked, true Steganography hides data within the actual structure of the file.
* **Audio LSB (Least Significant Bit):** `.wav` files store uncompressed audio frames. Changing the 1st bit of an 8-bit or 16-bit audio sample is imperceptible to the human ear, but allows us to encode binary data directly into the sound wave.
* **Archive Steganography:** The `.zip` format has an "End of Central Directory" (EOCD) record at the end of the file. By expanding the length of the comment field in the EOCD, or injecting data immediately *after* it, we can hide payloads without corrupting the unzipping capability.

## 2. Implementation: How does it work?

### Audio (`audio_handler.py`)
Uses the standard library `wave`. It reads the `.wav` file into a bytearray. It takes the binary representation of the secret payload (and a length header) and iterates over the audio bytearray, replacing the least significant bit (`byte & 254 | bit`) of each audio byte with a bit from the payload.

### Archives (`archive_handler.py`)
ZIP files are parsed backwards looking for the EOCD signature `\x50\x4b\x05\x06`. While Python's `zipfile` module allows writing comments, `ArchiveHandler` does structural padding: it injects a specific magic byte sequence (`HIDERSECRET`) right after the end of the file structure.

## 3. Usage
**CLI Command:**
```bash
# Audio Steganography
python3 hider.py audio clip.wav --mode hide --data "Secret Message" --out hidden.wav
python3 hider.py audio hidden.wav --mode extract

# Archive Padding
python3 hider.py archive backup.zip --mode hide --data "Payload" --out malicious.zip
python3 hider.py archive malicious.zip --mode extract
```
