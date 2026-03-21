# Lateral Movement via SMB (Fileless)

## What is SMB Lateral Movement?
Server Message Block (SMB) is widely used in Windows domains for file sharing and inter-process communication. Traditional "PsExec-style" lateral movement involves copying an executable to an `Admin$` share and creating a Windows Service to execute it. This touches disk and spawns highly suspicious child processes.

## The Hider Implementation (`lat_smb`)
Hider upgrades this technique to be entirely **fileless**. Instead of dropping a binary, it encodes a PowerShell payload into Base64 and leverages the WMI Provider over SMB to create a `Win32_Service` directly from memory. 

The service `binPath` points directly to an obfuscated memory execution (e.g., `powershell.exe -enc ...`), which means no `.exe` artifacts ever touch the target system's disk.
