"""One SQLite database on a local disk; writes include their audit event."""
import sqlite3
from contextlib import contextmanager
from pathlib import Path

def connect(path):
    conn = sqlite3.connect(str(path), timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA busy_timeout=10000")
    return conn

@contextmanager
def transaction(path, *, write=False):
    conn = connect(path)
    try:
        conn.execute("BEGIN IMMEDIATE" if write else "BEGIN")
        yield conn
        conn.commit()
    except BaseException:
        conn.rollback()
        raise
    finally:
        conn.close()

def initialize(path):
    from . import domain
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    conn = connect(path)
    try:
        conn.execute("PRAGMA journal_mode=WAL")
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY, password_hash TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('admin','analyst','auditor')),
                active INTEGER NOT NULL DEFAULT 1 CHECK(active IN (0,1))
            );
            CREATE TABLE IF NOT EXISTS sessions (
                token_hash TEXT PRIMARY KEY, username TEXT NOT NULL REFERENCES users(username),
                csrf_token TEXT NOT NULL, expires_at INTEGER NOT NULL, last_seen INTEGER NOT NULL
            );
            CREATE INDEX IF NOT EXISTS sessions_user ON sessions(username);
            CREATE TABLE IF NOT EXISTS login_limits (
                key TEXT PRIMARY KEY, window_start INTEGER NOT NULL, failures INTEGER NOT NULL
            );
        """)
        version = conn.execute("SELECT value FROM metadata WHERE key='schema_version'").fetchone()
        if version and version[0] != "1":
            raise RuntimeError("Unsupported database schema; restore a compatible backup")
        domain.init_schema(conn)
        conn.execute("INSERT OR IGNORE INTO metadata VALUES ('schema_version','1')")
        conn.commit()
    finally:
        conn.close()

def demo_enabled(conn):
    row = conn.execute("SELECT value FROM metadata WHERE key='demo'").fetchone()
    return bool(row and row[0] == "true")

