# Release verification

## Version 1.1.2 — local account setup, 2026-10-27

The full suite passed **113 tests** on Windows / CPython 3.11.15, with the existing
upstream TestClient adapter warning. Ruff passed. The suite completed in about
92 seconds.

Eighteen operator-credential tests cover random local generation, successful
14/128-character interactive initialization, retries and cancellation, hash-only
database storage, output only after commit, session revocation, and narrowly
scoped username lockout clearing. A separate HTTP test creates an administrator
using --generate-password after ten failed bootstrap attempts, then verifies a
successful browser-style login and a credential-free report.

All credential tests use temporary databases. No test creates, resets, reads, or
prints the user's actual password. Shared IP throttling remains enabled. The new
option prints a generated secret only in the terminal where an operator explicitly
runs the account command.

## Version 1.1.1 — framework update, 2026-10-27

| Check | Observed result | Scope |
| --- | --- | --- |
| Full Python suite | **94 passed**, one upstream TestClient adapter warning | Windows / CPython 3.11.15 |
| Framework-specific tests | 19 passed, included in the full suite | Exact references, evidence freshness, explicit demo opt-in, all six selected CSF Functions, and reference-only guidance |
| Python / JavaScript checks | Ruff and Node syntax checks passed | No added runtime dependencies |
| Browser smoke | CSF acronym/edition search, ISO publisher filter, edition/source labels, Respond mapping and linked local control verified | Authenticated synthetic workspace; no console errors observed |
| Packaging | Version 1.1.1 source distribution and wheel built | Both framework JSON files included |
| Publication/data review | 12 catalog records, 12 starter topics, 79 explicitly partial links | Official NIST/ISO sources checked 2026-10-27; original project mapping rationale |

The full suite completed in approximately 62 seconds. The library includes NIST
SP 800-61 Rev. 3 as reference guidance and a selected CSF RS.MA-01 association for
the supplier incident topic. A reference-only publication correctly has zero
inferred mapped controls; that is not an assessment result.

The existing tagged synthetic preview received one new reference through the
audited demo-mapping command. Its other references were preserved. Real workspace
records are not automatically remapped. The demonstration snapshot was regenerated
with the current seed and framework metadata.

Runtime dependency versions did not change. The advisory result below remains the
2026-10-26 scan; this framework-only update did not refresh that scan. Docker, remote
CI, independent assessment, and target-environment acceptance remain unverified.

## Historical verification — version 1.0.0

Verified on **2026-10-26** against the delivered version 1.0.0 source.

## Observed results

| Check | Result | Practical limit |
|---|---|---|
| Python tests | **73 passed** | Windows, CPython 3.11.15; one upstream TestClient deprecation warning |
| Python lint | Ruff passed | Focused error/undefined-name rules in pyproject.toml |
| JavaScript syntax | Node syntax check passed | Does not prove every browser interaction |
| Runtime dependency audit | No known vulnerabilities found in 14 pinned packages | PyPI advisory snapshot; not a security certification |
| Packaging | Source distribution and wheel built | Runtime wheel includes Python modules and static console |
| Local server | Live/ready endpoint and browser sign-in succeeded | Loopback preview, synthetic records |
| Browser smoke | Dashboard, control creation, vendor listing and audit view verified | Desktop and narrow layouts inspected; not a full browser/device matrix |
| Backup/restore | Automated record and audit-chain round trip passed | Temporary database; no host recovery or encrypted-backup acceptance |

The final test run completed in approximately 57 seconds. This is execution time
in the authoring environment, not a production performance measurement.

## What the tests protect

The domain suite verifies reference integrity, strict risk scales, reviewer stamping,
evidence date/cadence freshness, finding-to-control evidence binding, bounded
acceptance, optimistic updates, duplicate source keys, transactional rollback,
seed consistency, and audit-chain tampering.

HTTP tests verify anonymous denial, session hashing, role enforcement, origin and
CSRF checks, input-redacted validation, body caps, secure production cookies,
session expiry/revocation, login failure persistence, cloud asset matching,
import rollback, and credential-free report exports.

Review regression tests verify that a submitter cannot approve their own revised
evidence, newer cloud failures reopen closed/accepted findings, stale source
snapshots cannot overwrite triage, timestamps require timezones, failed backups
do not leave a partial file, destinations are reserved exclusively, and readiness
rejects missing tables or incompatible schema metadata.

The local browser smoke created one additional synthetic control in the preview
database. The seed remains 12 controls; screenshots and exported fixtures may
represent different points in that local demonstration.

## Dependency evidence

The machine-readable advisory result is [runtime-audit.json](runtime-audit.json).
The exact runtime and development versions are in the repository locks.
No dependency was upgraded automatically as a remediation during this release.
A negative advisory scan cannot detect unpublished vulnerabilities or design flaws.

The upstream Starlette TestClient warns that its httpx adapter is deprecated.
The installed adapter works and all tests pass. This warning is retained visibly,
rather than suppressed. Review the supported test adapter when updating dependencies.

## Still requiring validation

- Docker image build, TLS proxy integration, Linux and Python 3.12 execution.
- GitHub-hosted CI execution after the repository is published.
- Load/soak tests, host capacity, application/proxy lockout behavior under attack.
- Independent penetration testing and organizational authorization review.
- Backup encryption, retention, monitoring, offsite checkpoint custody and actual recovery time.
- Accessibility audit with assistive technology and a supported-browser matrix.
- Organization-specific framework mappings, legal obligations and control operating effectiveness.

The workflow file schedules some of these engineering checks in CI; it does not
mean those remote checks have already succeeded. See [deployment](deployment.md)
for the acceptance process before real workplace use.

