# Vendor risk lifecycle

A supplier review asks whether a particular service, data flow, and access arrangement is acceptable. It does not produce a permanent judgment that a company is “secure.” A payroll service, public status-page provider, and production deployment integration need different depth of review.

This project uses lifecycle thinking informed by [NIST SP 800-161 Rev. 1, updated November 2024](https://csrc.nist.gov/pubs/sp/800/161/r1/upd1/final). The tiers, review intervals, questionnaire, and decision rules below are Northstar design choices, not NIST requirements.

## Intake before purchase or integration

The business sponsor identifies the service purpose, owner, alternatives, expected data fields, customer impact if unavailable, data locations, subprocessors, access method, and exit path. Compare the proposed integration with the system boundary. “No data stored” is insufficient if the service can read production through an API or privileged support session.

Record actual use, not only the product's marketing description. A messaging provider sending only delivery events differs from one receiving full customer exports. A change in use triggers reassessment even when the supplier's name is unchanged.

## Deterministic screening tier

These rules match the application's tier derivation. Higher tiers take precedence.

| Tier | Rule | Proposed review depth and timing |
| --- | --- | --- |
| Tier 1 | Critical business dependency **or** restricted data **or** privileged access | Full assessment before approval; review every six months and on material change |
| Tier 2 | Otherwise high criticality **or** confidential data | Targeted evidence review before approval; at least annual reassessment |
| Tier 3 | All remaining suppliers | Basic screening and documented owner approval; at least every two years or on change |

Tier expresses review priority, not an assurance result. A Tier 1 service may be acceptable with strong evidence and controls. A Tier 3 service may be rejected for an unresolved issue. The application can derive tier from entered values; it cannot verify that those values describe the real integration.

## Evidence requests

| Area | Ask for | Evaluate rather than merely collect |
| --- | --- | --- |
| Scope and assurance | Current independent assurance material, scope, period, relevant exceptions, bridge information if available | Does it cover the product, location, and service being used? What remains the customer's responsibility? |
| Identity and access | SSO/MFA support, privileged support access, approval/revocation process, access logging | Can Northstar enforce its intended access boundary? |
| Data protection | Data flow, storage locations, encryption, retention, deletion, subprocessor information | Does actual data use match the approved purpose and contract? |
| Software/service security | Vulnerability handling, independent testing summary, remediation process, disclosure contact | Are material issues managed with evidence and dates? |
| Incident response | Notification route, response responsibilities, escalation contacts | Will the organization receive useful information soon enough to act? |
| Resilience and exit | Recovery approach, test summary, export capability, termination/deletion process | Can Northstar continue or leave the service within acceptable loss/time? |

Assurance reports are often confidential. Review them in an authorized location and summarize only permitted conclusions. A report logo, certificate image, or questionnaire answer does not establish relevance or operating effectiveness. Do not upload proprietary standards or supplier reports to the public project.

## Questionnaire and scoring

Use the [vendor assessment template](../templates/vendor-assessment.md). For a simple structured review, assess five domains—access, data handling, vulnerability management, incident response, and resilience—on a 0–4 scale: 0 unknown; 1 absent or material gap; 2 partial; 3 defined and supported; 4 tested and relevant. Calculate `sum(domain scores) / 20 × 100` only when all five were assessed. Record source, reviewer, date, and uncertainty with each judgment.

Unknown is a request for evidence, not proof of failure; do not treat it as success. The optional 0–100 score in Harbor is a reviewer-entered summary, not an automatic approval rule. The application does not calculate this five-domain questionnaire for you. A high average cannot cancel a material blocker.

Proposed blockers include inability to restrict privileged access, unacceptable data use, no usable incident contact, an unresolved material exposure, or an exit dependency the business cannot tolerate. Legal/privacy specialists decide contractual and legal questions. Security provides the technical assessment and limitations.

## Decision and follow-up

Use `screening` while scope is being collected and `due_diligence` while evidence is assessed. Then record `approved`, `conditional`, or `rejected` with dated rationale in assurance notes. A conditional decision needs the gap, interim control, action owner, due date, approver, and expiry. Record its remediation work as a finding. Where the residual scenario is accepted, link the risk decision; a conditional vendor status alone is not risk acceptance.

The accountable business owner signs the operational decision after security and other relevant reviews. The application checks required data but does not replace procurement, contractual approval, or delegated authority. Keep the signed decision in the approved repository and summarize its reference in the record.

## Northstar worked example

A fictional support service, Helpdesk Cedar at `support.cedar.example`, initially sees internal ticket metadata. The sponsor requests access to customer event exports for troubleshooting. The analyst changes the proposed data sensitivity to confidential and documents the new flow. If the integration would have privileged access, the service becomes Tier 1 under the rule above.

The reviewer discovers that support administrators cannot be limited to the requested dataset. A questionnaire average of 85 would not solve this boundary problem. Options include using synthetic troubleshooting data, a mediated time-limited access workflow, another supplier, or a documented executive exception with compensating controls. Record the selected option and verify it before enabling the integration. This is a fictional assessment exercise, not an assessment of a real vendor.

## Monitoring and exit

Monitor material incidents, new subprocessors, ownership or service changes, expired evidence, access changes, and approaching renewal. Reassessment is a review of changed facts, not resending last year's form unchanged.

For offboarding, disable the integration, revoke tokens/accounts, remove trust relationships, export required records, verify retention/deletion actions under the contract, update data flows, and confirm downstream users no longer depend on the service. Keep a dated verification record before marking `offboarded`. Test a critical supplier's exit plan before the organization urgently needs it.
