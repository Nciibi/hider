import sys
import os
import argparse
from metadata_engine import MetadataEngine
from universal_engine import UniversalEngine
from pdf_handler import PDFHandler

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
    extract_parser.add_argument("image", help="Path to the image file")
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
    universal_parser.add_argument("--mode", choices=["hide", "extract"], required=True)
    universal_parser.add_argument("--data", help="Data to hide (for hide mode)")
    universal_parser.add_argument("--out", help="Output path")

    # PDF commands
    pdf_parser = subparsers.add_parser("pdf", help="PDF metadata manipulation")
    pdf_parser.add_argument("file", help="Target PDF file")
    pdf_parser.add_argument("--mode", choices=["view", "edit"], required=True)
    pdf_parser.add_argument("--key", help="Metadata key (e.g. /Title)")
    pdf_parser.add_argument("--value", help="Metadata value")
    pdf_parser.add_argument("--out", help="Output path")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    try:
        if args.command in ["view", "edit", "inject", "hide", "extract"]:
            engine = MetadataEngine(args.image)
            
            if args.command == "view":
                engine.view_pretty()
        
        elif args.command == "edit":
            # Note: value parsing might need sophistication for types (bytes vs str vs int)
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
                UniversalEngine.tail_hide(args.file, args.data.encode(), args.out)
                print(f"Successfully hid data in {args.out or args.file}")
            elif args.mode == "extract":
                data = UniversalEngine.tail_extract(args.file)
                if data:
                    print(f"Extracted: {data.decode(errors='ignore')}")
                else:
                    print("No hidden data found.")

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

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
