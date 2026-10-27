"""Scope, reference integrity, and evidence semantics for the partial catalog."""
import sqlite3
from datetime import date, datetime, timedelta, timezone
from urllib.parse import urlsplit

import pytest

from harbor_grc import domain, frameworks
from harbor_grc.seed import seed_demo


@pytest.fixture
def conn():
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    domain.init_schema(connection)
    connection.execute("CREATE TABLE metadata (key TEXT PRIMARY KEY,value TEXT NOT NULL)")
    connection.commit()
    yield connection
    connection.close()


def payload(kind, record, **changes):
    value = {key: record[key] for key in domain.SCHEMAS[kind].model_fields}
    value.update(changes)
    return value


def tagged_demo(conn):
    conn.execute("INSERT OR REPLACE INTO metadata VALUES ('demo','true')")


def control(conn, **changes):
    return domain.create_record(conn, "controls", {
        "title": "Access review", "owner": "Security", "status": "implemented",
        "test_procedure": "Inspect approved role grants and a complete account population",
        **changes,
    }, "collector")


def effective_control(conn, **changes):
    item = control(conn, **changes)
    day = domain.today()
    evidence = domain.create_record(conn, "evidence", {
        "title": "Independent test artifact", "owner": "Security", "control_id": item["id"],
        "uri": "https://evidence.company.example/test.json", "sha256": "a" * 64,
        "collected_on": day.isoformat(), "expires_on": (day + timedelta(days=90)).isoformat(),
    }, "collector")
    evidence = domain.update_record(conn, "evidence", evidence["id"], payload("evidence", evidence,
        status="approved", review_notes="Scope and sample independently checked"), 1, "reviewer")
    item = domain.update_record(conn, "controls", item["id"], payload("controls", item,
        status="effective"), 1, "reviewer")
    return item, evidence


def index(result):
    return {item["framework_id"]: item for item in result["items"]}


def test_catalog_is_versioned_scoped_and_uses_primary_sources():
    value = frameworks.catalog()
    assert date.fromisoformat(value["checked_on"]) <= datetime.now(timezone.utc).date()
    assert value["catalog_version"]
    ids = [item["id"] for item in value["items"]]
    assert len(ids) == len(set(ids))
    assert {
        "nist-csf-2.0", "nist-sp-800-37-r2", "nist-sp-800-53-r5", "nist-sp-800-53a-r5",
        "nist-sp-800-53b", "nist-sp-800-30-r1", "nist-sp-800-161-r1", "nist-sp-800-171-r3",
        "nist-sp-800-61-r3", "iso-iec-27001-2022", "iso-iec-27002-2022", "iso-iec-27005-2022",
    } <= set(ids)
    assert value["limitations"] and "not an exhaustive" in value["scope"]
    for item in value["items"]:
        assert {"id", "name", "edition", "publisher", "type", "summary", "applicability", "source_url", "scope"} <= item.keys()
        for source in [item["source_url"], *item.get("related_sources", [])]:
            parsed = urlsplit(source)
            assert parsed.scheme == "https"
            assert parsed.hostname in {"www.nist.gov", "csrc.nist.gov", "www.iso.org"}
    entries = {item["id"]: item for item in value["items"]}
    assert "baselines unchanged" in entries["nist-sp-800-53b"]["edition"]
    assert "Amendment 1:2024" in entries["iso-iec-27001-2022"]["edition"]
    assert "CUI" in entries["nist-sp-800-171-r3"]["applicability"]
    assert "not itself a certification" in entries["iso-iec-27002-2022"]["summary"]


def test_catalog_and_mapping_callers_cannot_mutate_shared_data():
    first = frameworks.catalog()
    original_count = len(first["items"])
    first["items"].clear()
    assert len(frameworks.catalog()["items"]) == original_count
    mappings = frameworks.mappings()
    mappings["items"][0]["links"].clear()
    assert frameworks.mappings()["items"][0]["links"]


