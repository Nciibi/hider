# Hider: Universal Metadata & Steganography Tool

Hider is a powerful command-line and web-based utility designed for security researchers and penetration testers. It allows for the manipulation of metadata across a wide range of file formats, providing capabilities for spoofing, data concealment (steganography), and security testing.

![Hider Dashboard](assets/gui_main.png)

## 🚀 Features

- **Hider Dashboard (GUI)**: A modern, glassmorphic web interface for easy file processing.
- **Advanced Evasion**: HTA obfuscation and PDF JS encoding to bypass AV/EDR (Windows Defender).
- **EXIF Manipulation**: View, edit, and inject payloads into image metadata (JPG, TIFF).
- **Security Payloads**: Predefined injections for XSS, Buffer Overflows, and Null Byte testing.
- **Universal Steganography**: "Tail-loading" technique to hide data in *any* binary file.
- **PDF Support**: Deep metadata editing, JavaScript injection, and object manipulation.
- **Office Support**: Full core property manipulation for Word (`.docx`), Excel (`.xlsx`), and PowerPoint (`.pptx`).
- **DLL / PE Support**: Structural data hiding in Windows executables and libraries.

## 🛠️ Installation

```bash
# Clone the repository
git clone https://github.com/user/hider.git
cd hider

# Set up virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install Pillow piexif pypdf python-docx openpyxl python-pptx pefile flask
```

## 🖥️ Usage: Hider Dashboard (GUI)

To launch the web interface:
```bash
python3 app.py
```
Open your browser and navigate to `http://127.0.0.1:5000`.

## 📖 Usage: CLI Examples

### 1. Advanced Evasion (Obfuscated PDF JS)
```bash
python3 hider.py pdf document.pdf --mode open-action --value "app.alert('Hello');" --obfuscate
```

### 2. HTA Polyglot with AMSI Bypass
```bash
python3 hider.py universal image.jpg --mode hta-polyglot --data "msgbox 'Hello'" --obfuscate --out payload.hta
```

### 3. Image EXIF Injection (XSS)
```bash
python3 hider.py inject image.jpg --type xss --out malicious.jpg
```

### 4. Universal Data Hiding
```bash
python3 hider.py universal secret.pdf --mode hide --data 'SENSITIVE_INFO'
```

## ⚠️ Disclaimer

This tool is for **educational and ethical security research purposes only**. Never use Hider on systems or files you do not have explicit permission to test. The authors are not responsible for any misuse or damage caused by this tool.

## 📄 License

MIT License
