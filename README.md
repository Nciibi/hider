# Hider: Universal Metadata & Steganography Tool

Hider is a powerful command-line utility designed for security researchers and penetration testers. It allows for the manipulation of metadata across a wide range of file formats, providing capabilities for spoofing, data concealment (steganography), and security testing.

## 🚀 Features

- **EXIF Manipulation**: View, edit, and inject payloads into image metadata (JPG, TIFF).
- **Security Payloads**: Predefined injections for XSS, Buffer Overflows, and Null Byte testing.
- **Universal Steganography**: "Tail-loading" technique to hide data in *any* binary file.
- **PDF Support**: Deep metadata editing and object injection.
- **Office Support**: Full core property manipulation for Word (`.docx`), Excel (`.xlsx`), and PowerPoint (`.pptx`).
- **DLL / PE Support**: Structural data hiding in Windows executables and libraries.
- **JPEG Exploits**: Advanced segment manipulation (Pre-header and EOI trailing data).

## 🛠️ Installation

```bash
# Clone the repository
git clone https://github.com/user/hider.git
cd hider

# Set up virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install Pillow piexif pypdf python-docx openpyxl python-pptx pefile
```

## 📖 Usage Examples

### 1. Image EXIF Injection (XSS)
```bash
python3 hider.py inject image.jpg --type xss --out malicious.jpg
```

### 2. Universal Data Hiding (Any Format)
```bash
python3 hider.py universal secret.pdf --mode hide --data 'SENSITIVE_INFO'
python3 hider.py universal secret.pdf --mode extract
```

### 3. PDF Metadata Editing
```bash
python3 hider.py pdf document.pdf --mode edit --key /Author --value 'Anonymous'
```

### 4. Office Document Spoofing
```bash
python3 hider.py office report.docx --mode edit --key author --value 'Trusted User'
```

### 5. DLL Steganography
```bash
python3 hider.py dll plugin.dll --mode hide --data 'C2_SERVER_URL'
```

## ⚠️ Disclaimer

This tool is for **educational and ethical security research purposes only**. Never use Hider on systems or files you do not have explicit permission to test. The authors are not responsible for any misuse or damage caused by this tool.

## 📄 License

MIT License
