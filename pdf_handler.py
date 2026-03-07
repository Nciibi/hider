from pypdf import PdfReader, PdfWriter
import io

class PDFHandler:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path

    def get_metadata(self):
        reader = PdfReader(self.pdf_path)
        return reader.metadata

    def update_metadata(self, key, value, output_path=None):
        if output_path is None:
            output_path = self.pdf_path
            
        reader = PdfReader(self.pdf_path)
        writer = PdfWriter()
        
        for page in reader.pages:
            writer.add_page(page)
            
        metadata = reader.metadata or {}
        new_metadata = {k: v for k, v in metadata.items()}
        # Standard PDF metadata keys usually start with /
        actual_key = key if key.startswith("/") else f"/{key}"
        new_metadata[actual_key] = value
        
        writer.add_metadata(new_metadata)
        
        with open(output_path, "wb") as f:
            writer.write(f)
        return output_path

    def inject_hidden_object(self, data, output_path=None):
        """Experimental: Injects a custom non-rendered object into the PDF."""
        # Simple implementation using metadata for now, 
        # but could be expanded to actual stream objects.
        return self.update_metadata("/HiderPayload", data, output_path)
