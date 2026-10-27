# Tabletop: a supplier token and customer export exposure

This 75-minute facilitated exercise joins SaaS governance, cloud configuration, and vendor response. All names, events, and artifacts are fictional. Run it with synthetic examples; do not change live permissions or notify real customers as part of the exercise.

## Framework context

This exercise is a project-authored scenario informed by [NIST SP 800-61 Rev. 3](https://csrc.nist.gov/pubs/sp/800/61/r3/final), finalized 2025-04-03 and replacing Rev. 2. It is a CSF 2.0 Community Profile reference for relating incident work to cybersecurity risk management. Select the relevant outcomes and document readiness/targets using the [CSF Profile template](../templates/csf-organizational-profile.md); define test scope and limits with the [assessment plan](../templates/framework-assessment-plan.md).

The scenario does not implement or assess the full publication. Adding its reference does not mean the exercise has been performed or that incident capability is proven. The facilitator should distinguish decisions discussed from actions demonstrated and results independently verified.

## Objectives and participants

Test whether the team can scope a suspected exposure, assign authority, preserve evidence, coordinate a supplier, make a customer-impact decision, and verify recovery. Include an incident commander, platform responder, application owner, GRC/evidence lead, support/business lead, and legal/privacy communications contact when relevant. A facilitator gives injects; an observer records decisions and elapsed time.

Before starting, identify approved incident channels, out-of-band contacts, access to logs, decision authority, evidence storage, and the scope of the exercise. Do not assume Harbor will be available during an incident; keep essential contacts and runbooks accessible through approved alternatives.

## Opening situation

At 09:10, a fictional support supplier reports that a diagnostic integration token may have been copied from a technician's machine. The token has access to a support workflow associated with customer export jobs. Separately, a cloud finding indicates that an export storage policy changed yesterday. There is no confirmed disclosure yet.

Ask the incident commander to state what is known, unknown, and assumed. A vulnerability observation is not proof of exfiltration; lack of a confirmed event is not proof that no access occurred.

## Injects

| Minute | New information | Decisions to surface |
| --- | --- | --- |
| 0–10 | Supplier provides a token identifier and an imprecise 24-hour window | Who declares an incident? Who contacts the supplier? What access is revoked, and who approves business impact? |
| 10–20 | One export bucket permits an unintended access path; the inventory lists two buckets but the cloud account contains three | How is scope reconciled? What containment is safe? How are logs/configuration preserved before changes? |
| 20–30 | Application logs show unusual export requests for two synthetic tenants; logs omit a field needed for attribution | What can be concluded? What other records are available? Who owns the evidence gap? |
| 30–40 | Token revocation disrupts legitimate support operations during a customer incident | What temporary workflow is acceptable? How is access limited, time-bounded, and reviewed? |
| 40–50 | A large customer asks whether its data was accessed; the supplier cannot yet confirm the compromised period | Who approves factual communications? What contractual/legal assessment is needed, and by whom? |
| 50–60 | Configuration is corrected and a new token issued, but a background job still uses an old credential | What proves revocation is complete? How are dependent workloads and all accounts checked? |
| 60–65 | A test request succeeds through the intended workflow and fails through the unauthorized path | What additional evidence supports recovery? What remains uncertain? Who accepts return to normal operation? |

Keep notification timing as an issue for the relevant contractual/legal assessment. This project does not supply jurisdiction-specific reporting deadlines.

## Record during the exercise

Use the [incident action log](../templates/incident-action-log.md). For each material decision record time/time zone, decision maker, facts, uncertainty, action, owner, expected result, and next check. Label exercise evidence clearly. Preserve source artifacts and access decisions through the approved incident process.

The GRC lead links the supplier assessment, affected assets, findings, and risk scenarios. A new control failure can require reassessment even when an earlier acceptance remains within its expiry. Do not close the incident just because all scanner findings are resolved.

## Evaluation

The observer assesses whether the team identified an accountable commander, reconciled the asset/supplier scope, contained the relevant credentials, preserved sufficient evidence, distinguished facts from assumptions, involved the right communication authority, tested intended and unintended access, and assigned improvement work.

Timing is a learning aid. Do not report invented success percentages or claim a recovery objective was met in a discussion-only exercise. Record which actions were discussed, simulated, demonstrated, or actually verified.

## Debrief and follow-up

Within two business days, record what worked, what blocked response, and what remains unproven. Convert gaps into findings with owners, dates, and observable closure conditions. Examples include an incomplete export inventory, missing log fields, unclear supplier notification route, an undocumented token dependency, or no independent post-change test.

Schedule retests for the most important gaps. Update risk assessments, supplier approval conditions, control procedures, and training. Preserve the initial exercise result alongside later improvements so a reviewer can see what changed.
