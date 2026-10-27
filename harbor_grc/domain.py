"""Transactional GRC operations; connections and commits belong to the caller.

The hash chain detects edits relative to a trusted checkpoint. It is not WORM
storage and cannot prevent a database administrator from rewriting history.
"""
import hashlib
import json
import uuid
from datetime import date, datetime, timedelta, timezone

from .schemas import KINDS, SCHEMAS


class ConflictError(ValueError):
    """The record changed after the client read it."""


def utcnow():
    return datetime.now(timezone.utc).isoformat(timespec="microseconds")


def today():
    return datetime.now(timezone.utc).date()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def init_schema(conn):
    # executescript would commit a caller's transaction.
    conn.execute("""CREATE TABLE IF NOT EXISTS records (
        id TEXT PRIMARY KEY, kind TEXT NOT NULL, version INTEGER NOT NULL CHECK(version > 0),
        data TEXT NOT NULL, created_by TEXT NOT NULL, created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL)""")
    conn.execute("CREATE INDEX IF NOT EXISTS records_kind ON records(kind)")
    conn.execute("""CREATE TABLE IF NOT EXISTS audit (
        seq INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT NOT NULL,
        actor TEXT NOT NULL, action TEXT NOT NULL, target TEXT NOT NULL,
        details TEXT NOT NULL, previous_hash TEXT NOT NULL, hash TEXT NOT NULL)""")


def _kind(kind):
    if kind not in KINDS:
        raise ValueError("Unknown record kind")


def _unpack(row):
    result = json.loads(row["data"])
    if row["kind"] == "findings":
        result.setdefault("source_updated_at", None)
    result.update({key: row[key] for key in ("id", "version", "created_by", "created_at", "updated_at")})
    return result


def list_records(conn, kind):
    _kind(kind)
    return [_unpack(row) for row in conn.execute(
        "SELECT * FROM records WHERE kind=? ORDER BY created_at,id", (kind,))]


def get_record(conn, kind, record_id):
    _kind(kind)
    row = conn.execute("SELECT * FROM records WHERE kind=? AND id=?", (kind, record_id)).fetchone()
    if row is None:
        raise KeyError("Record not found")
    return _unpack(row)


def _ref(conn, kind, record_id):
    if record_id:
        try:
            return get_record(conn, kind, record_id)
        except KeyError as exc:
            raise ValueError(f"Referenced {kind} record does not exist: {record_id}") from exc
    return None


def vendor_tier(vendor):
    """An inherent triage rule, not a quantitative assurance rating."""
    if (vendor["criticality"] == "critical" or vendor["data_sensitivity"] == "restricted"
            or vendor["access_level"] == "privileged"):
        return "tier_1"
    if vendor["criticality"] == "high" or vendor["data_sensitivity"] == "confidential":
        return "tier_2"
    return "tier_3"


def _fresh(evidence, control=None):
    within_cadence = (control is None or date.fromisoformat(evidence["collected_on"])
                      + timedelta(days=control["frequency_days"]) >= today())
    return (evidence["status"] == "approved" and evidence["expires_on"] >= today().isoformat()
            and evidence["collected_on"] <= today().isoformat() and within_cadence)


