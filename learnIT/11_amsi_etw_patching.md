# AMSI and ETW Patching

## 1. Concept: What is it?
Microsoft provides two primary telemetry engines used by AV/EDR solutions:
* **AMSI (Anti-Malware Scan Interface):** Allows applications (like PowerShell or MSHTA) to pass in-memory script contents to an antivirus scanner *before* execution.
* **ETW (Event Tracing for Windows):** A kernel-level instrumentation framework that logs system events (like process creation, API calls) for EDR analysis.

Since these components run in user-mode inside the current process block (in `amsi.dll` and `ntdll.dll`), their memory space can be overwritten. "Patching" involves writing a single byte (like `0xC3` for `RET`, or `0xB8,0x57,0x00,0x07,0x80,0xC3` to return a fake "clean" code) over the engine's core functions (`AmsiScanBuffer` and `EtwEventWrite`).

## 2. Implementation: How does it work?
In `patch_engine.py`, the `PatchEngine` dynamically generates PowerShell snippets using `.NET` interop techniques (specifically `[Runtime.InteropServices.Marshal]::Copy`).

To defeat static signatures (which frequently flag standard AMSI bypass scripts), the engine is highly polymorphic:
1. It generates random, 8-character string names for every variable, object, and assembly reference (e.g., `${vK}` instead of `$kernel32`).
2. It breaks strings apart (`AmsiSc'+'anBuffer`) to evade simple string-matching rules.
3. For ETW patches, it generates a custom C# class in-memory via `Add-Type` to call `VirtualProtect` allowing the memory page to be overwritten.
4. The output is a snippet that can be prepended to any malicious script, disabling telemetry for the remainder of that process's lifespan.

## 3. Usage
**CLI Command:**
```bash
# Generate a combined AMSI+ETW polymorphic patch
python3 hider.py patch --target all --out stealth_patch.ps1

# Generate a Base64 encoded payload that executes the bypass natively
python3 hider.py patch --target amsi --obfuscate --out patch.txt
```
