import zipfile
import os

class ArchiveHandler:
    DELIMITER = b"|||HIDER|||"

    @staticmethod
    def encode(zip_path, data, output_path):
        """
        Hides data within a ZIP file by appending it as an unreferenced extra file
        or padding the End of Central Directory (EOCD) record, which most parsers ignore.
        We'll use the EOCD padding approach for stealth.
        """
        if isinstance(data, str):
            data = data.encode('utf-8')
            
        data_to_hide = data + ArchiveHandler.DELIMITER
        
        # Verify it's a valid ZIP
        if not zipfile.is_zipfile(zip_path):
            raise ValueError("Target is not a valid ZIP archive.")
            
        with open(zip_path, 'rb') as f:
            zip_content = f.read()
            
        # Append data to the end of the ZIP (after EOCD)
        # Many zip tools ignore trailing data, making this a classic stego technique
        modified_content = zip_content + data_to_hide
        
        with open(output_path, 'wb') as f:
            f.write(modified_content)

    @staticmethod
    def decode(zip_path):
        """
        Extracts hidden data appended to the end of a ZIP file.
        """
        with open(zip_path, 'rb') as f:
            zip_content = f.read()
            
        # Search for the delimiter from the end
        delim_idx = zip_content.rfind(ArchiveHandler.DELIMITER)
        
        if delim_idx == -1:
            return None
            
        # The data starts somewhere after the true end of the ZIP.
        # To find the start, we'd theoretically need to parse the EOCD length,
        # but for simplicity in this implementation, if the file was only modified by us,
        # it might just be the tail chunk. 
        # A more robust search looks for the 0x06054b50 (EOCD signature) to find the true ZIP end.
        
        eocd_sig = b'PK\x05\x06'
        eocd_idx = zip_content.rfind(eocd_sig)
        
        if eocd_idx != -1:
            # EOCD is at least 22 bytes long. Let's assume standard length without comments
            # The structure is: Signature(4), DiskNo(2), CDStartDisk(2), RecordsOnDisk(2), TotalRecords(2), CDSize(4), CDOffset(4), CommentLength(2)
            # If comment length is 0, EOCD is 22 bytes. Any extra is our payload.
            comment_len = int.from_bytes(zip_content[eocd_idx+20:eocd_idx+22], byteorder='little')
            zip_end_idx = eocd_idx + 22 + comment_len
            
            if zip_end_idx < delim_idx:
                hidden_data = zip_content[zip_end_idx:delim_idx]
                return hidden_data
                
        # Fallback if EOCD parsing is tricky (e.g. multiple EOCDs)
        # Try finding the EOCD and scanning forward until delimiter.
        return None
