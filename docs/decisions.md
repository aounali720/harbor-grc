# Design decisions

These decisions describe the delivered implementation and the tradeoffs behind it. They are a starting point for changing the project deliberately, rather than assumptions that every team should adopt.

## 1. Keep risks and findings separate

A finding records an observed condition. A risk explains the uncertain business consequence. Harbor stores them separately and allows a finding to reference a risk, control, asset, and supplier. Several observations can therefore inform one business scenario without turning every scanner alert into a new risk.

This adds a linking step and leaves the analyst responsible for the relationship. The benefit is a usable distinction between fixing an issue and deciding what exposure remains. A future grouping or deduplication feature should preserve source observations, explain suggested links, and let an analyst correct them.

**Implementation:** [record schemas](../harbor_grc/schemas.py) and [domain reference checks](../harbor_grc/domain.py).

## 2. Record residual risk as a reviewed assessment

The application multiplies the entered likelihood and impact values to show a score. It does not reduce that score because controls were linked or evidence was approved. A residual rating needs both values, a rationale, and a review date; the domain layer records the acting reviewer.

That takes more judgment than an automatic discount, but a control count cannot establish how much a particular loss scenario changed. Unknown residual risk stays visible. Any future quantitative model should document assumptions, uncertainty, calibration, and an override/review process before its output influences decisions.

**Implementation:** [risk validation and reporting](../harbor_grc/domain.py) and [risk method](risk-methodology.md).

## 3. Store evidence metadata, with artifacts elsewhere

An evidence record contains a control reference, stable HTTPS URI, SHA-256, collection/expiry dates, and review information. Harbor neither uploads the artifact nor follows its URL. References with credentials or query strings are rejected to reduce accidental storage of embedded download tokens.

This keeps a confidential-file service out of the application. It also means the organization must operate the evidence repository, retain the right bytes, and keep them retrievable. The digest identifies bytes relative to the recorded value; it does not establish truth. A future connector should preserve this provenance while adding explicit authorization, access checks, retention behavior, and failure handling.

**Implementation:** [evidence fields](../harbor_grc/schemas.py), [workflow checks](../harbor_grc/domain.py), and [evidence review](control-testing.md).

## 4. Start with one organization and SQLite

The initial deployment uses one application worker and a SQLite database on local disk. Updates and their audit events commit in the same transaction; expected record versions reject stale edits. This is a compact setup that a small team can inspect, back up, and run without a separate database service.

The cost is limited concurrency and availability. Every authenticated account can read every register, so membership is a confidentiality decision; this is not a tenant-isolated service. Move beyond this design when measured contention, isolation requirements, or recovery/availability objectives require it. A database change should include migrations, concurrent-write tests, restore/rollback tests, and a revised deployment plan.

**Implementation:** [database transactions](../harbor_grc/db.py), [version checks](../harbor_grc/domain.py), and [architecture](architecture.md).

## 5. Require a different actor for approval

Evidence starts as a submission. Its creator or current submitter cannot approve it, changed content must be submitted for review again, and approval needs review notes. Effective controls and finding closure need current approved evidence within the control's test cadence. Risk acceptance likewise requires someone other than the record creator, plus a reason and future expiry.

These gates make unchecked self-approval harder. They do not establish a person's competence, real independence, or executive authority. An admin/analyst role can perform permitted record actions without an organization-specific approval hierarchy. A future delegation model should cover authority limits, substitutes, revocation, escalation, and attempts to bypass the intended approver.

**Implementation:** [approval and freshness gates](../harbor_grc/domain.py) and [role/authority boundary](architecture.md#permissions).

## 6. Make framework links explicit and partial

The framework pack contains versioned publication metadata and selected references. Coverage recognizes exact curated reference strings and counts distinct local controls; it does not infer a mapping from a control title. Unknown-to-pack references remain visible. Each starter link states that its contribution is partial.

This makes counts explainable and avoids silently treating a topic match as equivalence. It also creates curation work and leaves most criteria outside the starter pack. Add a reference only after checking its edition, scope, contribution, untested parts, and source. A future mapping import should preserve contributor/version/direction and allow review before it changes organizational records.

**Implementation:** [framework helpers](../harbor_grc/frameworks.py), [mapping pack](../harbor_grc/data/control_mappings.json), and [crosswalk limits](framework-crosswalk.md).
