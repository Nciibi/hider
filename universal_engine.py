import os

class UniversalEngine:
    @staticmethod
    def tail_hide(target_path, data_to_hide, output_path=None):
        """Appends data to the end of any file."""
        if output_path is None:
            output_path = target_path
            
        with open(target_path, "rb") as f:
            original_data = f.read()
            
        # Add a unique delimiter for extraction
        delimiter = b"\x00\xffHIDER_START\xff\x00"
        modified_data = original_data + delimiter + data_to_hide
        
        with open(output_path, "wb") as f:
            f.write(modified_data)
        return output_path

    @staticmethod
    def tail_extract(target_path):
        """Extracts data appended after the delimiter."""
        delimiter = b"\x00\xffHIDER_START\xff\x00"
        with open(target_path, "rb") as f:
            data = f.read()
            
        idx = data.rfind(delimiter)
        if idx == -1:
            return None
        return data[idx + len(delimiter):]

    @staticmethod
    def create_polyglot(file1_path, file2_path, output_path):
        """Simple polyglot: Combines two files. 
        Works best for formats like ZIP+JPG where engines read from different ends.
        """
        with open(file1_path, "rb") as f1, open(file2_path, "rb") as f2:
            data1 = f1.read()
            data2 = f2.read()
            
        with open(output_path, "wb") as out:
            out.write(data1 + data2)
        return output_path
