# API and integration contract

The browser is the primary client. Every `/api/*` route requires a session except
login. There are no service API keys, bearer tokens, CORS allowances, or cloud credentials.
The API deliberately requires an exact `Origin` on all state-changing requests,
including non-browser clients.

## Authentication

`POST /api/auth/login` with JSON `{"username":"your-user","password":"your-passphrase"}`.
Send `Origin: <GRC_ORIGIN>`. The response sets an HttpOnly cookie and returns
`{user:{username,role},csrf_token,workspace:{name,demo}}`. Keep credentials out of shell
history. `GET /api/auth/me` returns the same user/session metadata.
`POST /api/auth/logout` sends an empty JSON object plus `X-CSRF-Token`.

For every other POST/PUT, preserve the cookie, send `Content-Type: application/json`,
`Origin`, and `X-CSRF-Token`. Do not place the CSRF value in a URL.
Sessions expire after eight hours or thirty minutes of inactivity; activity
refresh is recorded at most once per minute.

## Resources

Kinds: `risks`, `controls`, `vendors`, `assets`, `evidence`, `findings`.

| Method and route | Behavior |
|---|---|
| GET /api/schema | `{kinds:{kind:JSONSchema}}`; canonical current field constraints |
| GET /api/{kind} | `{items:[record,...]}` |
| GET /api/{kind}/{id} | One record |
| POST /api/{kind} | Create payload, HTTP 201 |
| PUT /api/{kind}/{id} | Full replacement of model fields with `{version:n,data:{...}}` |
| GET /api/dashboard | Date-stamped counts and attention signals |
| GET /api/audit?limit=200 | Events (newest first, at most 1000) plus full-chain verification |
| GET /api/report | Download JSON registers, derived values and checkpoint; records an export event |
| POST /api/import/cloud | Import `{Findings:[ASFF observation,...]}`; result `{created,updated,skipped}` |

Unknown fields are rejected on domain records. Timestamps, versions, IDs and creators
are server metadata and must be excluded from replacement payloads. Evidence reviewer/
submitter and risk reviewer/acceptance-approver fields are stamped by the server;
they cannot be used to impersonate a reviewer. Optional model defaults are available
through the schema endpoint. Source observation timestamps on findings are optional
for manual records and require a timezone when supplied.

A stale version gives HTTP 409. Reload the record and reconcile edits. Do not
blindly retry a replacement with a new version. There is no deletion endpoint:
preserve business decisions and close/offboard records.

## Offline cloud imports

Only observations with `Compliance.Status="FAILED"` and active state are processed.
Passed, warning, not-available, and archived observations are skipped. Required
fields are Id, ProductArn, Title, and UpdatedAt. UpdatedAt must include a timezone;
timestamps more than five minutes in the future are rejected. Severity.Label defaults to MEDIUM; resources
can link an already inventoried asset by exact external_id. Unknown top-level
batch keys are rejected; additional fields within an observation are ignored.

A source key is a SHA-256 digest over ProductArn, a separator, and Id. A repeated
source does not create a duplicate. The adapter records the observation's UpdatedAt
as source_updated_at. Older or equal source timestamps are skipped, so a stale
replay cannot overwrite current triage. A newer failed observation updates the source
fields and timestamp while preserving its assigned owner, notes, links, and due date.
A previously closed/accepted finding reopens even if its title, description, and
severity are unchanged: a newer failure requires renewed triage. For a manually
created source-linked finding without source_updated_at, its last local updated_at
is the comparison boundary. Review due dates after severity changes; the existing
date is preserved. An import never closes a finding or changes a control's effectiveness.

Defaults for due dates (critical 3 days, high 14, medium 30, low 90) are project
policy examples, not AWS requirements. Informational observations map to low.
The adapter stores no full raw export and performs no source signature verification.

Validate and sanitize an export before importing it. Product IDs are hashed, but
titles/descriptions may contain account names, resource paths, or sensitive text.
The 250-observation and 1 MiB caps apply. The transaction rolls back the entire batch
on a validation or workflow failure.

## Metrics and reports

Read `as_of` and report generation timestamps. Controls need an effective status
and current approved evidence for the coverage denominator/numerator. This is an
evidence-backed control coverage metric, not a compliance percentage.

Audit verification exposes `valid`, `count`, and `head_hash`. Keep a protected
checkpoint outside this database if truncation/rewrite detection matters.
Reports are snapshots of current records; they are not a full change-history archive.


## Framework references and local mapping counts

Authenticated readers, including auditors, can use:

| Route | Response |
|---|---|
| GET /api/frameworks | Curated catalog, edition metadata, official sources, check date and limits |
| GET /api/frameworks/mappings | Twelve starter control topics and project-authored partial relationships |
| GET /api/frameworks/coverage | Distinct local mapped/evidence-backed control counts and unknown references |

These routes do not change a record or contact NIST/ISO. JSON catalogs ship with
the application and are versioned. Coverage recognizes exact canonical reference
strings from the pack. A matching title is not a mapping. Custom references are
retained; those absent from this selected pack appear as unknown for human review.

Evidence-backed counts require effective local control status and fresh approved
evidence under the same cadence rules as the dashboard. They do not mean that
every mapped external requirement was tested or satisfied. No full-framework
percentage or equivalence score is returned.

Both HTTP and CLI exports include framework_catalog, framework_mappings, and
framework_coverage snapshots alongside the current registers. This preserves the
reference-pack version used when the report was generated.
