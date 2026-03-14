"""
c2/session.py — Session Manager

Tracks active implant sessions in a local SQLite database.
Each session stores: UUID, hostname, OS, username, IP, last check-in time,
and a command queue.
"""
import os
import json
import sqlite3
import uuid
from datetime import datetime


DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hider_c2.db")


def _get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create tables if they don't exist."""
    conn = _get_conn()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            hostname TEXT,
            os TEXT,
            username TEXT,
            ip TEXT,
            first_seen TEXT,
            last_seen TEXT,
            status TEXT DEFAULT 'active'
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS commands (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            command TEXT,
            status TEXT DEFAULT 'pending',
            result TEXT,
            created_at TEXT,
            completed_at TEXT,
            FOREIGN KEY (session_id) REFERENCES sessions(id)
        )
    """)
    conn.commit()
    conn.close()


def register(hostname, os_info, username, ip):
    """Register a new implant session. Returns the session UUID."""
    conn = _get_conn()
    c = conn.cursor()
    session_id = str(uuid.uuid4())[:8]
    now = datetime.utcnow().isoformat()
    c.execute(
        "INSERT INTO sessions (id, hostname, os, username, ip, first_seen, last_seen) VALUES (?,?,?,?,?,?,?)",
        (session_id, hostname, os_info, username, ip, now, now)
    )
    conn.commit()
    conn.close()
    return session_id


def heartbeat(session_id, ip=None):
    """Update the last_seen timestamp for a session."""
    conn = _get_conn()
    c = conn.cursor()
    now = datetime.utcnow().isoformat()
    if ip:
        c.execute("UPDATE sessions SET last_seen=?, ip=?, status='active' WHERE id=?", (now, ip, session_id))
    else:
        c.execute("UPDATE sessions SET last_seen=?, status='active' WHERE id=?", (now, session_id))
    conn.commit()
    conn.close()


def get_session(session_id):
    """Get a single session by ID."""
    conn = _get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM sessions WHERE id=?", (session_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None


def list_sessions():
    """Return all sessions."""
    conn = _get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM sessions ORDER BY last_seen DESC")
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def queue_command(session_id, command):
    """Queue a command for a session."""
    conn = _get_conn()
    c = conn.cursor()
    now = datetime.utcnow().isoformat()
    c.execute(
        "INSERT INTO commands (session_id, command, created_at) VALUES (?,?,?)",
        (session_id, command, now)
    )
    conn.commit()
    conn.close()


def get_pending(session_id):
    """Get the next pending command for a session (FIFO)."""
    conn = _get_conn()
    c = conn.cursor()
    c.execute(
        "SELECT * FROM commands WHERE session_id=? AND status='pending' ORDER BY id ASC LIMIT 1",
        (session_id,)
    )
    row = c.fetchone()
    if row:
        c.execute("UPDATE commands SET status='sent' WHERE id=?", (row['id'],))
        conn.commit()
    conn.close()
    return dict(row) if row else None


def store_result(command_id, result):
    """Store the result of a command execution."""
    conn = _get_conn()
    c = conn.cursor()
    now = datetime.utcnow().isoformat()
    c.execute(
        "UPDATE commands SET result=?, status='completed', completed_at=? WHERE id=?",
        (result, now, command_id)
    )
    conn.commit()
    conn.close()


def get_results(session_id, limit=20):
    """Get recent command results for a session."""
    conn = _get_conn()
    c = conn.cursor()
    c.execute(
        "SELECT * FROM commands WHERE session_id=? ORDER BY id DESC LIMIT ?",
        (session_id, limit)
    )
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def kill_session(session_id):
    """Mark a session as dead."""
    conn = _get_conn()
    c = conn.cursor()
    c.execute("UPDATE sessions SET status='dead' WHERE id=?", (session_id,))
    conn.commit()
    conn.close()


# Initialize DB on import
init_db()
