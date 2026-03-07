from PIL import Image
import numpy as np

class LSBEngine:
    @staticmethod
    def encode(image_path, data, output_path):
        """
        Hides data in the least significant bits of an image.
        Supports PNG and other lossless formats.
        """
        img = Image.open(image_path).convert('RGB')
        pixels = np.array(img)
        
        # Convert data to binary string
        # Add a delimiter to know when to stop decoding
        delimiter = '###DONE###'
        data_bin = ''.join([format(ord(i), '08b') for i in (data + delimiter)])
        
        if len(data_bin) > pixels.size:
            raise ValueError("Data too large for image")
        
        # Flatten pixels and modify LSB
        flat_pixels = pixels.flatten()
        for i in range(len(data_bin)):
            # Use safer bit manipulation to avoid signedness issues with ~1
            flat_pixels[i] = (flat_pixels[i] >> 1 << 1) | int(data_bin[i])
        
        # Reshape back to image dimensions
        new_pixels = flat_pixels.reshape(pixels.shape)
        new_img = Image.fromarray(new_pixels.astype('uint8'), 'RGB')
        new_img.save(output_path)
        return output_path

    @staticmethod
    def decode(image_path):
        """
        Extracts hidden data from the least significant bits of an image.
        """
        img = Image.open(image_path).convert('RGB')
        pixels = np.array(img)
        flat_pixels = pixels.flatten()
        
        binary_data = ""
        for i in range(len(flat_pixels)):
            binary_data += str(flat_pixels[i] & 1)
        
        # Convert binary string to chars
        all_bytes = [binary_data[i:i+8] for i in range(0, len(binary_data), 8)]
        decoded_data = ""
        for byte in all_bytes:
            if len(byte) < 8: break
            decoded_char = chr(int(byte, 2))
            decoded_data += decoded_char
            if "###DONE###" in decoded_data:
                return decoded_data.replace("###DONE###", "")
        
        return ""
