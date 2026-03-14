import base64
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad

class EncryptionEngine:
    @staticmethod
    def _get_key(password):
        """Generates a 256-bit key from a password using SHA-256."""
        hasher = SHA256.new(password.encode('utf-8'))
        return hasher.digest()

    @staticmethod
    def encrypt(data, password):
        """
        Encrypts data using AES-256-CBC.
        Returns base64 encoded string containing IV + Ciphertext.
        """
        key = EncryptionEngine._get_key(password)
        iv = get_random_bytes(AES.block_size)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        
        if isinstance(data, str):
            data = data.encode('utf-8')
            
        padded_data = pad(data, AES.block_size)
        ciphertext = cipher.encrypt(padded_data)
        
        # Prepend IV for decryption
        encrypted_blob = iv + ciphertext
        return base64.b64encode(encrypted_blob)

    @staticmethod
    def decrypt(encrypted_b64, password):
        """
        Decrypts base64 encoded AES-256-CBC (IV + Ciphertext).
        """
        try:
            encrypted_blob = base64.b64decode(encrypted_b64)
            key = EncryptionEngine._get_key(password)
            
            # Extract IV and ciphertext
            iv = encrypted_blob[:AES.block_size]
            ciphertext = encrypted_blob[AES.block_size:]
            
            cipher = AES.new(key, AES.MODE_CBC, iv)
            padded_data = cipher.decrypt(ciphertext)
            data = unpad(padded_data, AES.block_size)
            
            return data
        except Exception as e:
            raise ValueError(f"Decryption failed: Incorrect password or corrupted data. ({str(e)})")
