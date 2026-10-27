"""Regressions discovered by the independent implementation review."""
import copy
import hashlib
import json
import os
import sqlite3
from datetime import datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

from harbor_grc import auth, db, domain
from harbor_grc import __main__ as operator
from harbor_grc.app import create_app
from harbor_grc.cloud import import_findings
from harbor_grc.config import Settings


@pytest.fixture
def cloud_conn():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    domain.init_schema(conn)
    yield conn
    conn.close()


def observation(updated="2026-01-01T00:00:00Z"):
    return {"Findings": [{
        "Id": "synthetic-recurrent-storage-check",
        "ProductArn": "arn:aws:securityhub:us-east-1:000000000000:product/example/check",
        "UpdatedAt": updated, "Title": "Public storage configuration failed",
        "Description": "Synthetic repeated failure", "Compliance": {"Status": "FAILED"},
        "Severity": {"Label": "HIGH"},
    }]}


def payload(kind, record, **changes):
    result = {key: record[key] for key in domain.SCHEMAS[kind].model_fields}
    result.update(changes)
    return result


def close_cloud_finding(conn):
    import_findings(conn, observation(), "importer")
    finding = domain.list_records(conn, "findings")[0]
    control = domain.create_record(conn, "controls", {"title": "Storage access test", "owner": "Cloud lead"}, "collector")
    today = domain.today()
    evidence = domain.create_record(conn, "evidence", {
        "title": "Storage test result", "owner": "Cloud lead", "control_id": control["id"],
        "uri": "https://evidence.company.example/test.json", "sha256": "a" * 64,
        "collected_on": today.isoformat(), "expires_on": (today + timedelta(days=30)).isoformat(),
    }, "collector")
    approved = domain.update_record(conn, "evidence", evidence["id"], payload("evidence", evidence,
        status="approved", review_notes="Independent review of configuration and unauthorized request test"), 1, "reviewer")
    return domain.update_record(conn, "findings", finding["id"], payload("findings", finding,
        status="closed", control_id=control["id"], evidence_id=approved["id"], owner="Named engineer",
        remediation="Retested the corrected policy; independent reviewer confirmed the sample"), 1, "reviewer")


def test_newer_recurring_failure_reopens_even_when_words_are_unchanged(cloud_conn):
    closed = close_cloud_finding(cloud_conn)
    result = import_findings(cloud_conn, observation("2026-01-02T00:00:00Z"), "importer")
    current = domain.get_record(cloud_conn, "findings", closed["id"])
    assert result == {"created": 0, "updated": 1, "skipped": 0}
    assert current["status"] == "open"
    assert current["owner"] == "Named engineer"
    assert current["remediation"] == closed["remediation"]
    assert current["control_id"] == closed["control_id"]
    assert current["source_updated_at"].startswith("2026-01-02T00:00:00")


@pytest.mark.parametrize("updated", ["2026-01-01T00:00:00Z", "2025-12-31T12:00:00-05:00"])
def test_stale_or_equal_replay_cannot_reopen_or_overwrite_manual_closure(cloud_conn, updated):
    closed = close_cloud_finding(cloud_conn)
    incoming = observation(updated)
    incoming["Findings"][0]["Severity"]["Label"] = "CRITICAL"
    result = import_findings(cloud_conn, incoming, "importer")
    current = domain.get_record(cloud_conn, "findings", closed["id"])
    assert result["skipped"] == 1
    assert current["status"] == "closed" and current["severity"] == "high"
    assert current["version"] == closed["version"]


@pytest.mark.parametrize("timestamp", [None, "2026-01-01T00:00:00"])
def test_asff_source_timestamp_is_required_and_timezone_aware(cloud_conn, timestamp):
    incoming = observation()
    if timestamp is None:
        del incoming["Findings"][0]["UpdatedAt"]
    else:
        incoming["Findings"][0]["UpdatedAt"] = timestamp
    with pytest.raises(ValidationError):
        import_findings(cloud_conn, incoming, "importer")
    assert domain.list_records(cloud_conn, "findings") == []


def test_future_observation_rejects_entire_batch_before_mutation(cloud_conn):
    incoming = observation()
    future = copy.deepcopy(incoming["Findings"][0])
    future["Id"] = "future"
    future["UpdatedAt"] = (datetime.now(timezone.utc) + timedelta(minutes=6)).isoformat()
    incoming["Findings"].append(future)
    with pytest.raises(ValidationError, match="five minutes"):
        import_findings(cloud_conn, incoming, "importer")
    assert domain.list_records(cloud_conn, "findings") == []


def test_manual_source_link_uses_local_edit_time_until_source_timestamp_known(cloud_conn):
    incoming = observation()
    item = incoming["Findings"][0]
    source = "asff:" + hashlib.sha256((item["ProductArn"] + "\0" + item["Id"]).encode()).hexdigest()
    manual = domain.create_record(cloud_conn, "findings", {"title": "Manual observation", "owner": "Cloud lead", "source_key": source}, "analyst")
    assert import_findings(cloud_conn, incoming, "importer")["skipped"] == 1
    # A later source update is allowed; the five-minute guard permits clock skew.
    later = datetime.now(timezone.utc) + timedelta(seconds=1)
    incoming["Findings"][0]["UpdatedAt"] = later.isoformat()
    assert import_findings(cloud_conn, incoming, "importer")["updated"] == 1
    assert domain.get_record(cloud_conn, "findings", manual["id"])["source_updated_at"] is not None


