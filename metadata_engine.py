import piexif
from PIL import Image
import os

class MetadataEngine:
    def __init__(self, image_path):
        self.image_path = image_path
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")
        self.exif_dict = piexif.load(image_path)

    def get_all_exif(self):
        """Returns the raw EXIF dictionary."""
        return self.exif_dict

    def view_pretty(self):
        """Prints a human-readable list of EXIF tags."""
        for ifd in ("0th", "Exif", "GPS", "1st"):
            print(f"\n--- {ifd} IFD ---")
            for tag in self.exif_dict[ifd]:
                tag_name = piexif.TAGS[ifd][tag]["name"]
                value = self.exif_dict[ifd][tag]
                print(f"{tag_name} ({tag}): {value}")

    def update_tag(self, ifd, tag, value):
        """Updates a specific tag in a given IFD."""
        if ifd not in self.exif_dict:
            raise ValueError(f"Invalid IFD: {ifd}")
        self.exif_dict[ifd][tag] = value

    def inject_payload(self, ifd, tag, payload):
        """Injects a payload into a specific tag."""
        # This is basically update_tag but semi-documented for 'injection'
        # Can be expanded for specific exploit types later
        self.update_tag(ifd, tag, payload)

    def save(self, output_path=None):
        """Saves the modified EXIF data back to the image."""
        if output_path is None:
            output_path = self.image_path
        
        exif_bytes = piexif.dump(self.exif_dict)
        img = Image.open(self.image_path)
        img.save(output_path, exif=exif_bytes)
        print(f"Saved modified image to: {output_path}")

if __name__ == "__main__":
    # Quick test logic if run directly
    pass