def test_mapping_links_are_partial_resolvable_and_fit_the_control_schema():
    publications = {item["id"]: item for item in frameworks.catalog()["items"]}
    pack = frameworks.mappings()
    assert {item["control_key"] for item in pack["items"]} == {f"CTL-{number:02d}" for number in range(1, 13)}
    assert pack["checked_on"] == "2026-10-27"
    assert "not satisfaction" in pack["scope"]
    for item in pack["items"]:
        references = []
        for link in item["links"]:
            assert link["framework_id"] in publications
            assert link["relationship"] == "partial"
            assert link["topic"] and link["rationale"] and link["source_url"]
            assert link["source_url"] == publications[link["framework_id"]]["source_url"]
            assert len(link["reference"]) <= 80
            references.append(link["reference"])
        assert len(references) == len(set(references))
        domain.SCHEMAS["controls"].model_validate({"title": item["title"], "owner": "Security", "framework_refs": references})
    assert frameworks.references_for_control("CTL-01")[0] == "NIST CSF 2.0 PR.AA-05"
    assert frameworks.references_for_control("CTL-01 extra") == []
    assert frameworks.references_for_control("CTL-99") == []


def test_coverage_includes_reference_only_publications_without_false_percentages(conn):
    result = frameworks.coverage(conn)
    assert result["local_control_count"] == 0
    assert len(result["items"]) == len(frameworks.catalog()["items"])
    assert all(item["mapped_controls"] == item["evidence_backed_controls"] == 0 for item in result["items"])
    assert result["unknown_references"] == []
    assert "do not measure full-framework" in result["scope"]
    assert all("percent" not in key for item in result["items"] for key in item)


def test_coverage_uses_exact_explicit_references_and_never_control_titles(conn):
    control(conn, title="CTL-01 Quarterly privileged access review")
    malformed = control(conn, framework_refs=["NIST CSF 2.0 pr.aa-05", "NIST SP 800-53 Rev. 5 SC-7"])
    result = frameworks.coverage(conn)
    assert all(item["mapped_controls"] == 0 for item in result["items"])
    assert {item["reference"] for item in result["unknown_references"]} == set(malformed["framework_refs"])
    assert all(item["control_id"] == malformed["id"] for item in result["unknown_references"])


def test_multiple_links_to_one_framework_count_the_local_control_once(conn):
    refs = frameworks.references_for_control("CTL-01")
    control(conn, framework_refs=refs + refs)
    result = index(frameworks.coverage(conn))
    for framework_id in ("nist-csf-2.0", "nist-sp-800-53-r5", "iso-iec-27001-2022", "iso-iec-27002-2022"):
        assert result[framework_id]["mapped_controls"] == 1
        assert result[framework_id]["evidence_backed_controls"] == 0
    assert result["nist-sp-800-171-r3"]["mapped_controls"] == 0


def test_reference_and_effective_label_alone_never_prove_evidence_coverage(conn, monkeypatch):
    refs = frameworks.references_for_control("CTL-01")
    item, _ = effective_control(conn, framework_refs=refs, frequency_days=7)
    result = index(frameworks.coverage(conn))
    assert result["nist-sp-800-53-r5"]["evidence_backed_controls"] == 1
    later = domain.today() + timedelta(days=8)
    monkeypatch.setattr(domain, "today", lambda: later)
    result = index(frameworks.coverage(conn))
    assert result["nist-sp-800-53-r5"]["mapped_controls"] == 1
    assert result["nist-sp-800-53-r5"]["evidence_backed_controls"] == 0
    assert domain.get_record(conn, "controls", item["id"])["status"] == "effective"


def test_rejected_evidence_removes_evidence_backed_coverage(conn):
    _, evidence = effective_control(conn, framework_refs=frameworks.references_for_control("CTL-01"))
    domain.update_record(conn, "evidence", evidence["id"], payload("evidence", evidence,
        status="rejected", review_notes="Re-review found a population gap"), evidence["version"], "reviewer")
    result = index(frameworks.coverage(conn))
    assert result["nist-csf-2.0"]["mapped_controls"] == 1
    assert result["nist-csf-2.0"]["evidence_backed_controls"] == 0


