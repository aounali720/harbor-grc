"""Workflow, integrity, expiry and concurrency regression tests for the GRC core."""
import json
import sqlite3
from datetime import timedelta

import pytest
from pydantic import ValidationError

from harbor_grc import domain
from harbor_grc.schemas import SCHEMAS
from harbor_grc.seed import seed_demo


@pytest.fixture
def conn():
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    domain.init_schema(connection)
    connection.commit()
    yield connection
    connection.close()


def data(kind, record, **changes):
    result = {key: record[key] for key in SCHEMAS[kind].model_fields}
    result.update(changes)
    return result


def create_control(conn, **changes):
    return domain.create_record(conn, "controls", {
        "title": "Privileged access reviews", "owner": "Identity lead",
        "status": "implemented", "test_procedure": "Reconcile every privileged grant with an approved role.",
        **changes,
    }, "collector")


def evidence_for(conn, control, **changes):
    today = domain.today()
    return domain.create_record(conn, "evidence", {
        "title": "Access review sample", "owner": "Identity lead", "control_id": control["id"],
        "uri": "https://evidence.company.example/review.json", "sha256": "a" * 64,
        "collected_on": today.isoformat(), "expires_on": (today + timedelta(days=30)).isoformat(),
        **changes,
    }, "collector")


def approve(conn, evidence):
    return domain.update_record(conn, "evidence", evidence["id"], data("evidence", evidence,
        status="approved", review_notes="Scope, sample and exceptions independently examined.",
        reviewed_by="spoofed"), evidence["version"], "reviewer")


def test_independent_evidence_approval_and_effectiveness(conn):
    control = create_control(conn)
    evidence = evidence_for(conn, control)
    effective = data("controls", control, status="effective")
    with pytest.raises(ValueError, match="approved evidence"):
        domain.update_record(conn, "controls", control["id"], effective, 1, "reviewer")
    with pytest.raises(ValueError, match="other than its creator"):
        domain.update_record(conn, "evidence", evidence["id"], data("evidence", evidence,
            status="approved", review_notes="Self review"), 1, "collector")
    reviewed = approve(conn, evidence)
    assert reviewed["reviewed_by"] == "reviewer"
    updated = domain.update_record(conn, "controls", control["id"], effective, 1, "reviewer")
    assert updated["version"] == 2
    assert domain.dashboard(conn)["evidence_backed_effective_controls"] == 1
    assert domain.verify_audit(conn)["valid"]


def test_evidence_content_cannot_change_during_approval(conn):
    control = create_control(conn)
    evidence = evidence_for(conn, control)
    with pytest.raises(ValueError, match="pending"):
        domain.update_record(conn, "evidence", evidence["id"], data("evidence", evidence,
            status="approved", uri="https://evidence.company.example/different.json",
            review_notes="Review"), 1, "reviewer")
    approved = approve(conn, evidence)
    revised = domain.update_record(conn, "evidence", approved["id"], data("evidence", approved,
        status="pending", sha256="b" * 64), approved["version"], "collector")
    assert revised["reviewed_by"] == ""
    assert revised["status"] == "pending"


def test_effectiveness_recomputed_after_expiry_and_control_cadence(conn, monkeypatch):
    control = create_control(conn, frequency_days=7)
    evidence = approve(conn, evidence_for(conn, control))
    domain.update_record(conn, "controls", control["id"], data("controls", control,
        status="effective"), 1, "reviewer")
    next_week = domain.today() + timedelta(days=8)
    monkeypatch.setattr(domain, "today", lambda: next_week)
    dashboard = domain.dashboard(conn)
    assert dashboard["control_coverage_percent"] == 0
    assert dashboard["stale_effective_control_ids"] == [control["id"]]
    # Declared expiry is still in the future, but the scheduled test is stale.
    assert evidence["expires_on"] > next_week.isoformat()


def test_expired_evidence_cannot_be_approved(conn):
    control = create_control(conn)
    evidence = evidence_for(conn, control,
        collected_on=(domain.today() - timedelta(days=20)).isoformat(),
        expires_on=(domain.today() - timedelta(days=1)).isoformat())
    with pytest.raises(ValueError, match="Expired"):
        approve(conn, evidence)


