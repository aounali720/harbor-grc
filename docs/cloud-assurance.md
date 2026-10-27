# Cloud assurance baseline

This baseline is a manual assurance plan for the fictional AWS estate in [the case study](case-study.md). Harbor stores asset, finding, risk, control, and evidence records; it is not an AWS scanner and does not provision or repair cloud resources. Check actual service availability and the organization's architecture before adopting a test.

## Responsibility and scope

AWS protects underlying cloud infrastructure; the customer's responsibilities depend on the chosen service and configuration. A managed database reduces infrastructure tasks but leaves customer duties such as data access, credentials, configuration, and recovery decisions. Record who owns each customer-side task instead of marking a service “covered by AWS.” See the [AWS shared responsibility model](https://aws.amazon.com/compliance/shared-responsibility-model/).

Before collection, list production/nonproduction accounts, enabled regions, excluded services, account/region coverage of security tooling, and the observation window. Obtain read-only assessment access through the organization's approved identity process. Do not use root credentials or create broad permanent keys for this project. A regional scanner result cannot establish coverage of an entire organization.

## Proposed tests

The descriptive test keys below are handbook references, not permanent application record IDs. Frequencies and closure criteria are project-defined. Reconcile them with threat exposure, change frequency, contracts, and operational capacity.

| Key / objective | Procedure and population | Sufficient evidence | Frequency / owner |
| --- | --- | --- | --- |
| CLD-01: private export storage | Reconcile all export buckets with inventory. Check account and bucket public-access settings, bucket policies, ACL use, and intended access paths. Test an authorized export and an unauthorized request without fetching customer content. | Dated configuration export, complete bucket population, policy review, sanitized negative-test result, approved exceptions | On change plus monthly / Platform |
| CLD-02: protected privileged identity | Enumerate privileged human and workload paths. Verify federated access, MFA enforcement, scoped roles, emergency access, and root account safeguards. Review unused credentials and overly broad policies. | Identity/role inventory, enforcement configuration, approval record, last-use review, revocation test | On change plus quarterly / IT + Platform |
| CLD-03: durable audit logging | Reconcile accounts/regions with trail coverage. Inspect logging state, relevant event selection, destination permissions, retention, validation settings, and monitoring. Generate an approved benign event and trace it to the destination. | Trail configuration, source population, delivery timestamps, event trace, destination access review | Monthly and after logging changes / Platform |
| CLD-04: database access boundary | Inspect database public-access configuration, subnet routes, security groups, authorized clients, and administrative paths. Verify encryption settings and transport enforcement appropriate to the engine. | Dated instance/cluster inventory, networking/configuration exports, approved connection tests | On change plus monthly / Platform |
| CLD-05: recoverable backups | Check retention, restore permissions, protection against deletion, and dependency coverage. Restore a representative dataset in an isolated approved environment; verify application consistency and measure loss/time. | Restore log, measured RTO/RPO, data validation, dependency checks, cleanup record, reviewer conclusion | Quarterly and after material changes / Service owner |
| CLD-06: constrained network ingress | Reconcile externally reachable services against architecture. Review broad ingress, administrative ports, security group relationships, and documented public endpoints. Test only approved endpoints. | Complete exposure population, configuration changes, connectivity results, exceptions | Monthly / Platform |
| CLD-07: controlled deployment | Trace a production release from change request to reviewed source, checks, artifact, scoped deployment identity, and rollback. Verify branch protections and emergency change follow-up. | Release sample, approval/check records, deployment identity scope, rollback evidence | Each release; sample quarterly / Engineering |
| CLD-08: vulnerability response | Reconcile scanner coverage with workloads and dependencies. Validate a sample's applicability, owner, due date, deployment status, and retest. Treat internet exposure and exploitation context as prioritization inputs. | Coverage report, triage rationale, patch/change record, retest, accepted exceptions | Weekly triage / Engineering |
| CLD-09: secret handling | Review where application/deployment credentials are stored, who can read them, rotation triggers, and log redaction. Trace one controlled rotation and verify old credential revocation. | Secret-store metadata without values, permissions, rotation/revocation record | Quarterly and after suspected exposure / Platform |
| CLD-10: tenant authorization | Test representative API, background job, and export paths with two synthetic tenants. Confirm identifiers cannot override tenant context and support access is constrained/logged. | Test design, synthetic fixtures, negative-test outcomes, defect/retest records | Each relevant change plus quarterly / Engineering |

A screenshot may show a selected setting while omitting accounts, regions, other policy layers, or the observation period. Prefer structured exports with a clear population. Never put credentials, customer payloads, unrestricted account identifiers, or raw production logs in the public repository.

## Interpreting AWS checks

The official [S3 control reference](https://docs.aws.amazon.com/securityhub/latest/userguide/s3-controls.html) distinguishes account-level and bucket-level checks. Check both relevant layers; one passing result is not a complete access assessment. An approved public website bucket has a different purpose from private customer export storage.

The [IAM reference](https://docs.aws.amazon.com/securityhub/latest/userguide/iam-controls.html) documents the scope of individual policy checks. A check for one form of wildcard administrative policy does not prove all identities are least privileged. Review inline, managed, federated, workload, and emergency access paths as applicable.

The [CloudTrail reference](https://docs.aws.amazon.com/securityhub/latest/userguide/cloudtrail-controls.html) describes specific logging checks. The project additionally asks whether a relevant event arrives where responders can use it. “Enabled” without delivery, access, and retention checks is incomplete assurance.

The [RDS reference](https://docs.aws.amazon.com/securityhub/latest/userguide/rds-controls.html) includes separate checks for public access, encryption, and backups. Configuration conformance is one input; a measured restore exercise establishes a different kind of evidence.

## Findings and imports

When using an exported AWS Security Finding Format document, preserve the original export in the approved evidence store, record collection time and scope, and sanitize a separate copy before public sharing. [ASFF documentation](https://docs.aws.amazon.com/securityhub/latest/userguide/securityhub-findings-format.html) defines the exchange format. The application supports a bounded subset; read its import documentation and validate the result rather than assuming support for every ASFF attribute.

A repeated observation should update triage context without erasing the owner's remediation narrative or silently closing a finding. A provider's `PASSED`, `RESOLVED`, or archived state needs interpretation against the affected asset and test period. Keep business risk, scanner severity, and remediation priority distinct.

## Worked closure condition

For export exposure, an adequate closure condition is: all scoped export buckets have the approved access configuration; the authorized workflow still works; an unauthorized request cannot access a synthetic object; the deployment path prevents or detects drift; a qualified independent reviewer confirms the scope and results. Link the current approved evidence to the finding and retain the failed observation. Reassess residual risk separately.
