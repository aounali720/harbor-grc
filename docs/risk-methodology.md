# Risk assessment and acceptance

This method supports the Northstar scenario. Its thresholds, deadlines, and authorities are project choices. They are not prescribed by NIST and need management approval before organizational use. [NIST SP 800-30 Rev. 1](https://csrc.nist.gov/pubs/sp/800/30/r1/final) is a public reference for planning and maintaining assessments; the project does not claim to implement its complete process.

## Describe a scenario first

Use: **Because [condition], [threat/event] could occur, causing [business consequence] to [asset/process].**

Example: “Because production export permissions can change outside reviewed infrastructure code, administrator error could expose customer exports, causing confidential-data disclosure and contractual response costs.” Record affected assets, suppliers, existing controls, uncertainty, and date. Split consequences when they need materially different owners or treatments.

An issue is an observed condition. A risk concerns an uncertain future consequence. A bucket exposure finding may support several risks; ten duplicate alerts are not ten independent business risks.

## Likelihood over a 12-month planning horizon

| Value | Label | Judgment anchor |
| --- | --- | --- |
| 1 | Rare | Credible path, but unusual preconditions and verified barriers make occurrence remote |
| 2 | Unlikely | Plausible path; limited exposure and current evidence for relevant barriers |
| 3 | Possible | Realistic path; material exposure or control uncertainty |
| 4 | Likely | Repeated exposure, relevant incidents, or significant gaps make occurrence reasonably expected |
| 5 | Very likely | Event is recurring, active, or readily repeatable |

These are ordinal anchors, not calibrated probabilities. Record reasons, confidence, and information that could change the judgment in the narrative. No past incident is weak evidence when detection has not been tested.

## Impact if it occurs

Use the highest credible material impact across confidentiality, integrity, availability, financial loss, and customer/contract effects. Avoid counting overlapping consequences twice.

| Value | Label | Scenario anchor |
| --- | --- | --- |
| 1 | Negligible | Internal inconvenience; quickly corrected without meaningful customer effect |
| 2 | Minor | Limited degradation or small, reversible internal data error |
| 3 | Moderate | Customer-visible outage or contained disclosure requiring coordinated response |
| 4 | Major | Material customer harm, prolonged disruption, significant expense, or loss of a key contract |
| 5 | Severe | Widespread sensitive-data compromise, sustained loss of core service, or threat to business viability |

An organization should add approved monetary/service anchors based on its finances and contracts. The generic project avoids inventing amounts as industry benchmarks.

## Scores and priority

`score = likelihood × impact`, from 1 to 25. These bands match the application.

| Score | Band | Proposed response |
| --- | --- | --- |
| 1–5 | Low | Owner review at least annually; track material changes |
| 6–11 | Medium | Treatment or documented acceptance; quarterly review |
| 12–19 | High | Plan within 10 business days; target remediation within 30 calendar days |
| 20–25 | Critical | Executive escalation within one business day; immediate containment decision and daily review until stabilized |

Management still decides priority. Suspected active disclosure goes directly to incident response regardless of score. A score of 12 is not twice the risk of 6, and an average of scores is not expected loss. Consider exposure, concentration, cost, deadlines, and uncertainty alongside the matrix.

## Inherent, residual, and target

**Inherent** is the assessment before crediting the specified controls. State which controls were excluded so the counterfactual is understandable.

**Residual** is the assessment under current, evidenced conditions. The assessor supplies likelihood and impact with rationale and review date. Linking controls earns no mathematical discount. Unverified controls do not justify a lower score.

**Target** is the desired post-treatment state. Keep it in the treatment narrative until implementation and retest are complete. Do not enter an anticipated target as current residual risk.

Example: export exposure begins at likelihood 4, impact 4, score 16. Reviewed changes, access blocks, and an independent access test may support residual likelihood 2. Impact may remain 4 because disclosure would still cause major harm. “Implemented” alone supports neither change.

## Treatment and acceptance

Choose mitigation, avoidance, transfer/sharing, or acceptance. Insurance and contract terms may alter financial recovery but do not remove technical exposure. A plan needs an owner, due date, resources, measurable closure conditions, and an explanation of remaining risk.

Proposed authority: low/medium acceptance by the business owner after security review; high acceptance by the executive sponsor with the owner; critical acceptance through an executive decision with compensating measures and near-term review. Harbor checks workflow fields and actor separation; it cannot establish real budget or executive authority.

Acceptance records the scenario, residual assessment, reason for deferral, alternatives, compensating measures, approver, expiry, and reopening triggers. Proposed maximum durations are 180 days for low/medium, 90 days for high, and 30 days for critical. These duration limits are governance procedures, not automated policy limits in the application. Renewals require a fresh decision. Incidents, expired evidence, new access, or supplier changes can trigger reassessment earlier.

Use the [risk decision template](../templates/risk-decision.md). The submitter must not approve their own acceptance. If a small team lacks independence, escalate to a qualified manager or external reviewer and document the limitation. A second account operated by the same person is not an independent review.

## Review quality

A reviewer should reconstruct the assessment from scope, date, assumptions, evidence, and rationale. Challenge low scores, double-counted barriers, stale evidence, and unexplained changes. Preserve previous versions. Reassess after incidents, material architecture/supplier changes, control failures, and scheduled review dates.