def test_finding_closure_requires_fresh_evidence_for_same_control(conn, monkeypatch):
    first, second = create_control(conn), create_control(conn, title="Backup restore")
    evidence = approve(conn, evidence_for(conn, first))
    payload = {"title": "Missing review", "owner": "Identity lead", "status": "closed",
               "control_id": second["id"], "evidence_id": evidence["id"], "remediation": "Retested the sample"}
    with pytest.raises(ValueError, match="belong"):
        domain.create_record(conn, "findings", payload, "reviewer")
    payload["control_id"] = first["id"]
    finding = domain.create_record(conn, "findings", payload, "reviewer")
    future = domain.today() + timedelta(days=31)
    monkeypatch.setattr(domain, "today", lambda: future)
    assert domain.dashboard(conn)["stale_closed_finding_ids"] == [finding["id"]]
    with pytest.raises(ValueError, match="current approved"):
        domain.update_record(conn, "findings", finding["id"], data("findings", finding), 1, "reviewer")


def test_acceptance_is_independent_actor_stamped_and_time_bounded(conn):
    risk = domain.create_record(conn, "risks", {"title": "Supplier interruption", "owner": "Risk lead"}, "author")
    accepting = data("risks", risk, status="accepted", treatment="accept",
        acceptance_rationale="Business owner accepts the bounded exposure", acceptance_approver="spoofed",
        acceptance_expires=(domain.today() + timedelta(days=30)).isoformat())
    with pytest.raises(ValueError, match="other than"):
        domain.update_record(conn, "risks", risk["id"], accepting, 1, "author")
    bad = dict(accepting, acceptance_expires=domain.today().isoformat())
    with pytest.raises(ValueError, match="future expiry"):
        domain.update_record(conn, "risks", risk["id"], bad, 1, "approver")
    accepted = domain.update_record(conn, "risks", risk["id"], accepting, 1, "approver")
    assert accepted["acceptance_approver"] == "approver"


def test_risk_accepted_finding_needs_current_accepted_risk(conn, monkeypatch):
    risk = domain.create_record(conn, "risks", {"title": "Low impact outage", "owner": "Risk lead"}, "author")
    finding = {"title": "Outage exception", "owner": "Risk lead", "risk_id": risk["id"], "status": "risk_accepted"}
    with pytest.raises(ValueError, match="currently accepted"):
        domain.create_record(conn, "findings", finding, "approver")
    expires = domain.today() + timedelta(days=30)
    domain.update_record(conn, "risks", risk["id"], data("risks", risk, status="accepted", treatment="accept",
        acceptance_rationale="Tolerance approved", acceptance_expires=expires.isoformat()), 1, "approver")
    domain.create_record(conn, "findings", finding, "approver")
    monkeypatch.setattr(domain, "today", lambda: expires)
    assert risk["id"] in domain.dashboard(conn)["expired_acceptance_ids"]
    with pytest.raises(ValueError, match="currently accepted"):
        domain.create_record(conn, "findings", dict(finding, title="New exception"), "approver")


def test_residual_risk_is_explicit_and_never_control_count_discounted(conn):
    control = create_control(conn)
    risk = domain.create_record(conn, "risks", {"title": "Data disclosure", "owner": "Cloud lead",
        "likelihood": 5, "impact": 5, "control_ids": [control["id"]]}, "author")
    report = domain.report(conn)
    assert report["registers"]["risks"][0]["residual_score"] is None
    assert report["registers"]["risks"][0]["inherent_score"] == 25
    with pytest.raises(ValidationError, match="requires rationale"):
        domain.update_record(conn, "risks", risk["id"], data("risks", risk,
            residual_likelihood=2, residual_impact=5), 1, "reviewer")
    reviewed = domain.update_record(conn, "risks", risk["id"], data("risks", risk,
        residual_likelihood=2, residual_impact=5, residual_rationale="Sample supported reduced likelihood; impact remains unchanged",
        residual_review_date=domain.today().isoformat(), residual_reviewed_by="spoofed"), 1, "reviewer")
    assert reviewed["residual_reviewed_by"] == "reviewer"


def test_optimistic_conflict_does_not_overwrite_or_append_audit(conn):
    control = create_control(conn)
    updated = domain.update_record(conn, "controls", control["id"], data("controls", control, title="New title"), 1, "reviewer")
    count = domain.verify_audit(conn)["count"]
    with pytest.raises(domain.ConflictError):
        domain.update_record(conn, "controls", control["id"], data("controls", control, title="Stale title"), 1, "another")
    assert domain.get_record(conn, "controls", control["id"])["title"] == "New title"
    assert updated["version"] == 2
    assert domain.verify_audit(conn)["count"] == count


def test_invalid_reference_and_duplicate_source_cannot_enter_register(conn):
    with pytest.raises(ValueError, match="does not exist"):
        domain.create_record(conn, "risks", {"title": "Risk", "owner": "Owner", "control_ids": ["CTL-missing"]}, "author")
    payload = {"title": "Cloud finding", "owner": "Cloud lead", "source_key": "aws:test:synthetic-1"}
    domain.create_record(conn, "findings", payload, "importer")
    with pytest.raises(domain.ConflictError, match="source key"):
        domain.create_record(conn, "findings", payload, "importer")


