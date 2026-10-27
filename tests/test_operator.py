"""Operator recovery and backup tests."""
import json
import secrets
import sqlite3

import pytest

from harbor_grc import auth, db, domain
from harbor_grc.__main__ import main


@pytest.fixture
def operator_workspace(tmp_path, monkeypatch):
    path = tmp_path / "operator.db"
    monkeypatch.setenv("GRC_DATABASE", str(path))
    monkeypatch.setenv("GRC_ENV", "local")
    monkeypatch.setenv("GRC_ORIGIN", "http://127.0.0.1:8000")
    db.initialize(path)
    return path


def test_backup_restores_records_and_hash_chain(operator_workspace, tmp_path):
    with db.transaction(operator_workspace, write=True) as conn:
        item = domain.create_record(conn, "controls", {"title": "Backup test", "owner": "Security"}, "operator")
    backup = tmp_path / "snapshot.db"
    assert main(["backup", str(backup)]) == 0
    restored = db.connect(backup)
    try:
        assert restored.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
        assert domain.get_record(restored, "controls", item["id"])["title"] == "Backup test"
        assert domain.verify_audit(restored)["valid"]
    finally:
        restored.close()
    with pytest.raises(ValueError, match="new path"):
        main(["backup", str(backup)])


def test_export_excludes_credentials_and_refuses_overwrite(operator_workspace, tmp_path):
    with db.transaction(operator_workspace, write=True) as conn:
        auth.create_user(conn, "admin", secrets.token_urlsafe(24), "admin")
    report = tmp_path / "export.json"
    assert main(["export", str(report)]) == 0
    result = json.loads(report.read_text())
    assert result["audit_verification"]["valid"]
    assert "users" not in result and "sessions" not in result
    with pytest.raises(ValueError, match="exists"):
        main(["export", str(report)])


def test_last_admin_cannot_be_disabled(operator_workspace):
    with db.transaction(operator_workspace, write=True) as conn:
        auth.create_user(conn, "admin", secrets.token_urlsafe(24), "admin")
    with pytest.raises(ValueError, match="last administrator"):
        main(["disable-user", "admin"])


def test_future_schema_is_rejected(operator_workspace):
    with sqlite3.connect(operator_workspace) as conn:
        conn.execute("UPDATE metadata SET value='999' WHERE key='schema_version'")
    with pytest.raises(RuntimeError, match="Unsupported"):
        db.initialize(operator_workspace)

