# Framework assessment plan — working template

**Engagement/project:** [ ]. **Status:** [draft / approved / revised / closed]. **Sponsor:** [ ]. **Assessment lead:** [ ]. **Independent reviewer:** [ ]. **Plan version/date:** [ ].

This plan defines what will be assessed and the limits of the conclusion. It does not grant assessment access, authorize production changes, or establish certification. Tailor procedures with the actual criteria and service owners before execution.

## 1. Purpose and criteria

**Business decisions supported:** [ ]. **Assessment type:** [readiness / design review / implementation review / operating-period review / other]. **Period/as-of date:** [ ]. **Intended audience and permitted claims:** [ ].

| Selected reference | Exact edition/release and source | Why applicable to this scope | Criteria/outcomes selected | Tailoring/parameters/exclusions | Responsible approval |
| --- | --- | --- | --- | --- | --- |
| [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |

Separate outcome frameworks, control catalogues, assessment procedures, baselines, lifecycle processes, and ISMS requirements. Record the organization's actual obligation rather than inferring a mandate from a publication's existence. If CUI is involved, confirm the data boundary and agreement-specific requirements/revision with the appropriate authority.

**Mapping pack and version:** [ ]. **Contributor/direction/limitations of other mappings:** [ ]. **Authorized ISO standard access/reference, when needed:** [ ].

## 2. Boundary and populations

**Services/processes/data:** [ ]. **People/identities/suppliers:** [ ]. **Accounts/regions/environments/locations:** [ ]. **Interfaces and inherited controls:** [ ]. **Exclusions and consequences for conclusions:** [ ].

| Population | Authoritative source / extraction scope and date | Completeness reconciliation | Known gaps / resolution owner |
| --- | --- | --- | --- |
| [ ] | [ ] | [ ] | [ ] |

A source export must be scoped and reconciled. One account/region, one supplier report, or a convenient sample cannot establish enterprise coverage.

## 3. Methods and work program

Use examination, interviews, and testing as appropriate. Select rigor based on the intended decision, risk, population variability, evidence quality, and relevant assessment procedures. SP 800-53A is a procedure reference; using these method names alone does not establish compliance with it.

| Objective / criterion reference | Internal control and implementation | Method / specific steps | Population / sample method, size, reason | Expected evidence/result | Assessor / timing | Limitation/failure rule |
| --- | --- | --- | --- | --- | --- | --- |
| [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |

**Handling a zero-event population:** [readiness/design conclusion and limits]. **Substitution rules:** [ ]. **Missing/contradictory evidence:** [record unknown/failure and escalate; do not infer a pass]. **Retest process:** [retain initial exception and assess fresh evidence].

## 4. Access, evidence, and safety

**Approved assessment access and authorizing owner:** [ ]. **Read-only versus controlled test activities:** [ ]. **Production impact limits / stop conditions / contacts:** [ ]. **Synthetic test fixtures:** [ ].

**Evidence repository and access:** [ ]. **Collection scope/time zone/filters:** [ ]. **Integrity/provenance:** [exact bytes, checksums, source, collector, dates]. **Retention/deletion and confidential report restrictions:** [ ]. **Independent review:** [ ].

Harbor stores evidence metadata, not the artifact contents. Validate relevance and authenticity through the assessment process. Use stable HTTPS references without embedded secrets or signed-query tokens; retain actual artifacts in approved storage. A checksum does not establish truth or full-population coverage.

## 5. Evaluation and decisions

**Result vocabulary:** [supported / partially supported / unsupported / not assessed, with definitions]. **Severity/priority method:** [ ]. **Finding contents:** [criteria, observed condition, scope, consequence, owner, due date, measurable closure]. **Residual risk review:** [ ]. **Authorized acceptance route:** [ ].

**Reporting:** [scope, period, methods, sample limits, evidence gaps, exceptions, decisions, follow-up]. **Management response owner/deadline:** [ ]. **Independent quality review:** [ ]. **Retest and next assessment:** [ ].

Do not report a framework-wide percentage when only starter mappings were tested. Do not convert coverage into a CSF Tier, an ISO certificate, or an authorization decision. Define denominators and state which requirements were not assessed.

## 6. Approval and change record

| Approval/review | Person and actual authority | Date | Controlled reference / conditions |
| --- | --- | --- | --- |
| Scope and criteria | [ ] | [ ] | [ ] |
| Assessment access and test safety | [ ] | [ ] | [ ] |
| Evidence handling | [ ] | [ ] | [ ] |
| Plan quality/independence | [ ] | [ ] | [ ] |

**Material changes after approval and reassessment of impact:** [ ]. **Version history:** [ ].

## Fictional worked example — privileged supplier use

**Objective:** assess whether Northstar's production suppliers have appropriate access decisions and follow-up. **Selected references:** CSF GV.SC-04 as a prioritization topic; ISO/IEC 27001:2022 A.5.19 as a partial supplier topic. These are selected links, not equivalent requirements.

**Population:** all production integrations, reconciled across a synthetic procurement list and identity inventory. **Work:** examine intake/approval records, interview the service owner, and perform an authorized revocation test with a synthetic integration. Inspect every privileged supplier because the fictional population is small. Record missing suppliers and unknown access as gaps.

**Expected evidence:** dated reconciliation, decisions and authority, scoped permissions, test results, and outstanding exceptions. **Conclusion limit:** this work can support the selected supplier assessment; it does not assess the entire CSF, the complete ISO ISMS, or real supplier controls. **Actual test result:** not executed; fill only after completing the approved work.

## Optional incident-response workstream

**Reference:** [NIST SP 800-61 Rev. 3](https://csrc.nist.gov/pubs/sp/800/61/r3/final), final 2025-04-03. **Selected CSF outcomes and approved incident-profile scope:** [ ]. **Exercise objectives:** [ ]. **Current service/supplier/logging dependencies and limitations:** [ ]. **Authorized participants and decision makers:** [ ].

| Decision or capability to examine | Evidence / approved safe method | Demonstration versus discussion limit | Observer / expected result | Gap, retest, and accountable owner |
| --- | --- | --- | --- | --- |
| Declaration and authority | [ ] | [ ] | [ ] | [ ] |
| Supplier and service coordination | [ ] | [ ] | [ ] | [ ] |
| Containment and credential dependencies | [ ] | [ ] | [ ] | [ ] |
| Recovery verification and business return | [ ] | [ ] | [ ] | [ ] |
| Communications and applicable specialist review | [ ] | [ ] | [ ] | [ ] |

Use the [tabletop](../docs/incident-tabletop.md) and [action log](incident-action-log.md). The table is a project test structure, not a reproduction of every published recommendation. Do not perform live containment or send notifications through an exercise plan without the relevant operational authorization. Report untested capability as untested, then approve and verify follow-up work.
