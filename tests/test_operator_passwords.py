"""Account bootstrap and recovery tests use isolated temporary databases only."""
import json
import secrets

import pytest

from harbor_grc import auth, db, domain
from harbor_grc import __main__ as operator
from harbor_grc.config import Settings

GENERATED = "synthetic-" + "g" * 22
ORIGINAL = "fixture-original-passphrase"


@pytest.fixture(scope="session")
def original_hash():
    return auth.hash_password(ORIGINAL)


@pytest.fixture
def account_database(tmp_path, monkeypatch):
    path = tmp_path / "isolated-accounts.db"
    monkeypatch.setenv("GRC_DATABASE", str(path))
    monkeypatch.setenv("GRC_ENV", "local")
    monkeypatch.setenv("GRC_ORIGIN", "http://127.0.0.1:8000")
    db.initialize(path)
    return path


def add_account(path, password_hash, username="admin", role="admin"):
    with db.transaction(path, write=True) as conn:
        conn.execute("INSERT INTO users(username,password_hash,role) VALUES(?,?,?)",
            (username, password_hash, role))


def generated_only(monkeypatch):
    requests = []

    def generate(byte_count):
        assert byte_count == 24
        requests.append(byte_count)
        return GENERATED

    def unexpected_prompt(prompt):
        raise AssertionError("Generated-password mode must not request interactive input")

    monkeypatch.setattr(secrets, "token_urlsafe", generate)
    monkeypatch.setattr(operator.getpass, "getpass", unexpected_prompt)
    return requests


def test_generated_init_commits_hash_only_and_then_displays_local_secret(account_database, monkeypatch, capsys):
    calls = generated_only(monkeypatch)
    real_create = auth.create_user

    def verify_not_printed_before_commit(*args, **kwargs):
        assert GENERATED not in capsys.readouterr().out
        return real_create(*args, **kwargs)

    monkeypatch.setattr(auth, "create_user", verify_not_printed_before_commit)
    assert operator.main(["init", "--generate-password"]) == 0
    output = capsys.readouterr()
    assert output.out.count("Generated passphrase: " + GENERATED) == 1
    assert GENERATED not in output.err
    assert calls == [24]
    with db.transaction(account_database) as conn:
        users = conn.execute("SELECT username,password_hash,role,active FROM users").fetchall()
        assert len(users) == 1
        assert users[0]["username"] == "admin" and users[0]["role"] == "admin" and users[0]["active"] == 1
        assert users[0]["password_hash"].startswith("scrypt$")
        assert auth.check_password(GENERATED, users[0]["password_hash"])
        assert GENERATED not in "\n".join(conn.iterdump())
        assert GENERATED not in json.dumps(domain.list_audit(conn))
        assert domain.list_audit(conn, 1)[0]["action"] == "user.create"
        assert domain.verify_audit(conn)["valid"]


@pytest.mark.parametrize("arguments", [
    ["init", "--generate-password", "literal-password-must-be-rejected"],
    ["init", "--password", "literal-password-must-be-rejected"],
    ["create-user", "analyst", "--role", "analyst", "--generate-password", "literal-password-must-be-rejected"],
])
def test_generation_flag_does_not_accept_a_raw_password_argument(account_database, arguments):
    with pytest.raises(SystemExit) as exc:
        operator.main(arguments)
    assert exc.value.code == 2
    with db.transaction(account_database) as conn:
        assert conn.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0


def test_generate_create_user_keeps_existing_administrator(account_database, original_hash, monkeypatch, capsys):
    add_account(account_database, original_hash)
    generated_only(monkeypatch)
    assert operator.main(["create-user", "analyst", "--role", "analyst", "--generate-password"]) == 0
    assert "Generated passphrase: " + GENERATED in capsys.readouterr().out
    with db.transaction(account_database) as conn:
        original = conn.execute("SELECT password_hash,role FROM users WHERE username='admin'").fetchone()
        created = conn.execute("SELECT password_hash,role FROM users WHERE username='analyst'").fetchone()
        assert original["password_hash"] == original_hash and original["role"] == "admin"
        assert created["role"] == "analyst" and auth.check_password(GENERATED, created["password_hash"])
        assert GENERATED not in json.dumps(domain.list_audit(conn))


def test_generated_reset_clears_only_target_throttle_and_revokes_its_sessions(account_database, original_hash, monkeypatch, capsys):
    add_account(account_database, original_hash)
    add_account(account_database, original_hash, "analyst", "analyst")
    settings = Settings(database=account_database)
    with db.transaction(account_database, write=True) as conn:
        auth.start_session(conn, "admin", settings)
        auth.start_session(conn, "analyst", settings)
        for _ in range(10):
            auth.failed_login(conn, "admin", "127.0.0.1")
        for _ in range(3):
            auth.failed_login(conn, "analyst", "127.0.0.1")
        initial_limits = {row["key"]: dict(row) for row in conn.execute("SELECT * FROM login_limits")}
    generated_only(monkeypatch)
    assert operator.main(["reset-user", "admin", "--role", "admin", "--generate-password"]) == 0
    assert "Generated passphrase: " + GENERATED in capsys.readouterr().out
    with db.transaction(account_database) as conn:
        current_limits = {row["key"]: dict(row) for row in conn.execute("SELECT * FROM login_limits")}
        target_key = "user:" + auth.token_hash("admin")
        assert current_limits == {key: value for key, value in initial_limits.items() if key != target_key}
        assert conn.execute("SELECT COUNT(*) FROM sessions WHERE username='admin'").fetchone()[0] == 0
        assert conn.execute("SELECT COUNT(*) FROM sessions WHERE username='analyst'").fetchone()[0] == 1
        reset = conn.execute("SELECT password_hash,role,active FROM users WHERE username='admin'").fetchone()
        assert reset["role"] == "admin" and reset["active"] == 1
        assert auth.check_password(GENERATED, reset["password_hash"])
        assert not auth.check_password(ORIGINAL, reset["password_hash"])
        assert GENERATED not in "\n".join(conn.iterdump())
        assert domain.verify_audit(conn)["valid"]