def test_transaction_rollback_removes_record_and_audit_together(conn):
    with pytest.raises(RuntimeError):
        with conn:
            create_control(conn)
            raise RuntimeError("Simulated failure after mutation")
    assert domain.list_records(conn, "controls") == []
    assert domain.verify_audit(conn)["count"] == 0


@pytest.mark.parametrize("mutation", ["details", "actor", "hash", "previous_hash"])
def test_audit_detects_field_tampering(conn, mutation):
    create_control(conn)
    conn.execute(f"UPDATE audit SET {mutation}=? WHERE seq=1", ('{"changed":true}' if mutation == "details" else "tampered",))
    verification = domain.verify_audit(conn)
    assert verification["valid"] is False
    assert verification["failed_sequence"] == 1


def test_audit_interior_deletion_detected(conn):
    create_control(conn)
    create_control(conn, title="Second")
    create_control(conn, title="Third")
    conn.execute("DELETE FROM audit WHERE seq=2")
    assert domain.verify_audit(conn)["valid"] is False


@pytest.mark.parametrize("criticality,sensitivity,access,tier", [
    ("low", "public", "privileged", "tier_1"),
    ("critical", "internal", "none", "tier_1"),
    ("medium", "restricted", "user", "tier_1"),
    ("high", "internal", "none", "tier_2"),
    ("low", "confidential", "user", "tier_2"),
    ("medium", "internal", "none", "tier_3"),
])
def test_vendor_tiering_prioritizes_impact_over_questionnaire_score(criticality, sensitivity, access, tier):
    assert domain.vendor_tier({"criticality": criticality, "data_sensitivity": sensitivity,
        "access_level": access, "questionnaire_score": 100}) == tier


@pytest.mark.parametrize("uri", ["http://evidence.company.example/test", "https://user:password@evidence.company.example/test", "https://evidence.company.example/test?token=secret"])
def test_evidence_reference_rejects_insecure_or_secret_bearing_url(conn, uri):
    with pytest.raises(ValidationError):
        evidence_for(conn, create_control(conn), uri=uri)


@pytest.mark.parametrize("likelihood", [0, 6, True, 3.5, "3"])
def test_risk_score_rejects_out_of_range_and_coerced_values(conn, likelihood):
    with pytest.raises(ValidationError):
        domain.create_record(conn, "risks", {"title": "Risk", "owner": "Owner", "likelihood": likelihood}, "author")


def test_empty_coverage_has_no_false_positive(conn):
    assert domain.dashboard(conn)["control_coverage_percent"] is None
    create_control(conn, status="not_applicable", description="No in-scope privileged systems")
    assert domain.dashboard(conn)["control_coverage_percent"] is None


def test_seed_is_coherent_synthetic_idempotent_and_auditable(conn):
    result = seed_demo(conn, "operator")
    assert result["counts"] == {"risks": 10, "controls": 12, "vendors": 5, "assets": 8, "evidence": 8, "findings": 7}
    assert result["dashboard"]["evidence_backed_effective_controls"] == 6
    assert seed_demo(conn, "operator")["seeded"] is False
    assert domain.verify_audit(conn)["valid"]
    assert domain.list_audit(conn)[0]["action"] == "demo.seeded"
    snapshot = domain.report(conn)
    assert snapshot["schema_version"] == 1
    assert len(snapshot["registers"]["vendors"]) == 5
    assert all(".example/" in item["uri"] for item in snapshot["registers"]["evidence"])
    assert json.loads(json.dumps(snapshot))["dashboard"]["open_risks"] == 10


def test_evidence_independence_follows_current_submitter(conn):
    control = create_control(conn)
    approved = approve(conn, evidence_for(conn, control))
    changed = domain.update_record(conn, "evidence", approved["id"], data("evidence", approved,
        status="pending", sha256="c" * 64, submitted_by="spoofed"), approved["version"], "another-submitter")
    assert changed["submitted_by"] == "another-submitter"
    with pytest.raises(ValueError, match="current submitter"):
        domain.update_record(conn, "evidence", changed["id"], data("evidence", changed,
            status="approved", review_notes="Trying to approve my revised artifact"), changed["version"], "another-submitter")
    final = domain.update_record(conn, "evidence", changed["id"], data("evidence", changed,
        status="approved", review_notes="Independent verification of the resubmitted artifact"), changed["version"], "third-reviewer")
    assert final["reviewed_by"] == "third-reviewer"
