"""Password authentication and revocable opaque sessions."""
import hashlib
import hmac
import re
import secrets
import time

ROLES = {"admin", "analyst", "auditor"}
USERNAME = re.compile(r"[a-z0-9][a-z0-9_.-]{2,63}\Z")
SCRYPT_N = 131072
MIN_PASSWORD_LENGTH = 14
MAX_PASSWORD_LENGTH = 128

def normalize_username(value):
    value = value.strip().lower()
    if not USERNAME.fullmatch(value):
        raise ValueError("Username needs 3-64 lowercase letters, digits, dots, underscores or hyphens")
    return value

def hash_password(password):
    if not MIN_PASSWORD_LENGTH <= len(password) <= MAX_PASSWORD_LENGTH:
        raise ValueError("Use a password or passphrase of 14-128 characters")
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode(), salt=salt, n=SCRYPT_N, r=8, p=1,
                            maxmem=268435456, dklen=32)
    return f"scrypt${salt.hex()}${digest.hex()}"

def check_password(password, encoded):
    try:
        scheme, salt, expected = encoded.split("$")
        if scheme != "scrypt" or len(password) > 128:
            return False
        digest = hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt), n=SCRYPT_N,
                                r=8, p=1, maxmem=268435456, dklen=32)
        return hmac.compare_digest(digest.hex(), expected)
    except (ValueError, TypeError):
        return False

def token_hash(token):
    return hashlib.sha256(token.encode()).hexdigest()

def create_user(conn, username, password, role, *, actor="local-operator", reset=False):
    from .domain import record_event
    username = normalize_username(username)
    if role not in ROLES:
        raise ValueError("Unknown role")
    encoded = hash_password(password)
    exists = conn.execute("SELECT 1 FROM users WHERE username=?", (username,)).fetchone()
    if exists and not reset:
        raise ValueError("User exists; use reset-user to rotate credentials and sessions")
    if exists:
        conn.execute("UPDATE users SET password_hash=?,role=?,active=1 WHERE username=?",
                     (encoded, role, username))
        conn.execute("DELETE FROM sessions WHERE username=?", (username,))
    else:
        conn.execute("INSERT INTO users(username,password_hash,role) VALUES (?,?,?)",
                     (username, encoded, role))
    # A credential change recovers only this principal's failure window.
    # Shared IP protection and other principals' limits remain intact.
    conn.execute("DELETE FROM login_limits WHERE key=?", ("user:" + token_hash(username),))
    record_event(conn, actor, "user.reset" if exists else "user.create", username, {"role": role})
    return username

def start_session(conn, username, settings):
    now = int(time.time())
    token, csrf = secrets.token_urlsafe(32), secrets.token_urlsafe(32)
    conn.execute("DELETE FROM sessions WHERE expires_at<=? OR last_seen<=?",
                 (now, now - settings.idle_minutes * 60))
    conn.execute("INSERT INTO sessions VALUES (?,?,?,?,?)",
                 (token_hash(token), username, csrf, now + settings.session_hours * 3600, now))
    return token, csrf

def current_session(conn, token, settings):
    if not token or len(token) > 128:
        return None
    row = conn.execute("""SELECT s.*,u.role,u.active FROM sessions s
        JOIN users u ON s.username=u.username WHERE s.token_hash=?""", (token_hash(token),)).fetchone()
    now = int(time.time())
    if not row or not row["active"] or row["expires_at"] <= now or row["last_seen"] <= now-settings.idle_minutes*60:
        return None
    if now - row["last_seen"] >= 60:
        conn.execute("UPDATE sessions SET last_seen=? WHERE token_hash=?", (now, row["token_hash"]))
    return dict(row)

def login_keys(username, ip):
    return [("user:" + token_hash(username), 10), ("ip:" + token_hash(ip), 30)]

def rate_limited(conn, username, ip):
    now = int(time.time())
    for key, limit in login_keys(username, ip):
        row = conn.execute("SELECT * FROM login_limits WHERE key=?", (key,)).fetchone()
        if row and now-row["window_start"] < 900 and row["failures"] >= limit:
            return True
    return False

def failed_login(conn, username, ip):
    now = int(time.time())
    conn.execute("DELETE FROM login_limits WHERE window_start<?", (now-900,))
    for key, _ in login_keys(username, ip):
        conn.execute("""INSERT INTO login_limits VALUES (?,?,1)
            ON CONFLICT(key) DO UPDATE SET failures=failures+1""", (key, now))