def test_generated_create_removes_only_preexisting_target_username_throttle(account_database, original_hash, monkeypatch, capsys):
    add_account(account_database, original_hash)
    with db.transaction(account_database, write=True) as conn:
        auth.failed_login(conn, "new-user", "127.0.0.1")
        auth.failed_login(conn, "another-user", "127.0.0.1")
        initial = {row["key"]: dict(row) for row in conn.execute("SELECT * FROM login_limits")}
    generated_only(monkeypatch)
    operator.main(["create-user", "new-user", "--role", "analyst", "--generate-password"])
    capsys.readouterr()
    with db.transaction(account_database) as conn:
        current = {row["key"]: dict(row) for row in conn.execute("SELECT * FROM login_limits")}
        assert current == {key: value for key, value in initial.items() if key != "user:" + auth.token_hash("new-user")}


def test_failure_after_generation_never_prints_an_uncommitted_secret(account_database, monkeypatch, capsys):
    generated_only(monkeypatch)
    real_create = auth.create_user

    def fail_after_user_write(*args, **kwargs):
        real_create(*args, **kwargs)
        raise RuntimeError("Simulated failure before transaction commit")

    monkeypatch.setattr(auth, "create_user", fail_after_user_write)
    with pytest.raises(RuntimeError, match="before transaction commit"):
        operator.main(["init", "--generate-password"])
    captured = capsys.readouterr()
    assert GENERATED not in captured.out + captured.err
    with db.transaction(account_database) as conn:
        assert conn.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0
        assert domain.verify_audit(conn)["count"] == 0


@pytest.mark.parametrize("length", [14, 128])
def test_prompt_accepts_both_length_boundaries_without_echo(monkeypatch, capsys, length):
    value = "b" * length
    entries = iter([value, value])
    monkeypatch.setattr(operator.getpass, "getpass", lambda prompt: next(entries))
    assert operator.password_prompt() == value
    captured = capsys.readouterr()
    assert value not in captured.out + captured.err


def test_prompt_retries_invalid_length_and_reports_count_without_value(monkeypatch, capsys):
    too_short = "short"
    too_long = "x" * 129
    valid = "valid-prompt-passphrase"
    entries = iter([too_short, too_long, valid, valid])
    monkeypatch.setattr(operator.getpass, "getpass", lambda prompt: next(entries))
    assert operator.password_prompt() == valid
    captured = capsys.readouterr()
    display = captured.out + captured.err
    assert "5" in display and "129" in display
    assert too_short not in display and too_long not in display and valid not in display


def test_prompt_retries_confirmation_mismatch_without_echo(monkeypatch, capsys):
    first = "first-valid-passphrase"
    mismatch = "different-valid-passphrase"
    accepted = "final-valid-passphrase"
    entries = iter([first, mismatch, accepted, accepted])
    monkeypatch.setattr(operator.getpass, "getpass", lambda prompt: next(entries))
    assert operator.password_prompt() == accepted
    captured = capsys.readouterr()
    assert all(value not in captured.out + captured.err for value in (first, mismatch, accepted))


@pytest.mark.parametrize("cancel_type", [EOFError, KeyboardInterrupt])
@pytest.mark.parametrize("at_confirmation", [False, True])
def test_cancelled_entry_never_creates_an_account(account_database, monkeypatch, cancel_type, at_confirmation):
    calls = 0

    def cancel(prompt):
        nonlocal calls
        calls += 1
        if at_confirmation and calls == 1:
            return "first-valid-passphrase"
        raise cancel_type()

    monkeypatch.setattr(operator.getpass, "getpass", cancel)
    try:
        result = operator.main(["init"])
    except (EOFError, KeyboardInterrupt):
        pass
    except SystemExit as exc:
        assert exc.code != 0
    else:
        assert result != 0
    with db.transaction(account_database) as conn:
        assert conn.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0
        assert domain.verify_audit(conn)["count"] == 0


@pytest.mark.parametrize("length", [14, 128])
def test_interactive_init_persists_a_working_boundary_length_passphrase(account_database, monkeypatch, capsys, length):
    chosen = "boundary-" + "z" * (length - len("boundary-"))
    entries = iter([chosen, chosen])
    monkeypatch.setattr(operator.getpass, "getpass", lambda prompt: next(entries))
    assert operator.main(["init"]) == 0
    captured = capsys.readouterr()
    assert chosen not in captured.out + captured.err
    with db.transaction(account_database) as conn:
        row = conn.execute("SELECT password_hash FROM users WHERE username='admin'").fetchone()
        assert row is not None and auth.check_password(chosen, row["password_hash"])
        assert chosen not in "\n".join(conn.iterdump())
        assert domain.verify_audit(conn)["valid"]
