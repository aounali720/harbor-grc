"""Curated framework references and explicit local-control coverage.

The bundled crosswalk is project-authored and partial. It supplies neither a
complete control library nor proof of conformance, certification, or equivalence.
All data is local; these helpers make no network calls and never infer mappings
from a control title. Mutations require an explicitly tagged fictional demo.
"""
import json
import re
from importlib.resources import files

from . import db, domain

_DEMO_CODE = re.compile(r"^(CTL-\d{2})(?:\s|$)")
_SCOPE = (
    "Counts cover distinct local controls with exact reference strings recognized "
    "by the bundled partial mapping pack. Evidence-backed means effective status "
    "plus current approved evidence within the control's test cadence. Counts do "
    "not measure full-framework coverage, conformance, certification, or equivalence. "
    "An unknown reference is outside this curated pack, not necessarily invalid."
)


def _read(name):
    # Fresh parsing prevents a caller from mutating a shared catalog cache.
    return json.loads(files("harbor_grc").joinpath("data", name).read_text(encoding="utf-8"))


def catalog():
    """Return versioned publication metadata, scope, and primary-source links."""
    return _read("frameworks.json")


def mappings():
    """Return the project-authored, explicitly partial 12-topic mapping pack."""
    return _read("control_mappings.json")


def references_for_control(code):
    """Return canonical strings for one exact starter code; unknown codes are empty."""
    for item in mappings()["items"]:
        if item["control_key"] == code:
            return list(dict.fromkeys(link["reference"] for link in item["links"]))
    return []


def coverage(conn):
    """Count explicit mappings; a reference alone never demonstrates assurance."""
    publications = catalog()["items"]
    recognized = {}
    for item in mappings()["items"]:
        for link in item["links"]:
            recognized.setdefault(link["reference"], set()).add(link["framework_id"])
    controls = domain.list_records(conn, "controls")
    evidence = domain.list_records(conn, "evidence")
    demonstrated = set()
    for control in controls:
        if control["status"] == "effective" and any(
            item["control_id"] == control["id"] and domain._fresh(item, control)
            for item in evidence
        ):
            demonstrated.add(control["id"])
    mapped = {item["id"]: set() for item in publications}
    unknown = []
    for control in controls:
        for reference in dict.fromkeys(control["framework_refs"]):
            framework_ids = recognized.get(reference)
            if framework_ids:
                for framework_id in framework_ids:
                    mapped[framework_id].add(control["id"])
            else:
                unknown.append({"control_id": control["id"], "reference": reference})
    return {
        "as_of": domain.today().isoformat(),
        "local_control_count": len(controls),
        "items": [{"framework_id": item["id"], "mapped_controls": len(mapped[item["id"]]),
                   "evidence_backed_controls": len(mapped[item["id"]] & demonstrated)}
                  for item in publications],
        "unknown_references": sorted(unknown, key=lambda item: (item["control_id"], item["reference"])),
        "scope": _SCOPE,
    }


def apply_demo_mappings(conn, actor):
    """Opt in to mappings on tagged demo starter records; caller owns the transaction.

    This does not identify real controls by title. The exact CTL prefix is usable
    solely after a local operator has explicitly designated the database as demo.
    Existing references are preserved and normal workflow/version checks apply.
    """
    has_metadata = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name='metadata'"
    ).fetchone()
    if not has_metadata or not db.demo_enabled(conn):
        raise ValueError("Framework starter mappings require an explicitly tagged fictional demo workspace")
    result = {"updated": 0, "unchanged": 0, "matched": 0}
    for control in domain.list_records(conn, "controls"):
        match = _DEMO_CODE.match(control["title"])
        references = references_for_control(match.group(1)) if match else []
        if not references:
            continue
        result["matched"] += 1
        combined = list(dict.fromkeys(control["framework_refs"] + references))
        if combined == control["framework_refs"]:
            result["unchanged"] += 1
            continue
        payload = {key: control[key] for key in domain.SCHEMAS["controls"].model_fields}
        payload["framework_refs"] = combined
        domain.update_record(conn, "controls", control["id"], payload, control["version"], actor)
        result["updated"] += 1
    if result["updated"]:
        domain.record_event(conn, actor, "framework.demo_mapped", "workspace", {
            **result, "mapping_version": mappings()["mapping_version"], "synthetic": True,
        })
    return result
