"""Local operator commands. Passwords are prompted, never command arguments."""
import argparse
import getpass
import json
import os
import secrets
import sqlite3
import sys
from pathlib import Path

from . import auth, db, domain
from .config import Settings


def password_prompt():
    while True:
        password = getpass.getpass("New passphrase (14-128 characters): ")
        if not auth.MIN_PASSWORD_LENGTH <= len(password) <= auth.MAX_PASSWORD_LENGTH:
            print(
                f"Received {len(password)} characters; use "
                f"{auth.MIN_PASSWORD_LENGTH}-{auth.MAX_PASSWORD_LENGTH} characters. Try again.",
                file=sys.stderr,
            )
            continue
        if getpass.getpass("Repeat passphrase: ") != password:
            print("Passphrases do not match. Try again.", file=sys.stderr)
            continue
        return password


def new_password(args):
    return secrets.token_urlsafe(24) if args.generate_password else password_prompt()


def show_generated_password(args, password):
    if args.generate_password:
        print("Generated passphrase: " + password)
        print("Keep it in your password manager. The database stores only a password hash.")


def add_password_option(parser):
    parser.add_argument(
        "--generate-password", action="store_true",
        help="Generate a random passphrase and display it once locally after saving",
    )


def main(argv=None):
    parser = argparse.ArgumentParser(prog="python -m harbor_grc")
    sub = parser.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init", help="Initialize a database and its first administrator")
    init.add_argument("--admin", default="admin")
    add_password_option(init)
    for command in ("create-user", "reset-user"):
        user = sub.add_parser(command, help="Create a user" if command == "create-user" else "Rotate password, role and sessions")
        user.add_argument("username")
        user.add_argument("--role", choices=sorted(auth.ROLES), required=True)
        add_password_option(user)
    disable = sub.add_parser("disable-user", help="Disable a user and revoke all their sessions")
    disable.add_argument("username")
    sub.add_parser("seed-demo", help="Load fictional records into an empty LOCAL workspace")
    sub.add_parser("apply-demo-framework-mappings", help="Add starter references to a tagged fictional demo")
    serve = sub.add_parser("serve", help="Run one application worker")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8000)
    export = sub.add_parser("export", help="Export records, metrics and chain checkpoint; excludes credentials")
    export.add_argument("path", type=Path)
    backup = sub.add_parser("backup", help="Create a consistent SQLite backup; includes credentials, protect it")
    backup.add_argument("path", type=Path)
    sub.add_parser("verify-audit", help="Verify chain continuity and print an external checkpoint")
    args = parser.parse_args(argv)
    settings = Settings.from_env()
    db.initialize(settings.database)
    operator = "local-operator"
    if args.command == "init":
        with db.transaction(settings.database) as conn:
            if conn.execute("SELECT 1 FROM users LIMIT 1").fetchone():
                raise ValueError("Already initialized; use create-user or reset-user")
        password = new_password(args)
        with db.transaction(settings.database, write=True) as conn:
            if conn.execute("SELECT 1 FROM users LIMIT 1").fetchone():
                raise ValueError("Already initialized")
            username = auth.create_user(conn, args.admin, password, "admin", actor=operator)
        print("Administrator created. Start with: python -m harbor_grc serve")
        print(f"Sign in at {settings.origin} as {username}")
        show_generated_password(args, password)
    elif args.command in {"create-user", "reset-user"}:
        password = new_password(args)
        with db.transaction(settings.database, write=True) as conn:
            username = auth.normalize_username(args.username)
            if args.command == "reset-user" and not conn.execute(
                    "SELECT 1 FROM users WHERE username=?", (username,)).fetchone():
                raise ValueError("User does not exist; use create-user")
            # Keep at least one active administrator.
            target = conn.execute("SELECT role,active FROM users WHERE username=?", (username,)).fetchone()
            if target and target["role"] == "admin" and target["active"] and args.role != "admin":
                count = conn.execute("SELECT COUNT(*) FROM users WHERE role='admin' AND active=1").fetchone()[0]
                if count <= 1:
                    raise ValueError("Create another administrator before changing the last administrator's role")
            auth.create_user(conn, username, password, args.role, actor=operator,
                             reset=args.command == "reset-user")
        print("User saved; existing sessions revoked for password resets.")
        print(f"Sign in at {settings.origin} as {username}")
        show_generated_password(args, password)
    elif args.command == "disable-user":
        username = auth.normalize_username(args.username)
        with db.transaction(settings.database, write=True) as conn:
            target = conn.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
            if not target:
                raise ValueError("User not found")
            if target["role"] == "admin" and target["active"] and conn.execute(
                    "SELECT COUNT(*) FROM users WHERE role='admin' AND active=1").fetchone()[0] <= 1:
                raise ValueError("Cannot disable the last administrator")
            conn.execute("UPDATE users SET active=0 WHERE username=?", (username,))
            conn.execute("DELETE FROM sessions WHERE username=?", (username,))
            domain.record_event(conn, operator, "user.disabled", username, {})
        print("User disabled and sessions revoked.")
    elif args.command == "seed-demo":
        if settings.production:
            raise ValueError("Demo seeding is disabled in production")
        from .seed import seed_demo
        with db.transaction(settings.database, write=True) as conn:
            existing = conn.execute("SELECT 1 FROM records LIMIT 1").fetchone()
            if existing:
                raise ValueError("Demo seeding requires an empty records database; choose a separate GRC_DATABASE")
            result = seed_demo(conn, operator)
            conn.execute("INSERT OR REPLACE INTO metadata VALUES ('demo','true')")
        print(json.dumps(result, indent=2))
    elif args.command == "apply-demo-framework-mappings":
        if settings.production:
            raise ValueError("Demo framework mapping is disabled in production")
        from .frameworks import apply_demo_mappings
        with db.transaction(settings.database, write=True) as conn:
            result = apply_demo_mappings(conn, operator)
        print(json.dumps(result, indent=2))
    elif args.command == "serve":
        if not settings.production and args.host not in {"127.0.0.1", "localhost", "::1"}:
            raise ValueError("Local mode listens on loopback only")
        import uvicorn
        from .app import create_app
        uvicorn.run(create_app(settings), host=args.host, port=args.port, workers=1,
                    proxy_headers=False, limit_concurrency=32, timeout_keep_alive=5,
                    access_log=False)
    elif args.command == "export":
        if args.path.exists():
            raise ValueError("Export destination already exists")
        args.path.parent.mkdir(parents=True, exist_ok=True)
        with db.transaction(settings.database, write=True) as conn:
            domain.record_event(conn, operator, "report.exported", "workspace", {})
            result = domain.report(conn)
            result["workspace"] = {"name": "Harbor GRC", "demo": db.demo_enabled(conn)}
            with args.path.open("x", encoding="utf-8") as output:
                json.dump(result, output, indent=2, ensure_ascii=False)
        print(f"Report saved: {args.path}")
    elif args.command == "backup":
        if args.path.resolve() == settings.database.resolve():
            raise ValueError("Backup destination must be a new path")
        args.path.parent.mkdir(parents=True, exist_ok=True)
        # Reserve atomically with restrictive permissions before writing credentials.
        # The destination directory must itself be trusted (not shared writable).
        try:
            reserved = os.open(args.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        except FileExistsError as exc:
            raise ValueError("Backup destination must be a new path") from exc
        os.close(reserved)
        source = destination = None
        complete = False
        try:
            source = db.connect(settings.database)
            destination = sqlite3.connect(str(args.path))
            # The SQLite backup API includes committed WAL pages consistently.
            source.backup(destination)
            if destination.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                raise ValueError("Backup failed integrity check")
            complete = True
        finally:
            if destination is not None:
                destination.close()
            if source is not None:
                source.close()
            if not complete:
                args.path.unlink(missing_ok=True)
        print(f"Sensitive database backup saved: {args.path}")
    elif args.command == "verify-audit":
        with db.transaction(settings.database) as conn:
            result = domain.verify_audit(conn)
        print(json.dumps(result, indent=2))
        return 0 if result["valid"] else 1
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (EOFError, KeyboardInterrupt):
        print("Cancelled.", file=sys.stderr)
        raise SystemExit(1)
    except (ValueError, sqlite3.Error) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1)