def test_demo_mapping_requires_explicit_tag_and_does_not_mutate_live_controls(conn):
    original = control(conn, title="CTL-01 Quarterly privileged access review", framework_refs=["Custom review requirement"])
    with pytest.raises(ValueError, match="explicitly tagged"):
        frameworks.apply_demo_mappings(conn, "operator")
    assert domain.get_record(conn, "controls", original["id"])["version"] == 1
    assert domain.get_record(conn, "controls", original["id"])["framework_refs"] == ["Custom review requirement"]
    tagged_demo(conn)
    assert frameworks.apply_demo_mappings(conn, "operator") == {"updated": 1, "unchanged": 0, "matched": 1}
    updated = domain.get_record(conn, "controls", original["id"])
    assert updated["framework_refs"][0] == "Custom review requirement"
    assert set(frameworks.references_for_control("CTL-01")) <= set(updated["framework_refs"])
    assert domain.verify_audit(conn)["valid"]
    assert domain.list_audit(conn, 1)[0]["action"] == "framework.demo_mapped"
    count = domain.verify_audit(conn)["count"]
    assert frameworks.apply_demo_mappings(conn, "operator") == {"updated": 0, "unchanged": 1, "matched": 1}
    assert domain.verify_audit(conn)["count"] == count


def test_demo_helper_matches_only_exact_starter_code_boundaries(conn):
    tagged_demo(conn)
    for title in ("Production CTL-01 review", "CTL-010 extra", "ctl-01 lower case", "CTL-99 unknown"):
        control(conn, title=title)
    assert frameworks.apply_demo_mappings(conn, "operator") == {"updated": 0, "unchanged": 0, "matched": 0}


def test_demo_changes_and_audit_can_rollback_as_one_transaction(conn):
    tagged_demo(conn)
    original = control(conn, title="CTL-01 Access review")
    conn.commit()
    with pytest.raises(RuntimeError):
        with conn:
            frameworks.apply_demo_mappings(conn, "operator")
            raise RuntimeError("Simulated downstream operation failure")
    assert domain.get_record(conn, "controls", original["id"])["framework_refs"] == []
    assert domain.list_audit(conn, 1)[0]["action"] == "record.created"


def test_fictional_seed_keeps_original_csf_links_and_adds_selected_references(conn):
    seed_demo(conn, "operator")
    # Model an existing demo created before the richer pack was installed.
    for item in domain.list_records(conn, "controls"):
        legacy = [ref for ref in item["framework_refs"] if ref.startswith("NIST CSF 2.0 ")][:1]
        if item["framework_refs"] != legacy:
            domain.update_record(conn, "controls", item["id"], payload("controls", item,
                framework_refs=legacy), item["version"], "operator")
    before = {item["id"]: item["framework_refs"] for item in domain.list_records(conn, "controls")}
    tagged_demo(conn)
    result = frameworks.apply_demo_mappings(conn, "operator")
    assert result == {"updated": 12, "unchanged": 0, "matched": 12}
    for item in domain.list_records(conn, "controls"):
        assert set(before[item["id"]]) <= set(item["framework_refs"])
    coverage = index(frameworks.coverage(conn))
    assert coverage["nist-csf-2.0"]["mapped_controls"] == 12
    assert coverage["nist-sp-800-53-r5"]["mapped_controls"] == 12
    assert coverage["iso-iec-27001-2022"]["mapped_controls"] == 12
    assert coverage["iso-iec-27002-2022"]["mapped_controls"] == 10
    assert coverage["nist-csf-2.0"]["evidence_backed_controls"] == 6
    assert coverage["iso-iec-27002-2022"]["evidence_backed_controls"] == 5
    assert coverage["nist-sp-800-53a-r5"]["mapped_controls"] == 0