def _validate(conn, kind, data, actor, old=None):
    values = SCHEMAS[kind].model_validate(data).model_dump(mode="json")
    if kind == "risks":
        for control_id in values["control_ids"]:
            _ref(conn, "controls", control_id)
        if len(values["control_ids"]) != len(set(values["control_ids"])):
            raise ValueError("Control references must be unique")
        residual_fields = ("residual_likelihood", "residual_impact", "residual_rationale", "residual_review_date")
        if values["residual_likelihood"] is not None:
            if old is None or any(values[key] != old[key] for key in residual_fields):
                values["residual_reviewed_by"] = actor
            else:
                values["residual_reviewed_by"] = old["residual_reviewed_by"]
        else:
            values["residual_reviewed_by"] = ""
        if values["status"] == "accepted":
            if old is None or actor == old["created_by"]:
                raise ValueError("Risk acceptance requires an approver other than the record creator")
            values["acceptance_approver"] = actor
            if (not values["acceptance_rationale"] or not values["acceptance_expires"]
                    or values["acceptance_expires"] <= today().isoformat()):
                raise ValueError("Risk acceptance requires rationale and a future expiry")
        if values["status"] == "closed" and not values["residual_rationale"]:
            raise ValueError("Closing a risk requires a documented residual rationale")
    elif kind == "controls":
        if values["status"] == "effective":
            if old is None or not any(_fresh(item, values) and item["control_id"] == old["id"]
                                      for item in list_records(conn, "evidence")):
                raise ValueError("An effective control requires current independently approved evidence")
            if not values["test_procedure"]:
                raise ValueError("An effective control requires a documented test procedure")
        if values["status"] == "not_applicable" and not values["description"]:
            raise ValueError("Not-applicable controls require a rationale in description")
    elif kind == "vendors":
        if values["status"] in ("approved", "conditional"):
            if not values["assurance_notes"] or not values["review_date"]:
                raise ValueError("Vendor approval requires assurance notes and a review date")
    elif kind == "evidence":
        _ref(conn, "controls", values["control_id"])
        immutable = ("title", "description", "control_id", "uri", "sha256", "collected_on", "expires_on")
        content_changed = old is None or any(values[key] != old[key] for key in immutable)
        values["submitted_by"] = actor if content_changed else old.get("submitted_by", old["created_by"])
        if values["status"] == "approved":
            if old is None:
                raise ValueError("Evidence approval requires a reviewer other than its creator or current submitter")
            if content_changed:
                raise ValueError("Submit changed evidence as pending before it can be approved")
            if actor in (old["created_by"], values["submitted_by"]):
                raise ValueError("Evidence approval requires a reviewer other than its creator or current submitter")
            if values["expires_on"] < today().isoformat():
                raise ValueError("Expired evidence cannot be approved")
            if not values["review_notes"]:
                raise ValueError("Evidence approval requires review notes")
            values["reviewed_by"] = actor
        else:
            values["reviewed_by"] = ""
    elif kind == "findings":
        for field, target in (("control_id", "controls"), ("risk_id", "risks"),
                              ("vendor_id", "vendors"), ("asset_id", "assets"),
                              ("evidence_id", "evidence")):
            _ref(conn, target, values[field])
        if values["source_key"]:
            for record in list_records(conn, "findings"):
                if record["source_key"] == values["source_key"] and (old is None or record["id"] != old["id"]):
                    raise ConflictError("A finding with this source key already exists")
        if values["status"] == "closed":
            evidence = _ref(conn, "evidence", values["evidence_id"])
            if evidence is None or not _fresh(evidence, _ref(conn, "controls", evidence["control_id"])):
                raise ValueError("Finding closure requires current approved evidence")
            if values["control_id"] and evidence["control_id"] != values["control_id"]:
                raise ValueError("Closure evidence must belong to the finding's control")
            if not values["remediation"]:
                raise ValueError("Finding closure requires remediation notes")
        if values["status"] == "risk_accepted":
            risk = _ref(conn, "risks", values["risk_id"])
            if (risk is None or risk["status"] != "accepted" or not risk["acceptance_expires"]
                    or risk["acceptance_expires"] <= today().isoformat()):
                raise ValueError("An accepted finding must reference a currently accepted risk")
    return values


def _audit_hash(fields):
    return hashlib.sha256(canonical(fields).encode("utf-8")).hexdigest()


def record_event(conn, actor, action, target, details):
    tail = conn.execute("SELECT hash FROM audit ORDER BY seq DESC LIMIT 1").fetchone()
    fields = {"timestamp": utcnow(), "actor": actor, "action": action, "target": target,
              "details": details, "previous_hash": tail["hash"] if tail else "0" * 64}
    digest = _audit_hash(fields)
    conn.execute("""INSERT INTO audit(timestamp,actor,action,target,details,previous_hash,hash)
        VALUES(?,?,?,?,?,?,?)""", (fields["timestamp"], actor, action, target,
                                  canonical(details), fields["previous_hash"], digest))
    return digest


def create_record(conn, kind, payload, actor):
    _kind(kind)
    values = _validate(conn, kind, payload, actor)
    record_id = {"risks": "RSK", "controls": "CTL", "vendors": "VND", "assets": "AST",
                 "evidence": "EVD", "findings": "FND"}[kind] + "-" + uuid.uuid4().hex[:12]
    timestamp = utcnow()
    conn.execute("INSERT INTO records(id,kind,version,data,created_by,created_at,updated_at) VALUES(?,?,?,?,?,?,?)",
                 (record_id, kind, 1, canonical(values), actor, timestamp, timestamp))
    record_event(conn, actor, "record.created", record_id, {"kind": kind, "version": 1})
    return get_record(conn, kind, record_id)


def update_record(conn, kind, record_id, payload, expected_version, actor):
    _kind(kind)
    old = get_record(conn, kind, record_id)
    if old["version"] != expected_version:
        raise ConflictError("Record version is stale; reload before saving")
    values = _validate(conn, kind, payload, actor, old)
    changed = [key for key, value in values.items() if value != old[key]]
    cursor = conn.execute("""UPDATE records SET version=version+1,data=?,updated_at=?
        WHERE id=? AND kind=? AND version=?""", (canonical(values), utcnow(), record_id, kind, expected_version))
    if cursor.rowcount != 1:
        raise ConflictError("Record version is stale; reload before saving")
    record_event(conn, actor, "record.updated", record_id,
                 {"kind": kind, "version": expected_version + 1, "changed_fields": changed})
    return get_record(conn, kind, record_id)


