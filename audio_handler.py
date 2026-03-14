import wave
import struct

class AudioHandler:
    DELIMITER = "|||HIDER|||"

    @staticmethod
    def encode(audio_path, data, output_path):
        """
        Hides data in the Least Significant Bits of a WAV file's audio frames.
        """
        data_to_hide = data + AudioHandler.DELIMITER
        
        # Convert data to binary string
        data_bin = ''.join([format(ord(c), '08b') for c in data_to_hide])
        
        # Read the audio file
        song = wave.open(audio_path, mode='rb')
        frame_bytes = bytearray(list(song.readframes(song.getnframes())))
        
        if len(data_bin) > len(frame_bytes):
            song.close()
            raise ValueError(f"Data is too large for this audio file! Required bits: {len(data_bin)}, Available bytes: {len(frame_bytes)}")
            
        # Replace LSB of each byte of the audio data
        for i, bit in enumerate(data_bin):
            frame_bytes[i] = (frame_bytes[i] & 254) | int(bit)
            
        # Write the modified frames back to a new audio file
        with wave.open(output_path, 'wb') as fd:
            fd.setparams(song.getparams())
            fd.writeframes(frame_bytes)
            
        song.close()

    @staticmethod
    def decode(audio_path):
        """
        Extracts hidden data from the Least Significant Bits of a WAV file.
        """
        song = wave.open(audio_path, mode='rb')
        frame_bytes = bytearray(list(song.readframes(song.getnframes())))
        song.close()
        
        # Extract LSB from each audio byte
        extracted_bits = [str(frame_byte & 1) for frame_byte in frame_bytes]
        
        # Group bits into bytes and convert to characters
        string_blocks = ["".join(extracted_bits[i:i+8]) for i in range(0, len(extracted_bits), 8)]
        decoded = ""
        
        for block in string_blocks:
            if len(block) == 8:
                decoded += chr(int(block, 2))
                if decoded.endswith(AudioHandler.DELIMITER):
                    return decoded[:-len(AudioHandler.DELIMITER)]
                    
        return None
