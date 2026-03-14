# Sandbox Detection Wrappers

## 1. Concept: What is it?
Modern email filters and Endpoint Detection & Response (EDR) solutions automatically detonate suspicious files and scripts in a virtual "Sandbox" environment to monitor their behavior.

Sandbox Detection is the practice of querying the environment for signs that the script is running in an analysis VM rather than a real user's workstation. Typical signs of a sandbox include:
* Very low RAM (e.g., < 4GB)
* Only 1 or 2 CPU cores
* The machine is not joined to an Active Directory Domain
* Time moves unusually fast

If these conditions are met, the script quietly exits *before* downloading the malicious payload, leaving the sandbox with no malicious behavior to flag.

## 2. Implementation: How does it work?
In `evasion_engine.py`, the `EvasionEngine` generates JScript and VBScript wrappers using Windows Management Instrumentation (WMI) and the `WScript.Network` object.

1. **Domain Check:** `network.UserDomain == network.ComputerName` indicates a local standalone machine, not an AD-joined workstation.
2. **RAM Check:** Queries `Win32_ComputerSystem TotalPhysicalMemory` via WMI.
3. **Core Check:** Queries `Win32_ComputerSystem NumberOfLogicalProcessors` via WMI.
4. **Sleep & Jitter:** Uses `WScript.Sleep()` but injects random "jitter" math so the sleep duration is inconsistent, breaking Machine Learning models that track precise process timings.
5. **API Hammering:** Calls harmless but loud Windows APIs (like reading the Registry Product Name in a tight loop 30 times) to overwhelm sandbox API telemetry hooks.

## 3. Usage
**CLI Command:**
```bash
# Generate a JScript payload that requires 8GB RAM, 4 cores, and a 20-second jittered sleep
python3 hider.py evasion --payload "powershell -c calc.exe" --type jscript \
    --min-ram 8 --min-cores 4 --sleep 20000 --out stealthyle.js

# Generate a VBScript payload that aborts if not domain-joined
python3 hider.py evasion --payload "cmd /c whoami" --type vbscript --check-domain --out stealth.vbs
```
