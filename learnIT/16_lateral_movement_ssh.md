# Lateral Movement via SSH Pivoting

## What is SSH Lateral Movement?
Secure Shell (SSH) is the ubiquitous administrative protocol on Linux, macOS, and increasingly, Windows environments. Adversaries who compromise SSH keys or credentials use the protocol to pivot deeper into the network.

## The Hider Implementation (`lat_ssh`)
A naive SSH pivot command (`ssh target "malicious_command"`) leaves plaintext artifacts in the target's `.bash_history` file, system logs, and process arguments (`ps aux`).

To achieve military-grade OpSec, Hider's `lat_ssh` module prevents this by encoding the payload on the C2 server natively. It establishes an SSH tunnel and pipes the encoded payload directly into standard input (`echo <b64> | base64 -d | sh`). Because the command arguments to `ssh` are just standard Unix pipe binaries, the actual payload is never recorded in system logs or shell memory histories.