def test_timezone_offsets_are_compared_as_instants(cloud_conn):
    import_findings(cloud_conn, observation("2026-01-01T05:00:00+05:00"), "importer")
    assert import_findings(cloud_conn, observation("2026-01-01T00:00:00Z"), "importer")["skipped"] == 1


def test_old_json_records_gain_optional_source_timestamp_default(cloud_conn):
    finding = domain.create_record(cloud_conn, "findings", {"title": "Legacy record", "owner": "Cloud lead"}, "analyst")
    stored = json.loads(cloud_conn.execute("SELECT data FROM records WHERE id=?", (finding["id"],)).fetchone()[0])
    stored.pop("source_updated_at")
    cloud_conn.execute("UPDATE records SET data=? WHERE id=?", (json.dumps(stored), finding["id"]))
    assert domain.get_record(cloud_conn, "findings", finding["id"])["source_updated_at"] is None


@pytest.fixture
def operator_database(tmp_path, monkeypatch):
    path = tmp_path / "workspace.db"
    monkeypatch.setenv("GRC_DATABASE", str(path))
    monkeypatch.setenv("GRC_ENV", "local")
    monkeypatch.setenv("GRC_ORIGIN", "http://127.0.0.1:8000")
    db.initialize(path)
    return path


def test_backup_destination_is_exclusively_reserved_before_sensitive_writes(operator_database, tmp_path, monkeypatch):
    target = tmp_path / "sensitive-backup.db"
    actual_open = os.open
    reservations = []

    def checked_open(path, flags, mode=0o777):
        if str(path) == str(target):
            assert flags & os.O_EXCL and flags & os.O_CREAT
            assert mode == 0o600
            reservations.append(path)
        return actual_open(path, flags, mode)

    monkeypatch.setattr(operator.os, "open", checked_open)
    assert operator.main(["backup", str(target)]) == 0
    assert reservations == [target]
    with sqlite3.connect(target) as restored:
        assert restored.execute("PRAGMA integrity_check").fetchone()[0] == "ok"


def test_backup_racing_destination_is_not_overwritten(operator_database, tmp_path, monkeypatch):
    target = tmp_path / "racing-backup.db"
    actual_open = os.open

    def simulate_race(path, flags, mode=0o777):
        if str(path) == str(target):
            target.write_bytes(b"another operator's backup")
        return actual_open(path, flags, mode)

    monkeypatch.setattr(operator.os, "open", simulate_race)
    with pytest.raises(ValueError, match="new path"):
        operator.main(["backup", str(target)])
    assert target.read_bytes() == b"another operator's backup"


def test_failed_backup_removes_only_its_partial_destination(operator_database, tmp_path, monkeypatch):
    target = tmp_path / "partial.db"
    actual_connect = sqlite3.connect

    def fail_destination(path, *args, **kwargs):
        if str(path) == str(target):
            raise sqlite3.OperationalError("Simulated backup destination failure")
        return actual_connect(path, *args, **kwargs)

    monkeypatch.setattr(operator.sqlite3, "connect", fail_destination)
    with pytest.raises(sqlite3.OperationalError, match="Simulated"):
        operator.main(["backup", str(target)])
    assert not target.exists()
    assert operator_database.exists()


@pytest.mark.parametrize("missing", ["records", "audit", "users", "sessions", "login_limits", "metadata-row", "future-schema"])
def test_readiness_rejects_missing_or_incompatible_schema(tmp_path, monkeypatch, missing):
    monkeypatch.setattr(auth, "hash_password", lambda value: "unused-in-readiness-test")
    settings = Settings(database=tmp_path / "readiness.db", origin="http://testserver")
    app = create_app(settings)
    ready = next(route.endpoint for route in app.routes if getattr(route, "path", "") == "/health/ready")
    assert ready() == {"status": "ready"}
    with db.transaction(settings.database, write=True) as conn:
        if missing == "metadata-row":
            conn.execute("DELETE FROM metadata WHERE key='schema_version'")
        elif missing == "future-schema":
            conn.execute("UPDATE metadata SET value='999' WHERE key='schema_version'")
        else:
            conn.execute(f"DROP TABLE {missing}")
    assert ready().status_code == 503


def test_newer_failure_reopens_an_accepted_finding_without_erasing_decision_link(cloud_conn):
    import_findings(cloud_conn, observation(), "importer")
    finding = domain.list_records(cloud_conn, "findings")[0]
    risk = domain.create_record(cloud_conn, "risks", {"title": "Bounded interruption", "owner": "Risk lead"}, "author")
    accepted = domain.update_record(cloud_conn, "risks", risk["id"], payload("risks", risk,
        status="accepted", treatment="accept", acceptance_rationale="Time-bounded business tolerance",
        acceptance_expires=(domain.today() + timedelta(days=30)).isoformat()), 1, "approver")
    domain.update_record(cloud_conn, "findings", finding["id"], payload("findings", finding,
        status="risk_accepted", risk_id=accepted["id"]), 1, "approver")
    assert import_findings(cloud_conn, observation("2026-01-02T00:00:00Z"), "importer")["updated"] == 1
    current = domain.get_record(cloud_conn, "findings", finding["id"])
    assert current["status"] == "open" and current["risk_id"] == accepted["id"]
