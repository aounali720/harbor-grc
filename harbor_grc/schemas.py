"""Validated records for a single-organization GRC register."""
from datetime import date, datetime, timezone
from typing import Annotated, Literal
from pydantic import BaseModel, AwareDatetime, ConfigDict, Field, HttpUrl, model_validator

Score = Annotated[int, Field(ge=1, le=5, strict=True)]
Short = Annotated[str, Field(min_length=1, max_length=180)]
Text = Annotated[str, Field(max_length=8000)]
Ref = Annotated[str, Field(max_length=80)]


class Record(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True, validate_default=True)
    title: Short
    owner: Short
    description: Text = ""


class Risk(Record):
    category: Literal["governance", "cloud", "vendor", "application", "operations", "privacy"] = "governance"
    likelihood: Score = 3
    impact: Score = 3
    residual_likelihood: Score | None = None
    residual_impact: Score | None = None
    residual_rationale: Text = ""
    residual_review_date: date | None = None
    residual_reviewed_by: Annotated[str, Field(max_length=180)] = ""
    treatment: Literal["mitigate", "accept", "avoid", "transfer"] = "mitigate"
    status: Literal["open", "in_treatment", "accepted", "closed"] = "open"
    due_date: date | None = None
    control_ids: list[Ref] = Field(default_factory=list, max_length=100)
    acceptance_rationale: Text = ""
    acceptance_approver: Annotated[str, Field(max_length=180)] = ""
    acceptance_expires: date | None = None

    @model_validator(mode="after")
    def scores_have_review(self):
        if (self.residual_likelihood is None) != (self.residual_impact is None):
            raise ValueError("Residual likelihood and impact must be supplied together")
        if self.residual_likelihood is not None:
            if not self.residual_rationale or not self.residual_review_date:
                raise ValueError("A residual rating requires rationale and review date")
            if self.residual_review_date > datetime.now(timezone.utc).date():
                raise ValueError("Residual review date cannot be in the future")
        if self.status == "accepted" and self.treatment != "accept":
            raise ValueError("Accepted risks must use the accept treatment")
        return self


class Control(Record):
    domain: Literal["governance", "cloud", "vendor", "identity", "operations", "application", "privacy"] = "governance"
    framework_refs: list[Annotated[str, Field(max_length=80)]] = Field(default_factory=list, max_length=30)
    status: Literal["planned", "implemented", "effective", "ineffective", "not_applicable"] = "planned"
    test_procedure: Text = ""
    frequency_days: Annotated[int, Field(ge=1, le=730)] = 90


class Vendor(Record):
    service: Short
    criticality: Literal["low", "medium", "high", "critical"] = "medium"
    data_sensitivity: Literal["public", "internal", "confidential", "restricted"] = "internal"
    access_level: Literal["none", "user", "privileged"] = "none"
    questionnaire_score: Annotated[int, Field(ge=0, le=100, strict=True)] | None = None
    status: Literal["screening", "due_diligence", "approved", "conditional", "rejected", "offboarded"] = "screening"
    review_date: date | None = None
    assurance_notes: Text = ""


class Asset(Record):
    provider: Literal["AWS", "Azure", "GCP", "SaaS", "internal"] = "AWS"
    environment: Literal["production", "staging", "development", "corporate"] = "production"
    asset_type: Short = "service"
    external_id: Annotated[str, Field(max_length=1024)] = ""
    data_classification: Literal["public", "internal", "confidential", "restricted"] = "internal"
    criticality: Literal["low", "medium", "high", "critical"] = "medium"


class Evidence(Record):
    control_id: Ref
    uri: HttpUrl
    sha256: Annotated[str, Field(pattern=r"^[a-f0-9]{64}$")]
    collected_on: date
    expires_on: date
    status: Literal["pending", "approved", "rejected"] = "pending"
    review_notes: Text = ""
    submitted_by: Annotated[str, Field(max_length=180)] = ""
    reviewed_by: Annotated[str, Field(max_length=180)] = ""

    @model_validator(mode="after")
    def date_order(self):
        if self.expires_on < self.collected_on:
            raise ValueError("Evidence expiry must be on or after collection")
        if self.collected_on > datetime.now(timezone.utc).date():
            raise ValueError("Evidence collection cannot be in the future")
        if self.uri.username or self.uri.password or self.uri.query:
            raise ValueError("Evidence references must not include embedded credentials or query tokens")
        if self.uri.scheme != "https":
            raise ValueError("Evidence references must use HTTPS")
        return self


class Finding(Record):
    severity: Literal["low", "medium", "high", "critical"] = "medium"
    status: Literal["open", "in_progress", "closed", "risk_accepted"] = "open"
    due_date: date | None = None
    control_id: Ref = ""
    risk_id: Ref = ""
    vendor_id: Ref = ""
    asset_id: Ref = ""
    evidence_id: Ref = ""
    source_key: Annotated[str, Field(max_length=1024)] = ""
    source_updated_at: AwareDatetime | None = None
    remediation: Text = ""


KINDS = ("risks", "controls", "vendors", "assets", "evidence", "findings")
SCHEMAS = dict(zip(KINDS, (Risk, Control, Vendor, Asset, Evidence, Finding)))



