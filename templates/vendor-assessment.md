# Supplier assessment and use decision

**Supplier/service:** [ ]. **Business sponsor:** [ ]. **Assessment owner/date:** [ ]. **Proposed use:** [ ]. **Status:** [screening / due_diligence / approved / conditional / rejected / offboarded].

## Intake and tier

| Input | Actual proposed arrangement | Evidence/source |
| --- | --- | --- |
| Business criticality and outage consequence | [ ] | [ ] |
| Data fields/classification, location, retention | [ ] | [ ] |
| Access type, privileges, and integration identity | [ ] | [ ] |
| Subprocessors and onward sharing | [ ] | [ ] |
| Export, replacement, and termination plan | [ ] | [ ] |

**Derived tier and reason:** [Tier 1 for critical/restricted/privileged; otherwise Tier 2 for high/confidential; otherwise Tier 3.] **Scope exclusions/unknowns:** [ ].

## Questionnaire review

Use 0 unknown, 1 material gap, 2 partial, 3 defined/supported, 4 tested/relevant. Complete all five before deriving a summary; `sum / 20 × 100` is a reviewer aid, not an approval rule.

| Domain | Questions | Score | Source/date | Reviewer judgment and limits |
| --- | --- | --- | --- | --- |
| Access | Can MFA/SSO and least privilege be enforced? How is support access approved, logged, and revoked? | [ ] | [ ] | [ ] |
| Data | What data is used/stored/shared, where, for how long, and how is deletion verified? | [ ] | [ ] | [ ] |
| Vulnerability response | How are issues found, prioritized, fixed, retested, and disclosed? | [ ] | [ ] | [ ] |
| Incident response | Who notifies whom, with what information, and through which verified contacts? | [ ] | [ ] | [ ] |
| Resilience/exit | What has been recovery-tested? Can data be exported and access terminated? | [ ] | [ ] | [ ] |

**Summary score, if used:** [ ]. **Material blockers regardless of score:** [ ]. **Independent assurance scope/period/exceptions:** [Summarize only permitted information; retain confidential reports in approved storage.]

## Decision

**Security conclusion and uncertainty:** [ ]. **Relevant procurement/legal/privacy review:** [ ]. **Business decision and actual authority:** [ ]. **Conditions/actions:** [gap, owner, due date, evidence, expiry]. **Linked findings/risks/acceptances:** [ ]. **Next review and triggers:** [ ].

| Approval/review | Person/role | Date | Controlled reference |
| --- | --- | --- | --- |
| Security | [ ] | [ ] | [ ] |
| Relevant specialist review | [ ] | [ ] | [ ] |
| Business service owner | [ ] | [ ] | [ ] |

## Offboarding verification

[ ] Revoke identities/tokens and remove trust. [ ] Disable integrations. [ ] Export required records. [ ] Confirm retention/deletion under approved terms. [ ] Remove downstream dependencies. [ ] Update inventory/data flows. [ ] Independent verification and dated closure.