def test_declared_evidence_expiry_removes_assurance_before_cadence_expires(conn, monkeypatch):
    item, _ = effective_control(conn, framework_refs=frameworks.references_for_control("CTL-01"),
        frequency_days=365)
    later = domain.today() + timedelta(days=91)
    monkeypatch.setattr(domain, "today", lambda: later)
    result = index(frameworks.coverage(conn))
    assert result["nist-csf-2.0"]["mapped_controls"] == 1
    assert result["nist-csf-2.0"]["evidence_backed_controls"] == 0
    assert domain.get_record(conn, "controls", item["id"])["status"] == "effective"


def test_not_applicable_control_keeps_mapping_without_evidence_assurance_count(conn):
    item, _ = effective_control(conn, framework_refs=frameworks.references_for_control("CTL-01"))
    domain.update_record(conn, "controls", item["id"], payload("controls", item,
        status="not_applicable", description="The relevant privileged service was retired from scope"),
        item["version"], "reviewer")
    result = index(frameworks.coverage(conn))
    assert result["nist-sp-800-53-r5"]["mapped_controls"] == 1
    assert result["nist-sp-800-53-r5"]["evidence_backed_controls"] == 0


def test_demo_mapper_rejects_workspace_without_metadata_table(conn):
    original = control(conn, title="CTL-01 Access review")
    conn.execute("DROP TABLE metadata")
    with pytest.raises(ValueError, match="explicitly tagged"):
        frameworks.apply_demo_mappings(conn, "operator")
    assert domain.get_record(conn, "controls", original["id"])["framework_refs"] == []
    assert domain.verify_audit(conn)["count"] == 1


def test_demo_mapper_rejects_false_demo_marker(conn):
    control(conn, title="CTL-01 Access review")
    conn.execute("INSERT INTO metadata VALUES ('demo','false')")
    with pytest.raises(ValueError, match="explicitly tagged"):
        frameworks.apply_demo_mappings(conn, "operator")
    assert domain.verify_audit(conn)["count"] == 1


def test_reference_only_incident_guidance_remains_zero_not_assessed(conn):
    item, _ = effective_control(conn, framework_refs=frameworks.references_for_control("CTL-06"))
    assert item["status"] == "effective"
    result = index(frameworks.coverage(conn))
    assert result["nist-sp-800-61-r3"] == {
        "framework_id": "nist-sp-800-61-r3", "mapped_controls": 0, "evidence_backed_controls": 0,
    }
    assert result["nist-csf-2.0"]["evidence_backed_controls"] == 1
    entry = next(item for item in frameworks.catalog()["items"] if item["id"] == "nist-sp-800-61-r3")
    assert "reference" in entry["scope"].lower()


def test_demo_mapper_does_not_bypass_expired_effective_control_workflow(conn, monkeypatch):
    item, _ = effective_control(conn, title="CTL-01 Access review", frequency_days=7)
    tagged_demo(conn)
    conn.commit()
    later = domain.today() + timedelta(days=8)
    monkeypatch.setattr(domain, "today", lambda: later)
    with pytest.raises(ValueError, match="current independently approved evidence"):
        with conn:
            frameworks.apply_demo_mappings(conn, "operator")
    assert domain.get_record(conn, "controls", item["id"])["framework_refs"] == []
    assert domain.list_audit(conn, 1)[0]["action"] == "record.updated"


def test_selected_csf_references_span_six_functions_without_full_coverage_claim():
    pack = frameworks.mappings()
    selected_functions = {
        link["reference"].split()[-1].split(".", 1)[0]
        for item in pack["items"] for link in item["links"]
        if link["framework_id"] == "nist-csf-2.0"
    }
    assert selected_functions == {"GV", "ID", "PR", "DE", "RS", "RC"}
    assert "partial" in pack["scope"].lower()
    assert all(link["relationship"] == "partial" for item in pack["items"] for link in item["links"])
