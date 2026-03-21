# Lateral Movement via WMI

## What is WMI?
Windows Management Instrumentation (WMI) is Microsoft's implementation of Web-Based Enterprise Management (WBEM). It provides a standardized way to manage devices and systems within a Windows network. 

## How it works for Lateral Movement
Adversaries use WMI to execute code on remote systems without relying on traditional SMB-based mechanisms (like dropping executables and creating services with `sc.exe`). Using the `Win32_Process` class, one can instantiate a new process on a remote machine.

### The Hider Implementation (`lat_wmi`)
The traditional approach passes raw command strings, which are easily logged by EDRs (Event ID 4688: Process Creation). 
In Hider's `lat_wmi` module, the payload is dynamically encoded into Base64 on the attacker's side before invoking the remote WMI call. The executed process is encoded (`powershell.exe -nop -w hidden -enc <BASE64>`), hiding the actual payload from command-line arguments logs.
