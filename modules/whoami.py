"""
modules/whoami.py — System Identity Module

Generates commands to retrieve user identity and privilege information
on both Windows and Linux targets.
"""

MODULE_INFO = {
    "name": "whoami",
    "description": "Get current user identity and privileges",
    "author": "Hider",
    "platform": "all",
}


def run(session, args):
    """
    Returns the appropriate command to execute on the target.
    If session contains OS info, pick the right variant automatically.
    """
    os_type = "windows"
    if session and isinstance(session, dict):
        os_type = session.get("os", "windows").lower()

    if "linux" in os_type:
        return _linux_cmd()
    return _windows_cmd()


def _windows_cmd():
    return "whoami /all & hostname & net user %USERNAME%"


def _linux_cmd():
    return "id && hostname && whoami && groups"
