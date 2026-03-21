# Lateral Movement via WinRM

## What is WinRM?
Windows Remote Management (WinRM) is a built-in feature that enables administrators to execute PowerShell commands remotely. It uses SOAP over HTTP/HTTPS, making it highly firewall-friendly compared to traditional SMB (Port 445).

## How it works for Lateral Movement
Normally, one can use `Invoke-Command` to send a `ScriptBlock` to a remote system. However, the raw contents of these script blocks are transmitted over the network and heavily scrutinized by the Anti-Malware Scan Interface (AMSI) upon execution.

### The Hider Implementation (`lat_winrm`)
The `lat_winrm` module builds a wrapper `ScriptBlock` that decodes a Base64-encoded payload dynamically inside the remote session. By doing this, the raw malicious payload is never transmitted in plaintext across the WSMan tunnel, significantly reducing the chances of network-based IDS or basic AMSI signature detection.
