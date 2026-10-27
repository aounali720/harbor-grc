# Governance operating model

The purpose of this program is to make security decisions accountable and repeatable. The Northstar scenario uses a small risk council because unresolved tradeoffs need a business owner, not another dashboard. The roles and service levels here are proposed operating procedures; the application records related data but does not schedule meetings or enforce management authority.

## Roles and decisions

| Activity | Executive sponsor | GRC lead | Control/service owner | Platform / Engineering | Independent reviewer |
| --- | --- | --- | --- | --- | --- |
| Approve scope, risk appetite, funding | A | R | C | C | I |
| Assess business risk | A for escalated decisions | R | A for owned scenario | C | C |
| Design and operate control | I | C | A | R | C |
| Select test sample and assess evidence | I | A | C | C | R |
| Remediate a finding | I | C | A | R | C |
| Approve supplier use | A for material exceptions | C | A for service | C | R for assessment |
| Accept high/critical risk | A | R for record | C | C | C |
| Present program status | A | R | C | C | C |

R = performs the work; A = accountable decision owner; C = consulted; I = informed. An executive is accountable for escalation while a service owner remains accountable for day-to-day risk decisions in their domain. Resolve overlapping authority in the decision record before work starts.

A GRC application account role is a technical permission. It is not a job title. An `admin` can manage application accounts; that does not make them the executive authorized to accept business risk. An `auditor` account supports read-only inspection. Evidence approval should be performed by a qualified person other than the person who submitted it, using an allowed write role.

## Working cadence

| Cadence | Participants | Inputs | Required output |
| --- | --- | --- | --- |
| Daily triage when critical items exist | GRC lead and affected owner | New findings, incidents, critical exceptions | Containment/ownership decision with next review |
| Weekly operations review, 30 minutes | GRC lead, engineering/platform owners | Overdue findings, upcoming evidence expiry, blocked work | Updated owners/dates and escalation list |
| Monthly risk council, 45 minutes | Sponsor, GRC lead, service owners | Top scenarios, changed residual risk, supplier decisions | Decisions, funding, accepted exceptions, expiry dates |
| Quarterly assurance review | GRC lead, independent reviewer, owner delegates | Test results, stale evidence, changed populations | Revised test plan and current/target posture |
| Annual scope/appetite review | Sponsor, business owners, legal/privacy as relevant | Business model, data flows, obligations, incident trends | Approved scope, policies, appetite, budget |

A failed control, suspected incident, new privileged supplier, acquisition, or material data-flow change triggers review outside the calendar. Waiting for the quarterly meeting is not appropriate for active exposure.

## Decision record quality

Record the question, options, facts and uncertainties, business consequence, decision maker, rationale, date, follow-up owner, and review/expiry. Link records by ID where practical. “Management approved” with no named decision maker or dated evidence is insufficient. Meeting notes may be stored in the controlled evidence repository; use a metadata reference in Harbor if they support a control.

Write policies as obligations people can perform. “Maintain least privilege” needs a defined population, review owner, review frequency, exception route, and revocation verification. Use [information security policy](../templates/security-policy.md) and [access review](../templates/access-review.md) templates as starting points.

## Management reporting

Report changes and decisions, not an unsupported “compliance score.” A useful one-page report contains three material risk scenarios, one service-impact concern, overdue high/critical work, vendor exceptions, evidence/test coverage, and specific decisions needed.

| Measure | Defined denominator | Interpretation and caveat |
| --- | --- | --- |
| Current evidence coverage | All in-scope applicable controls, with exclusions documented | Current approved evidence is a coverage signal; it does not prove complete operating effectiveness |
| Overdue finding count | Open/in-progress findings with a due date before the report date | Also report undated work; otherwise teams can improve the metric by removing dates |
| High/critical residual risk | Risks with an explicit residual rating in these bands | Show unrated risks separately rather than counting them as low |
| Vendor review timeliness | Active suppliers whose review is due in the period | Include suppliers awaiting an initial decision; do not hide them by omitting dates |
| Remediation cycle time | Closed findings in a defined period | Report median, range, reopened items, and severity mix |
| Acceptance expiry | Accepted risks with an expiry | Report expired and upcoming decisions; expiry does not remediate the risk |

Some measures above are review-report calculations rather than built-in dashboard fields. Label scope and as-of date when exporting. Counts from a partial inventory should be presented as partial. Keep raw numbers next to percentages so a reader can see a small denominator.

## Exception handling

A policy exception needs scope, rationale, compensating measures, owner, approver, and expiry. Tie it to the business risk and affected finding. Reject indefinite exceptions. If remediation misses its due date, update the treatment plan and obtain an explicit decision; changing the date silently removes useful accountability.

## Applying CSF 2.0

Use a scoped current/target profile to communicate desired outcomes and gaps. Selected mappings in this project are navigational labels, not evidence or assurance conclusions. The official [NIST CSF 2.0 profile guidance](https://www.nist.gov/cyberframework/profiles) supports tailoring profiles to the organization. The meeting cadence, metrics, and RACI in this file are Northstar's design choices.
