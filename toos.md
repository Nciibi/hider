# Hider Tools & Kits

This document lists all tools and capabilities included in the Hider framework.

## 🖥️ GUI Dashboard
- **Flask Web UI** - Modern glassmorphic interface for all operations (app.py)

## 📸 Image Manipulation
- **EXIF Metadata Engine** - View, edit, and inject payloads into JPG/TIFF metadata (metadata_engine.py)
- **LSB Steganography Engine** - Hide data in least-significant bits of lossless images (PNG, BMP) (lsb_engine.py)

## 🎵 Audio Steganography
- **WAV LSB Handler** - Hide data in the least-significant bits of .wav audio files (audio_handler.py)

## 📦 Archive Steganography
- **ZIP Padding Handler** - Inject hidden data into ZIP tail space (file remains valid) (archive_handler.py)

## 🔧 Universal Steganography
- **Universal Tail-Loading Engine** - Append data to the end of any binary file (universal_engine.py)
- **Polyglot Generator** - Merge two file formats into one (e.g., JPG+ZIP) (poly_engine.py)

## 📄 PDF Manipulation
- **PDF Handler** - Inject obfuscated JavaScript into PDF Open Actions (pdf_handler.py)

## 📊 Office Document Manipulation
- **Office Handler** - Manipulate core properties in .docx, .xlsx, .pptx files (office_handler.py)

## 🖥️ Executable Manipulation
- **PE Handler** - Hide data inside Windows executable resources (pe_handler.py)
- **Shortcut Handler** - Generate malicious .lnk shortcuts (lnk_handler.py)

## 🎥 Video Metadata Manipulation
- **Video Handler** - Manipulate tags via FFmpeg (video_handler.py)

## 🛡️ Evasion & Bypass
- **Evasion Engine** - HTA polyglots with AMSI bypass obfuscation (evasion_engine.py)
- **Sandbox Detection** - JScript/VBScript wrappers checking RAM, CPU, domain (evasion_engine.py)
- **VBA Macro Generator** - Auto-generate weaponized, obfuscated VBA macros (macro_engine.py)
- **Polymorphic Payload Wrapper** - Wrap payloads with unique AES encryption (poly_engine.py)
- **AMSI & ETW Patch Generator** - Generate PowerShell patch snippets (patch_engine.py)
- **Domain Fronting Generator** - Generate Domain Fronting payloads (CDN abuse) (front_engine.py)

## 🔐 Encryption & Obfuscation
- **Encryption Engine** - AES-256 encryption for any payload (encryption_engine.py)
- **Sleep Masking** - Memory sleep masking for opsec (c2/beacon_gen.py)

## 🛰️ Command & Control
- **C2 Server** - Flask-based HTTPS listener with SQLite session tracking (c2/server.py)
- **C2 Console** - Interactive shell for managing implants, commands, and modules (c2/console.py)
- **Beacon Generator** - Create custom P2P/bind beacons with sleep masking & domain rotation (c2/beacon_gen.py)
- **Session Manager** - Track active sessions with heartbeat and command queuing (c2/session.py)

## 🔗 Lateral Movement
- **SMB Module** - Fileless SMB pivoting (modules/lat_smb.py)
- **WMI Module** - Encoded WMI pivoting (modules/lat_wmi.py)
- **WinRM Module** - Encoded WinRM pivoting (modules/lat_winrm.py)
- **SSH Module** - Piped SSH pivoting (modules/lat_ssh.py)
- **P2P Link Module** - Named-pipe SMB pivoting between implants (modules/p2p_link.py)
- **Screenshot Module** - Capture and exfiltrate screenshots (modules/screenshot.py)
- **Sysinfo Module** - Gather system information (modules/sysinfo.py)
- **Whoami Module** - Enumerate user privileges (modules/whoami.py)
- **Hollow Process Module** - In-memory code execution via process hollowing (modules/hollow.py)
- **Shellcode Injection** - VirtualAlloc + CreateThread shellcode injection (modules/inject_shellcode.py)
- **PowerShell Injection** - .NET assembly execution (modules/inject_dotnet.py)
- **Python Injection** - ctypes + mmap based shellcode loader (modules/inject_python.py)
- **Registry Persistence** - Add HKCU Run key persistence (modules/persist_registry.py)
- **Cron Persistence** - Add crontab entries for persistence (modules/persist_cron.py)

## 📦 Staging & Recipes
- **Staging Engine** - Automated recipes for multi-stage attack chains (c2/stager.py)
  - `windows_full` - AMSI patch + shellcode stager
  - `lnk_dropper` - Certutil + LNK stager
  - `office_macro` - Beacon macros
  - `linux_memfd` - Linux memory stagers
  - `fronted_ps` - Fronted PowerShell

## 🔧 Loaders & Stagers
- **Loader Engine** - Generate Reflective In-Memory Stagers (loader_engine.py)
- **Front Engine** - Domain fronting payloads (CDN abuse) (front_engine.py)

## 🎯 LOLBin Chains
- **LOLBin Engine** - Generate LOLBin payload chains (mshta, rundll32, certutil, etc.) (lolbin_engine.py)

## ⚙️ Module System
- **Plugin Loader** - Hot-loadable module system for post-exploitation commands (__init__.py in modules/)

## 📈 Operational Security (OpSec)
- **Traffic Shaping** - Jitter-aware beaconing with sleep variance
- **Domain Rotation** - Automatic domain rotation for C2
- **Base64 Encoding** - Payload encoding for covert delivery
- **Custom Headers** - HTTP header manipulation

## 🔐 Advanced Features
- **mTLS Support** - Mutual TLS for encrypted C2 channels
- **Certificate Management** - Automatic certificate generation and rotation
- **Jitter Implementation** - Random sleep intervals for beacon detection avoidance
- **Kill Date Management** - Time-based beacon termination
- **Memory Protection** - AMSI and ETW patching

## 📚 Documentation & Learning
- **LearnIT Documentation** - Comprehensive guides for every feature (learnIT/)
- **Implementation Plan** - Detailed architecture and roadmap (implementation_plan.md)
- **CLI Reference** - Complete command-line interface documentation (README.md)

## 📊 Total Capabilities: 45+ Specialized Tools
Hider provides an extensive toolkit for:
- **Steganography** (7 techniques)
- **File Format Abuse** (5 formats)
- **Evasion & Sandbox Bypass** (4 techniques)
- **C2 Infrastructure** (3 components)
- **Lateral Movement** (15 modules)
- **Payload Generation** (5 engines)
- **Persistence** (2 mechanisms)
- **Operational Security** (4 layers)

The framework seamlessly integrates penetration testing, post-exploitation, and command-and-control operations into a unified platform.