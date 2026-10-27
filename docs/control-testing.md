# Control testing, evidence, and audit

The application can check whether an evidence record has an independent approver and is within its validity period and control test cadence. It cannot determine whether a screenshot is genuine, a population complete, or a sample representative. Those are assessment tasks. This guide defines the work that should support a meaningful approval.

## Design before execution

For each control, describe the responsible owner, intended risk reduction, trigger/frequency, population, required action, retained evidence, exception path, and reviewer. A control such as “quarterly access review” needs all in-scope accounts, a clear decision for each access item, removal follow-up, and verification. A meeting invite is not evidence that the review happened.

Distinguish **design adequacy** (would the control address the scenario if performed?) from **implementation** (has it been established?) and **operating effectiveness** (did it work consistently in the defined period?). The application's single status is a summary. The test record must preserve the scope and limitations behind it.

## Test plan

Use the [control test template](../templates/control-test.md) before collection. State period, source population, completeness checks, selection method, sample size, expected result, evidence, and failure rule. Select samples independently of the operator where possible. Explain substitutions and exclusions.

Proposed Northstar approach:

| Control type | Test approach | Limitation to record |
| --- | --- | --- |
| Rare critical event, such as emergency access | Inspect every event in the period and verify the zero-event claim against logs if none exist | A period with no event tests readiness/design, not actual event operation |
| Quarterly access review | Inspect all reviews in the assessment period and sample resulting revocations | A signed review without closure evidence is incomplete |
| Frequent deployment approval | Reconcile deployment population; choose examples across the period, operators, and change types, including an emergency change when present | A judgmental sample does not support a statistical confidence claim |
| Automated configuration guardrail | Inspect configuration, coverage and change history, then perform an approved positive/negative test with synthetic data | One point-in-time observation does not establish uninterrupted operation |
| Recovery | Observe a scoped restore and validate data, dependencies, application use, and measured loss/time | A successful database restore alone does not establish service recovery |

Sample sizes must follow population size, frequency, variability, criticality, and the intended conclusion. “Five samples for every control” has no defensible universal basis. Document why the chosen work is enough for the stated conclusion and where it is not.

## Evidence record

Maintain the actual artifact in an approved repository. Record its descriptive title, control, owner, collection date, expiry, HTTPS reference, and SHA-256 of the exact retained bytes. Calculate the checksum after approved sanitization if storing a sanitized artifact; if retaining both original and sanitized forms, label each and preserve their relationship securely.

Use structured exports when possible. Include the data source, scope, time zone, filters, extraction method, and reviewer conclusion. Redact secrets and unnecessary customer data before sharing. Keep an unredacted original only where authorized and needed. The public sample references are placeholders and do not point to assessed evidence.

A checksum detects byte differences relative to the recorded value. It does not prove authorship, correct scope, collection time, or truth. Harbor stores metadata and does not download or inspect the referenced file. References must use HTTPS without embedded credentials or a query string; use a stable controlled artifact reference rather than a signed download URL.

## Review and failure handling

Submit evidence as `pending`. The independent reviewer checks relevance, completeness, period, accuracy, restrictions, and test result. They set `approved` or `rejected` and record specific notes. The reviewer must not be the creator, and approval is not a substitute for qualifications or real independence.

An effective control requires approved evidence that is unexpired and fresh enough for the control frequency: collection date plus frequency days must not be before the current UTC date. A distant expiry does not override an overdue test cadence. If evidence expires or is rejected, reconsider the control's current assurance posture and the related risk. Do not reuse an old artifact with a new date to preserve a green metric.

On a failed test, open a finding with observed condition, expected condition, affected population, consequence, owner, severity, due date, and measurable remediation. Preserve the failed artifact. After remediation collect fresh evidence, obtain independent review, and link it for closure. A control passing later does not erase an exception earlier in the period.

## A practical audit walkthrough

1. Agree scope, period, criteria, access rules, deliverables, and reporting authority. The selected CSF mappings are context, not an audit opinion.
2. Export a dated register snapshot. Reconcile in-scope assets, suppliers, controls, and known gaps. Record exclusions.
3. Select one material risk and trace it through controls, test plan, evidence, review, finding, treatment, retest, and decision.
4. Trace in reverse from a cloud/vendor observation to its asset/service owner and business consequence. This exposes orphaned alerts and unsupported risk claims.
5. Inspect version conflicts, approval identity, dates, exceptions, and changes after the assessment period. Ask who can alter the underlying database and repository.
6. Record results with criteria, condition, cause where supported, consequence, action owner, and response date. Separate observed facts from assumptions.
7. Present unresolved scope/evidence limitations and remaining risk. Agree follow-up, then verify closure independently.

Use read-only auditor accounts where appropriate. Actual auditor independence, engagement standards, professional judgment, and legal obligations are outside what this repository can establish.

## Audit trail assurance boundary

A hash chain helps detect modification relative to its retained history. A database administrator who can rewrite the entire chain or replace the database can defeat a local-only check. It is not immutable storage or a digital signature. Export checkpoints to a separately controlled location and retain backups if stronger tamper evidence is required. Test restoration and verify the trail after restore.

Do not publish an organizational audit export to demonstrate the portfolio. Build the demonstration from the fictional dataset and state that the evidence and decisions are simulated.

