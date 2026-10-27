"""Wholly fictional Northstar Metrics case study. Never mix this with live records."""
import hashlib
from datetime import timedelta

from .domain import (KINDS, create_record, dashboard, list_records, record_event,
                     today, update_record)
from .schemas import SCHEMAS
from .frameworks import references_for_control


def _payload(kind, record):
    return {key: record[key] for key in SCHEMAS[kind].model_fields}


def seed_demo(conn, actor):
    """Insert an end-to-end case study into an empty register without committing.

    demo:* actors deliberately represent fictional case-study participants, not
    log-in accounts. The initiating operator is recorded in demo.seeded.
    """
    if conn.execute("SELECT 1 FROM records LIMIT 1").fetchone():
        return {"seeded": False, "reason": "Register is not empty; no sample data added"}
    now = today()
    def due(days):
        return (now + timedelta(days=days)).isoformat()

    maker, reviewer = "demo:control-owner", "demo:independent-reviewer"
    controls = []
    specifications = [
        ("CTL-01 Quarterly privileged access review", "identity", "PR.AA-05", "Identity lead", "Compare all privileged identities with approved role assignments; investigate terminated and dormant users.", 90),
        ("CTL-02 Production storage exposure", "cloud", "PR.DS-01", "Cloud lead", "Inspect account and bucket public-access settings; verify anonymous reads fail and exceptions have approval.", 30),
        ("CTL-03 Centralized cloud audit logging", "cloud", "DE.CM-09", "Cloud lead", "Sample each production account and region; verify management events arrive in the protected log account.", 30),
        ("CTL-04 Restore testing", "operations", "RC.RP-03", "Reliability lead", "Restore a representative backup in isolation; measure recovery time and confirm record integrity.", 90),
        ("CTL-05 Critical vendor due diligence", "vendor", "GV.SC-06", "Procurement lead", "Verify service scope, independent assurance, incident notice, data handling and customer responsibilities before approval.", 180),
        ("CTL-06 Supplier incident coordination", "vendor", "GV.SC-08", "Security lead", "Run a tabletop involving a critical supplier and verify escalation contacts and contractual notices.", 180),
        ("CTL-07 Risk decisions and exceptions", "governance", "GV.RM-02", "Risk lead", "Sample accepted risks; check independent authority, documented rationale, expiry and treatment follow-up.", 90),
        ("CTL-08 Vulnerability remediation", "application", "ID.RA-01", "Engineering lead", "Reconcile scanner inventory to production assets and retest overdue high-severity issues.", 14),
        ("CTL-09 Managed workforce authentication", "identity", "PR.AA-03", "Identity lead", "Sample workforce access paths and test enforced MFA, recovery and emergency-access procedures.", 90),
        ("CTL-10 Data retention and deletion", "privacy", "PR.DS-01", "Privacy lead", "Trace one approved deletion request through primary storage, analytics processors and documented backup retention.", 90),
        ("CTL-11 Production change authorization", "application", "PR.PS-01", "Engineering lead", "Sample production releases; verify independent approval, automated checks and rollback records.", 30),
        ("CTL-12 Security program oversight", "governance", "GV.OV-01", "Risk lead", "Review committee minutes for overdue actions, risk appetite decisions and resource commitments.", 90),
    ]
    for title, domain, ref, owner, test, days in specifications:
        controls.append(create_record(conn, "controls", {
            "title": title, "owner": owner, "description": "Northstar Metrics fictional case-study control; scope is the production SaaS service.",
            "domain": domain, "framework_refs": references_for_control(title[:6]) or [f"NIST CSF 2.0 {ref}"], "status": "implemented",
            "test_procedure": test, "frequency_days": days,
        }, maker))
    vendors = []
    vendor_specs = [
        ("VND-01 Nimbus Hosting", "Cloud infrastructure", "critical", "restricted", "privileged", 78, "conditional", "Independent assurance covers infrastructure only. Customer IAM and storage configuration remain Northstar responsibilities; missing recovery drill is tracked.", -12),
        ("VND-02 Lantern Identity", "Workforce identity provider", "critical", "confidential", "privileged", 90, "approved", "Assurance scope and incident-notification terms reviewed; recovery and emergency access tests need quarterly confirmation.", 120),
        ("VND-03 Parcel Email", "Transactional notifications", "high", "confidential", "user", 72, "conditional", "Retention commitments confirmed. Subprocessor change notification and deletion evidence remain open conditions.", 21),
        ("VND-04 Marble Analytics", "Product telemetry", "medium", "internal", "none", None, "due_diligence", "No customer identifiers permitted. Questionnaire not completed; procurement must not infer assurance from missing responses.", 14),
        ("VND-05 Canvas Design", "Public brand assets", "low", "public", "none", 82, "approved", "Public assets only; no production or customer access. Annual scope recheck assigned.", 300),
    ]
    for title, service, criticality, sensitivity, access, score, status, notes, days in vendor_specs:
        vendors.append(create_record(conn, "vendors", {
            "title": title, "owner": "Procurement lead", "service": service,
            "description": "Fictional supplier; any resemblance to a real provider is coincidental.",
            "criticality": criticality, "data_sensitivity": sensitivity, "access_level": access,
            "questionnaire_score": score, "status": status, "review_date": due(days), "assurance_notes": notes,
        }, "demo:vendor-analyst"))
    assets = []
    asset_specs = [
        ("AST-01 Production customer objects", "AWS", "production", "object-storage", "restricted", "critical"),
        ("AST-02 Customer application database", "AWS", "production", "managed-database", "restricted", "critical"),
        ("AST-03 Central audit archive", "AWS", "production", "log-archive", "confidential", "high"),
        ("AST-04 Container application service", "AWS", "production", "container-service", "confidential", "critical"),
        ("AST-05 Recovery backup vault", "AWS", "production", "backup-vault", "restricted", "critical"),
        ("AST-06 Staging integration service", "AWS", "staging", "container-service", "internal", "medium"),
        ("AST-07 Workforce identity tenant", "SaaS", "corporate", "identity-provider", "confidential", "critical"),
        ("AST-08 Telemetry processor", "SaaS", "production", "analytics", "internal", "medium"),
    ]
    for index, (title, provider, environment, asset_type, classification, criticality) in enumerate(asset_specs):
        assets.append(create_record(conn, "assets", {
            "title": title, "owner": "Cloud lead" if provider == "AWS" else "IT lead",
            "description": "Synthetic asset identifier; no live account or endpoint is represented.",
            "provider": provider, "environment": environment, "asset_type": asset_type,
            "external_id": f"https://inventory.northstar.example/assets/synthetic-{index + 1}",
            "data_classification": classification, "criticality": criticality,
        }, "demo:asset-owner"))
    risks = []
    risk_specs = [
        ("RSK-01 Public exposure of customer exports", "cloud", 4, 5, [1, 2], "Cloud lead", -7),
        ("RSK-02 Privileged access persists after role changes", "governance", 4, 4, [0, 8], "Identity lead", 14),
        ("RSK-03 Critical supplier outage exceeds recovery objectives", "vendor", 3, 5, [3, 4, 5], "Reliability lead", 21),
        ("RSK-04 Security logs are incomplete during an incident", "cloud", 3, 4, [2, 5], "Security lead", 30),
        ("RSK-05 High-severity dependency remains exploitable", "application", 4, 4, [7, 10], "Engineering lead", -3),
        ("RSK-06 Processor retains data beyond contract", "privacy", 3, 4, [4, 9], "Privacy lead", 45),
        ("RSK-07 Risk exceptions outlive their business justification", "governance", 3, 3, [6, 11], "Risk lead", 30),
        ("RSK-08 Supplier incident notice arrives too late", "vendor", 3, 4, [4, 5], "Procurement lead", 21),
        ("RSK-09 Restored backups cannot meet integrity requirements", "operations", 3, 5, [3], "Reliability lead", 35),
        ("RSK-10 Public design service unavailable for one business day", "vendor", 2, 2, [4, 6], "Marketing lead", 90),
    ]
    for index, (title, category, likelihood, impact, refs, owner, days) in enumerate(risk_specs):
        payload = {"title": title, "owner": owner, "description": "Scenario states a potential business loss, not a confirmed incident. Validate likelihood with local threat and loss history before reuse.",
                   "category": category, "likelihood": likelihood, "impact": impact,
                   "status": "in_treatment", "treatment": "mitigate", "due_date": due(days),
                   "control_ids": [controls[ref]["id"] for ref in refs]}
        if index in (1, 3, 6, 9):
            payload.update(residual_likelihood=max(1, likelihood - 1), residual_impact=impact,
                           residual_rationale="Fictional reviewer considered recent access/logging tests, remaining coverage gaps and business impact. Impact is unchanged; the residual estimate requires periodic review.",
                           residual_review_date=due(0))
        risks.append(create_record(conn, "risks", payload, "demo:risk-owner"))
    accepted = _payload("risks", risks[-1])
    accepted.update(status="accepted", treatment="accept", acceptance_rationale="Public design assets are cached locally; the estimated one-day disruption is within the fictional marketing risk tolerance.", acceptance_expires=due(90))
    risks[-1] = update_record(conn, "risks", risks[-1]["id"], accepted, risks[-1]["version"], "demo:risk-approver")
    evidence = []
    for index, control_index in enumerate((0, 1, 2, 3, 4, 8, 10, 11)):
        expired = index == 4
        payload = {"title": f"EVD-{index + 1:02d} Synthetic test record for {controls[control_index]['title'][:6]}",
                   "owner": controls[control_index]["owner"], "description": "Synthetic evidence metadata. The URI is reserved and does not host a real artifact; its digest represents a fictional case-study marker.",
                   "control_id": controls[control_index]["id"], "uri": f"https://evidence.northstar.example/demo/test-{index + 1}.json",
                   "sha256": hashlib.sha256(f"Northstar synthetic evidence {index + 1}".encode()).hexdigest(),
                   "collected_on": due(-120 if expired else -7), "expires_on": due(-10 if expired else 83)}
        item = create_record(conn, "evidence", payload, "demo:evidence-collector")
        if index not in (3, 4):
            approved = _payload("evidence", item)
            approved.update(status="approved", review_notes="Fictional independent review checked scope, sample, collection date and stated exceptions. No real assurance is asserted.")
            item = update_record(conn, "evidence", item["id"], approved, item["version"], reviewer)
            control = controls[control_index]
            effective = _payload("controls", control)
            effective["status"] = "effective"
            controls[control_index] = update_record(conn, "controls", control["id"], effective, control["version"], reviewer)
        evidence.append(item)
    finding_specs = [
        ("FND-01 Public storage exception lacks sign-off", "critical", 0, 1, 0, None, -7),
        ("FND-02 Dormant privileged account review incomplete", "high", 1, 0, 6, None, 7),
        ("FND-03 Supplier continuity exercise not completed", "high", 2, 3, 4, 0, 21),
        ("FND-04 Region coverage missing from log test", "medium", 3, 2, 2, None, 14),
        ("FND-05 Dependency remediation deadline missed", "high", 4, 7, 3, None, -3),
        ("FND-06 Deletion confirmation missing from processor", "medium", 5, 9, 7, 2, 30),
        ("FND-07 Change approval sampling exception resolved", "low", 4, 10, 3, None, 0),
    ]
    for index, (title, severity, risk_index, control_index, asset_index, vendor_index, days) in enumerate(finding_specs):
        payload = {"title": title, "owner": risks[risk_index]["owner"], "description": "A synthetic audit observation for the Northstar Metrics case study.",
                   "severity": severity, "due_date": due(days), "control_id": controls[control_index]["id"],
                   "risk_id": risks[risk_index]["id"], "asset_id": assets[asset_index]["id"],
                   "vendor_id": vendors[vendor_index]["id"] if vendor_index is not None else "",
                   "remediation": "Assign an accountable owner, record a bounded action, collect evidence and request independent retest.",
                   "status": "in_progress" if index % 2 else "open"}
        if index == 6:
            payload.update(status="closed", evidence_id=evidence[6]["id"], remediation="Independent reviewer resampled the fictional release records and confirmed approvals preceded deployment.")
        create_record(conn, "findings", payload, "demo:assurance-analyst")
    counts = {kind: len(list_records(conn, kind)) for kind in KINDS}
    record_event(conn, actor, "demo.seeded", "Northstar Metrics", {"synthetic": True, "counts": counts})
    return {"seeded": True, "counts": counts, "dashboard": dashboard(conn)}