def list_audit(conn, limit=200):
    return [{**dict(row), "details": json.loads(row["details"])} for row in conn.execute(
        "SELECT * FROM audit ORDER BY seq DESC LIMIT ?", (max(1, min(int(limit), 1000)),))]


def verify_audit(conn):
    previous, count = "0" * 64, 0
    for row in conn.execute("SELECT * FROM audit ORDER BY seq"):
        count += 1
        fields = {key: row[key] for key in ("timestamp", "actor", "action", "target", "previous_hash")}
        try:
            fields["details"] = json.loads(row["details"])
        except (ValueError, TypeError):
            return {"valid": False, "count": count, "failed_sequence": row["seq"], "head_hash": previous}
        if row["previous_hash"] != previous or row["hash"] != _audit_hash(fields):
            return {"valid": False, "count": count, "failed_sequence": row["seq"], "head_hash": previous}
        previous = row["hash"]
    return {"valid": True, "count": count, "head_hash": previous,
            "limitation": "Requires an external trusted checkpoint to detect truncation or a fully rewritten chain."}


def risk_rating(score):
    return "critical" if score >= 20 else "high" if score >= 12 else "medium" if score >= 6 else "low"


def dashboard(conn):
    records = {kind: list_records(conn, kind) for kind in KINDS}
    as_of = today().isoformat()
    controls, evidence = records["controls"], records["evidence"]
    control_index = {item["id"]: item for item in controls}
    current_ids = {item["control_id"] for item in evidence if _fresh(item, control_index[item["control_id"]])}
    evidence_index = {item["id"]: item for item in evidence}
    applicable = [item for item in controls if item["status"] != "not_applicable"]
    demonstrated = [item for item in applicable if item["status"] == "effective" and item["id"] in current_ids]
    open_risks = [item for item in records["risks"] if item["status"] != "closed"]
    heatmap = [[0 for _ in range(5)] for _ in range(5)]
    for risk in open_risks:
        heatmap[risk["likelihood"] - 1][risk["impact"] - 1] += 1
    expired_acceptances = [item["id"] for item in records["risks"] if item["status"] == "accepted"
                           and (not item["acceptance_expires"] or item["acceptance_expires"] <= as_of)]
    return {
        "as_of": as_of,
        "counts": {kind: len(items) for kind, items in records.items()},
        "open_risks": len(open_risks),
        "high_inherent_risks": sum(item["likelihood"] * item["impact"] >= 12 for item in open_risks),
        "unreviewed_residual_risks": sum(item["residual_likelihood"] is None for item in open_risks),
        "applicable_controls": len(applicable), "evidence_backed_effective_controls": len(demonstrated),
        "control_coverage_percent": round(len(demonstrated) / len(applicable) * 100, 1) if applicable else None,
        "coverage_note": "Coverage means effective status plus current approved evidence; it is not certification or a compliance percentage.",
        "stale_effective_control_ids": [item["id"] for item in controls if item["status"] == "effective" and item["id"] not in current_ids],
        "stale_closed_finding_ids": [item["id"] for item in records["findings"] if item["status"] == "closed"
            and (not evidence_index.get(item["evidence_id"]) or not _fresh(evidence_index[item["evidence_id"]], control_index[evidence_index[item["evidence_id"]]["control_id"]]))],
        "expired_evidence": sum(item["expires_on"] < as_of for item in evidence),
        "pending_evidence": sum(item["status"] == "pending" for item in evidence),
        "open_findings": sum(item["status"] in ("open", "in_progress") for item in records["findings"]),
        "overdue_findings": sum(item["status"] in ("open", "in_progress") and bool(item["due_date"]) and item["due_date"] < as_of for item in records["findings"]),
        "overdue_risks": sum(item["status"] not in ("accepted", "closed") and bool(item["due_date"]) and item["due_date"] < as_of for item in records["risks"]),
        "expired_acceptance_ids": expired_acceptances,
        "vendor_tiers": {tier: sum(vendor_tier(item) == tier for item in records["vendors"]) for tier in ("tier_1", "tier_2", "tier_3")},
        "overdue_vendor_reviews": sum(item["status"] not in ("offboarded", "rejected") and bool(item["review_date"]) and item["review_date"] < as_of for item in records["vendors"]),
        "inherent_heatmap": heatmap,
    }


def report(conn):
    from . import frameworks

    registers = {kind: list_records(conn, kind) for kind in KINDS}
    for item in registers["vendors"]:
        item["tier"] = vendor_tier(item)
    for item in registers["risks"]:
        item["inherent_score"] = item["likelihood"] * item["impact"]
        item["residual_score"] = (item["residual_likelihood"] * item["residual_impact"]
                                  if item["residual_likelihood"] is not None else None)
    return {"generated_at": utcnow(), "schema_version": 1, "registers": registers,
            "dashboard": dashboard(conn), "audit_verification": verify_audit(conn),
            "framework_catalog": frameworks.catalog(), "framework_mappings": frameworks.mappings(),
            "framework_coverage": frameworks.coverage(conn)}




