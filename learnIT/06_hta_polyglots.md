# HTA Polyglots

## 1. Concept: What is it?
A "Polyglot" is a file that is perfectly valid in two different formats simultaneously. 
An HTA (HTML Application) Polyglot typically combines an Image (like a `.jpg`) with an `.hta` file. 

Because HTML parsers (specifically MSHTA.exe) are extremely forgiving, they will ignore the binary image data and execute any `<script>` tags found within the file. If an attacker tricks a user into downloading this file and running it via `mshta.exe`, it will display the image but silently execute the malicious script in the background.

## 2. Implementation: How does it work?
In `universal_engine.py`, the `UniversalEngine.create_hta_polyglot` method constructs this payload.
1. It reads the binary bytes of the cover image.
2. It generates an HTA shell containing a hidden window (`<HTA:APPLICATION ... WINDOWSTATE="minimize">`).
3. If `--obfuscate` is passed, it uses `EvasionEngine`'s obfuscation to encode the VBScript payload to bypass AMSI (Anti-Malware Scan Interface).
4. The script is injected between `<script language="VBScript">` tags.
5. The final payload is the raw Image bytes + a newline + the HTA HTML text.

When opened as an image, the image viewer ignores the text at the end. When opened with `mshta`, the parser ignores the binary "garbage" at the top and runs the script.

## 3. Usage
**CLI Command:**
```bash
# Create an HTA polyglot that runs calc.exe
python3 hider.py universal cute_cat.jpg --mode hta-polyglot --data "calc.exe" --out payload.hta

# Create an obfuscated polyglot to bypass AMSI
python3 hider.py universal cute_cat.jpg --mode hta-polyglot --data "powershell -c IEX(etc)" --obfuscate --out payload.hta
```
