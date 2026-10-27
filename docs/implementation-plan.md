# A 90-day implementation plan

This plan assumes an executive sponsor, a part-time GRC lead, service owners, and engineering capacity for the highest-priority findings. It is a proposed rollout, not evidence of work completed. If an active exposure is discovered, contain and respond immediately instead of waiting for its phase.

## Days 1–15: establish the boundary

**Accountable:** executive sponsor. **Working owner:** GRC lead.

Meet the service owner, platform lead, procurement owner, and privacy/legal contacts. Confirm service objectives, customers, data categories, dependencies, and important obligations. Draw the current data flow. Reconcile assets against deployment/account inventories and suppliers against finance, identity, and integration records. Review the scope with owners and record exclusions.

Approve the initial risk method, appetite, decision authority, and recurring meetings. Create a controlled evidence location and define who can submit, review, and administer it. Deploy Harbor in an isolated environment using [deployment guidance](deployment.md), then validate permissions, backup/restore, logging, and account recovery before entering organizational information.

**Exit evidence:** approved scope and role matrix; reconciled first inventory; approved method; deployment validation record; agreed evidence handling. A list copied from a spreadsheet without reconciliation is not the exit condition.

## Days 16–30: assess and prioritize

**Accountable:** business service owners. **Working owner:** GRC lead with platform/engineering.

Run scenario workshops for tenant isolation, privileged compromise, cloud exposure, recovery, deployment integrity, and supplier disruption. Record inherent assessments and uncertainty. Identify existing controls and inspect enough evidence to avoid assuming that a policy is operating. Identify new work and assign owners.

Screen every identified supplier using actual data/access/criticality. Start Tier 1 reviews first, including suppliers already in use. Define cloud test coverage by account and region. Triage existing exported findings and remove duplicates without losing source references. Choose current/target outcomes using selected CSF identifiers only where relevant.

**Exit evidence:** reviewed risk register; prioritized treatment plans; vendor tiers and review schedule; control inventory and test plan; first management decision log. Any incomplete inventory or untested control is reported as a limitation.

## Days 31–45: operate one full assurance cycle

**Accountable:** control owners. **Working owner:** operators and independent reviewer.

Execute the highest-value control tests. Include at least privileged access, storage exposure, logging delivery, a production change, a restore, and a Tier 1 supplier. Use approved read-only/isolated assessment methods and synthetic test data. Collect artifacts, record metadata/checksums, obtain independent reviews, and open findings for failures.

Start weekly finding reviews. Validate due dates and blockages. Document risk decisions with authority and expiry. Do not mark controls effective just to complete the plan: unsupported controls remain an explicit gap.

**Exit evidence:** a complete trace from business risk to current evidence and reviewed finding; failed tests preserved; named remediation plans; a measured recovery result or an explicit inability to demonstrate recovery.

## Days 46–60: remediate and test decisions

**Accountable:** affected service owners. **Working owner:** engineering/platform plus reviewer.

Deliver agreed high-priority changes, retest them, and review evidence independently. Confirm changes did not break the business workflow. Exercise joiner/mover/leaver and vendor offboarding with controlled accounts. Hold the [incident tabletop](incident-tabletop.md). Run a restoration exercise for Harbor itself, including evidence reference availability and audit-trail verification.

Review expiring acceptances and conditional suppliers. Check that the same person is not using multiple accounts to satisfy separation of duties. Ask owners whether reporting helps them make decisions or simply adds administration.

**Exit evidence:** approved retests for completed actions; open residual items with owners; tabletop action log; verified application recovery record; documented adjustments to weak processes.

## Days 61–75: run an internal assessment

**Accountable:** sponsor. **Working owner:** reviewer with no operational ownership of sampled work.

Agree the assessment scope and period. Reconcile populations and sample across time, people, accounts, change types, and suppliers. Inspect decisions and evidence independently. Challenge stale evidence, orphan findings, missing dates, unsupported low residual scores, and exclusions.

Classify each observation by condition and business consequence. Distinguish design gaps, operating exceptions, and evidence limitations. Obtain owner responses with feasible actions. An unresolved limitation is part of the result, not a reason to omit the control.

**Exit evidence:** dated internal assessment with scope and limitations; action plan; verified register snapshot; sponsor decisions. This is an internal project assessment, not a SOC 2 report, ISO certification, or independent attestation.

## Days 76–90: establish sustainable operation

**Accountable:** sponsor and service owners. **Working owner:** GRC lead.

Repeat the monthly reporting cycle using defined denominators and as-of dates. Review whether treatment deadlines are achievable. Confirm budget and owner coverage. Set next-quarter tests, vendor reassessments, acceptance expiries, and policy reviews. Reduce duplicate record keeping where evidence can safely be referenced.

Prepare a sanitized demonstration copy from fictional data. Review the export, repository, commit history, screenshots, logs, archives, and metadata before any public release. Keep organizational evidence in approved private systems.

**Exit evidence:** approved next-quarter plan; operating cadence in calendars; accountable owners; recovery and access procedures; dated management report; reviewed public demonstration package.

## Adoption gates

Move to organizational use only when the deployment's owner has validated access boundaries, recovery, change management, retention, vulnerability handling, and the intended scale. Feature completeness is not the same as operational readiness. Record unmet items with a decision owner. See [verification](verification.md) for checks performed on the delivered build and distinguish them from tests needed in the target environment.

## First-quarter success criteria

A useful first quarter has a scoped and reconciled inventory, material risks with reasoned decisions, no orphan critical finding, current evidence for priority controls, an exercised restore, reviewed Tier 1 suppliers, and a management team that can explain its remaining risk. A green dashboard alone is insufficient.
