"""Bounded, offline ASFF adapter. Cloud observations never approve controls."""
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Literal

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, field_validator

from . import domain


class Resource(BaseModel):
    Id: str = Field(min_length=1, max_length=1024)


class CloudSeverity(BaseModel):
    Label: Literal["INFORMATIONAL", "LOW", "MEDIUM", "HIGH", "CRITICAL"] = "MEDIUM"


class Observation(BaseModel):
    model_config = ConfigDict(extra="ignore")
    Id: str = Field(min_length=1, max_length=800)
    ProductArn: str = Field(min_length=1, max_length=800)
    UpdatedAt: AwareDatetime
    Title: str = Field(min_length=1, max_length=180)
    Description: str = Field(default="", max_length=8000)
    Severity: CloudSeverity = Field(default_factory=CloudSeverity)
    Resources: list[Resource] = Field(default_factory=list, max_length=100)
    Compliance: dict = Field(default_factory=dict)
    RecordState: Literal["ACTIVE", "ARCHIVED"] = "ACTIVE"

    @field_validator("UpdatedAt")
    @classmethod
    def plausible_timestamp(cls, value):
        if value > datetime.now(timezone.utc) + timedelta(minutes=5):
            raise ValueError("UpdatedAt cannot be more than five minutes in the future")
        return value.astimezone(timezone.utc)


class Batch(BaseModel):
    model_config = ConfigDict(extra="forbid")
    Findings: list[Observation] = Field(min_length=1, max_length=250)


def import_findings(conn, payload, actor):
    # Validate the entire batch before creating any records.
    batch = Batch.model_validate(payload)
    result = {"created": 0, "updated": 0, "skipped": 0}
    by_source = {x["source_key"]: x for x in domain.list_records(conn, "findings") if x["source_key"]}
    assets = {x["external_id"]: x["id"] for x in domain.list_records(conn, "assets") if x["external_id"]}
    for observation in batch.Findings:
        if observation.RecordState == "ARCHIVED" or observation.Compliance.get("Status") != "FAILED":
            result["skipped"] += 1
            continue
        source = "asff:" + hashlib.sha256(
            (observation.ProductArn + "\0" + observation.Id).encode()).hexdigest()
        severity = observation.Severity.Label.lower()
        if severity == "informational":
            severity = "low"
        observed = {"title": observation.Title, "description": observation.Description,
                    "severity": severity, "source_updated_at": observation.UpdatedAt.isoformat()}
        old = by_source.get(source)
        if old:
            # Source time, not arrival order, governs updates. Manual records without
            # source history use their last local edit as a conservative boundary.
            previous = old.get("source_updated_at") or old["updated_at"]
            previous_time = datetime.fromisoformat(previous.replace("Z", "+00:00"))
            if observation.UpdatedAt <= previous_time:
                result["skipped"] += 1
                continue
            data = {key: old[key] for key in domain.SCHEMAS["findings"].model_fields}
            data.update(observed)
            # A newer failure is renewed evidence of exposure even if its words
            # and severity match the previously remediated observation.
            if data["status"] in {"closed", "risk_accepted"}:
                data["status"] = "open"
            item = domain.update_record(conn, "findings", old["id"], data, old["version"], actor)
            result["updated"] += 1
        else:
            due = domain.today() + timedelta(days={"critical": 3, "high": 14, "medium": 30, "low": 90}[severity])
            asset = next((assets[r.Id] for r in observation.Resources if r.Id in assets), "")
            item = domain.create_record(conn, "findings", {
                **observed, "owner": "Cloud security", "source_key": source,
                "asset_id": asset, "due_date": due.isoformat(),
                "remediation": "Triage the source observation, assign an owner, and document verified remediation."
            }, actor)
            result["created"] += 1
        by_source[source] = item
    domain.record_event(conn, actor, "cloud.imported", "workspace", result)
    return result
