import os
import secrets
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from hider import MetadataEngine, UniversalEngine, PDFHandler, OfficeHandler, PEHandler, VideoHandler, LSBEngine, LNKHandler, EncryptionEngine, AudioHandler, ArchiveHandler

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/process', methods=['POST'])
def process():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    command = request.form.get('command')
    mode = request.form.get('mode')
    
    filename = secure_filename(file.filename)
    input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(input_path)
    
    output_filename = f"hider_{filename}"
    output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
    
    try:
        if command == 'universal':
            data = request.form.get('data', '')
            password = request.form.get('password', '')
            
            if mode == 'hide':
                payload = data.encode()
                if password:
                    b64_cipher = EncryptionEngine.encrypt(payload, password)
                    payload = b"ENC:" + b64_cipher

                UniversalEngine.tail_hide(input_path, payload, output_path)
            elif mode == 'extract':
                extracted = UniversalEngine.tail_extract(input_path)
                result = ""
                if extracted:
                    if extracted.startswith(b"ENC:") and password:
                        try:
                            decrypted = EncryptionEngine.decrypt(extracted[4:], password)
                            result = decrypted.decode(errors='ignore')
                        except Exception as e:
                            result = f"Failed to decrypt: Incorrect password or corrupted data."
                    else:
                        result = extracted.decode(errors='ignore')
                return jsonify({'success': True, 'extracted': result})
            elif mode == 'hta-polyglot':
                obfuscate = request.form.get('obfuscate') == 'true'
                UniversalEngine.create_hta_polyglot(input_path, data, output_path, obfuscate=obfuscate)
                if not output_filename.endswith('.hta'):
                    os.rename(output_path, output_path + '.hta')
                    output_filename += '.hta'
        
        elif command == 'pdf':
            handler = PDFHandler(input_path)
            value = request.form.get('value', '')
            if mode == 'open-action':
                obfuscate = request.form.get('obfuscate') == 'true'
                if obfuscate:
                    handler.inject_obfuscated_js(value, output_path)
                else:
                    handler.inject_open_action(value, output_path)
            elif mode == 'edit':
                key = request.form.get('key', '')
                handler.update_metadata(key, value, output_path)
        
        elif command == 'office':
            handler = OfficeHandler(input_path)
            key = request.form.get('key', '')
            value = request.form.get('value', '')
            handler.update_metadata(key, value, output_path)
            
        elif command == 'dll':
            handler = PEHandler(input_path)
            data = request.form.get('data', '')
            handler.update_version_string("HiderData", data, output_path)

        elif command == 'video':
            handler = VideoHandler(input_path)
            key = request.form.get('key', '')
            value = request.form.get('value', '')
            if mode == 'edit':
                handler.update_metadata(key, value, output_path)

        elif command == 'lsb':
            data = request.form.get('data', '')
            password = request.form.get('password', '')
            if mode == 'hide':
                payload_str = data
                if password:
                    b64_cipher = EncryptionEngine.encrypt(payload_str, password)
                    payload_str = "ENC:" + b64_cipher.decode('utf-8')
                LSBEngine.encode(input_path, payload_str, output_path)
            elif mode == 'extract':
                extracted = LSBEngine.decode(input_path)
                if extracted and extracted.startswith("ENC:") and password:
                    try:
                        decrypted = EncryptionEngine.decrypt(extracted[4:].encode('utf-8'), password)
                        extracted = decrypted.decode(errors='ignore')
                    except Exception as e:
                        extracted = f"Failed to decrypt: Incorrect password or corrupted data."
        elif command == 'audio':
            data = request.form.get('data', '')
            password = request.form.get('password', '')
            if mode == 'hide':
                payload_str = data
                if password:
                    b64_cipher = EncryptionEngine.encrypt(payload_str, password)
                    payload_str = "ENC:" + b64_cipher.decode('utf-8')
                AudioHandler.encode(input_path, payload_str, output_path)
            elif mode == 'extract':
                extracted = AudioHandler.decode(input_path)
                if extracted and extracted.startswith("ENC:") and password:
                    try:
                        decrypted = EncryptionEngine.decrypt(extracted[4:].encode('utf-8'), password)
                        extracted = decrypted.decode(errors='ignore')
                    except Exception as e:
                        extracted = f"Failed to decrypt: Incorrect password or corrupted data."
                return jsonify({'success': True, 'extracted': extracted})
                
        elif command == 'archive':
            data = request.form.get('data', '')
            password = request.form.get('password', '')
            if mode == 'hide':
                payload = data.encode()
                if password:
                    b64_cipher = EncryptionEngine.encrypt(payload, password)
                    payload = b"ENC:" + b64_cipher
                ArchiveHandler.encode(input_path, payload, output_path)
            elif mode == 'extract':
                extracted = ArchiveHandler.decode(input_path)
                result = ""
                if extracted:
                    if extracted.startswith(b"ENC:") and password:
                        try:
                            decrypted = EncryptionEngine.decrypt(extracted[4:], password)
                            result = decrypted.decode(errors='ignore')
                        except Exception as e:
                            result = f"Failed to decrypt: Incorrect password or corrupted data."
                    else:
                        result = extracted.decode(errors='ignore')
                return jsonify({'success': True, 'extracted': result})

        elif command == 'shortcut':
            cmd = request.form.get('data', '')
            output_filename = "malicious.lnk"
            output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
            LNKHandler.create_lnk_payload(cmd, output_path)
            return jsonify({'success': True, 'filename': output_filename})

        return jsonify({'success': True, 'filename': output_filename})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
