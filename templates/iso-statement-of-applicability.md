# ISO/IEC 27001 Statement of Applicability — working template

**Status:** [draft / reviewed / approved]. **ISMS scope:** [controlled scope reference]. **Owner/approver:** [ ]. **Version/as-of date:** [ ]. **Next review:** [ ].

**Criteria edition:** ISO/IEC 27001:2022 with Amd 1:2024. **Authorized standards copy/reference:** [ ]. **Related risk method/treatment plan/version:** [ ]. **Mapping pack/version:** [ ].

This document is an adaptable structure, not a completed SoA or a reproduction of Annex A. Use the authorized standard to complete the comparison. See the [standard overview](https://www.iso.org/standard/27001), [amendment](https://www.iso.org/standard/88435.html), and explanatory [ISO committee SoA note](https://committee.iso.org/files/live/sites/jtc1sc27/files/resources/ISO-IECJTC1-SC27-WG1_N3298_Auditing%20Practices%20Note%20-%20SoA.pdf). The committee note is discussion material; the standard is the assessment criterion.

## 1. Scope and control determination

**Services, data, people, locations, suppliers, interfaces:** [ ]. **Validated requirements:** [legal/contractual/business requirements, sources, responsible reviewers]. **Assessment date/period:** [ ]. **Risk assessment and selected treatments:** [ ]. **Controls necessary to perform those treatments:** [ ]. **Known gaps and pending decisions:** [ ].

Determine necessary controls from risk treatment and relevant requirements. Compare them with Annex A to check for omissions. Include organization-specific controls where needed. Do not limit the set to the 12 Harbor starter controls or copy applicability from another organization.

## 2. Necessary control register

Create a row for every necessary control, including custom controls and controls selected from other sources. Use concise original implementation language rather than copying protected standards text.

| Internal control ID / original description | Reference identifier(s), edition | Reason for inclusion / linked risk or requirement | Implementation state and scope | Accountable owner / operator | Evidence / test / limitation | Reviewer / date / next review |
| --- | --- | --- | --- | --- | --- | --- |
| [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |

“Necessary” does not mean “implemented.” Record planned, partial, implemented, or unverified states honestly and link treatment work. An excluded reference control is different from a necessary control that has not yet been implemented.

## 3. Annex A comparison and justified exclusions

Complete a comparison covering the full Annex A reference set using the authorized criteria. The small project crosswalk is insufficient for that check. This template intentionally does not reproduce the complete control list.

| Annex A identifier | Necessary control(s) addressing the topic, if included | Inclusion justification or exclusion rationale tied to actual scope/risk | Evidence supporting decision | Decision owner / reviewer / date | Reconsideration trigger |
| --- | --- | --- | --- | --- | --- |
| [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |

Explain exclusions specifically. “Cloud hosted,” “small company,” or “the supplier handles it” is not enough without examining retained responsibilities and risk. Do not use a SoA exclusion to exclude management-system requirements in Clauses 4–10.

**Full comparison completed by/date:** [ ]. **Omissions resolved:** [ ]. **Unresolved items and escalation:** [ ].

## 4. ISMS processes tracked separately

| Area | Controlled process/evidence reference | Responsible owner | Assessment result and remaining work |
| --- | --- | --- | --- |
| Context, interested parties, scope | [ ] | [ ] | [ ] |
| Leadership, policy, responsibility | [ ] | [ ] | [ ] |
| Risk method, treatment, objectives, planned changes | [ ] | [ ] | [ ] |
| Resources, competence, communications, controlled information | [ ] | [ ] | [ ] |
| Operation and review of assessments/treatments | [ ] | [ ] | [ ] |
| Evaluation, internal audit, management review | [ ] | [ ] | [ ] |
| Corrective action and improvement | [ ] | [ ] | [ ] |

This table is a coordination aid, not a substitute for assessing every applicable requirement in the authorized standard.

### Evidence and implementation gaps

Maintain this work register alongside the SoA. A necessary control stays necessary while its implementation or evidence is incomplete. Record management-system process gaps as well as technical control gaps; use the [framework guide's work-product table](../docs/frameworks.md#translate-isms-work-into-owned-evidence) to coordinate owners.

| Control or ISMS process reference | Actual gap and business consequence | Missing implementation / evidence / scope | Action owner / due date | Interim treatment or authorized risk decision | Closure test and independent result |
| --- | --- | --- | --- | --- | --- |
| [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |

**Fictional example:** the supplier-control procedure exists but the integration population has not been reconciled. Keep the necessary supplier control included, label operating assurance incomplete, assign reconciliation/testing, and preserve the uncertainty. Do not exclude the control or mark it effective to avoid reporting a gap.

## 5. Climate-context determination

**Potential climate-related issues affecting the scoped ISMS:** [ ]. **Relevant interested parties and their requirements:** [ ]. **Relevance conclusion and reasons:** [ ]. **Source/evidence and uncertainty:** [ ]. **Required changes to risk, resilience, supplier oversight, or objectives:** [ ]. **Decision owner/date and review trigger:** [ ].

Reach a scoped conclusion under Amd 1:2024. Do not insert mandatory emissions controls without a relevant requirement or risk basis. A conclusion of no identified relevance needs reasons and reconsideration triggers.

## 6. Approval and change control

**Risk owner acceptance of remaining exposure:** [separate authorized decisions and expiry]. **SoA review:** [ ]. **Authorized approval/date/reference:** [ ]. **Distribution/access:** [ ]. **Review triggers:** [scope/risk/obligation/supplier/technology/criteria change].

| Version | Change and rationale | Affected risks/controls | Reviewer/approver/date |
| --- | --- | --- | --- |
| [ ] | [ ] | [ ] | [ ] |

## Fictional worked example — two necessary controls

| Internal control | Selected reference | Inclusion rationale | State and evidence | Owner/review |
| --- | --- | --- | --- | --- |
| CUST-SUP-01: evaluate production supplier access before use and on change | ISO/IEC 27001:2022 A.5.19; selected partial topic link | Privileged suppliers can affect customer data and service access | Planned; synthetic intake only, review population incomplete | Service owner; [review date] |
| CUST-TEN-01: test tenant isolation for API, jobs, and exports using synthetic tenants | Custom control; cross-reference relevant authorized criteria after review | Tenant boundary failure is a material SaaS scenario; an application-specific test is necessary | Partial design; operating test not yet performed | Engineering owner; [review date] |

These examples are invented and are not a complete SoA or preapproved applicability decisions. No exclusion is preapproved by this template. If the fictional context identifies regional disruption as relevant to service recovery, record the reasoning and supplier/recovery actions in section 5; that does not by itself create a carbon-reporting obligation.
