# Harbor GRC

Harbor is a small GRC application for keeping risks, controls, evidence, and the
decisions around them in one place. It covers a SaaS business, its cloud
environment, and the suppliers it depends on.

The project includes a fictional company, **Northstar Metrics**, so you can work
through a realistic assessment without using customer or employer data.

**Project status:** suitable for a portfolio, learning, and controlled pilots.
Workplace deployment needs further security and operational validation.

![Harbor GRC overview](docs/images/dashboard.jpg)

## The problem it explores

A scanner can tell you that a storage bucket is exposed. It cannot decide who owns
the business risk, whether the fix was tested properly, or whether the remaining
risk is acceptable.

Harbor keeps those steps connected. In the sample scenario, a storage finding
links to an asset, a customer-impact risk, and a control. The owner records the
remediation, another person reviews the evidence, and the risk owner reassesses
the remaining exposure. A supplier review follows the same approach.

That distinction between an observation and a decision is the main idea behind
the project.

## What is included

- Six linked registers: risks, controls, vendors, assets, evidence, and findings.
- Explicit inherent and residual risk assessments, with a rationale for changes.
- Evidence review, expiry, and control test-cadence checks.
- Supplier tiers based on service criticality, data sensitivity, and access.
- Offline import of sanitized AWS Security Finding Format exports.
- An audit history, report exports, and local account and backup commands.
- A searchable library of **12 NIST/ISO publications** and **79 partial mapping
  links** across the 12 starter control topics.
- A handbook, worked case study, and reusable assessment templates.

The clean demo contains **10 risks, 12 controls, 5 vendors, 8 assets, 8 evidence
records, and 7 findings**. Some work is deliberately overdue or incomplete, so
there are useful decisions to investigate.

## Run it locally

You need Python 3.11 or later. Run these commands from the project folder.

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.lock
.\.venv\Scripts\python.exe -m harbor_grc init --admin admin --generate-password
```

The last command prints a random passphrase in your terminal. Store it privately;
you will use it to sign in as `admin`. There is no shared default password.

Load the fictional scenario and start the app:

```powershell
.\.venv\Scripts\python.exe -m harbor_grc seed-demo
.\.venv\Scripts\python.exe -m harbor_grc serve
```

Open **[http://127.0.0.1:8000](http://127.0.0.1:8000)**. Keep the terminal running;
press **Ctrl+C** to stop the server. On later visits, run only the `serve` command.

### macOS / Linux

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.lock
.venv/bin/python -m harbor_grc init --admin admin --generate-password
.venv/bin/python -m harbor_grc seed-demo
.venv/bin/python -m harbor_grc serve
```

These commands are provided for portability; the recorded local verification was
on Windows. See the CI results for checks performed on other environments.

Skip `seed-demo` if you want an empty workspace. It requires an empty records
database. If the account already exists, use `reset-user admin --role admin
--generate-password` instead of running `init` again. You can omit
`--generate-password` to choose your own 14–128 character passphrase.

The normal local database is `data/harbor.db`. `GRC_DATABASE` selects another
database; `GRC_ORIGIN` must match the exact browser origin if you change the port.
The [deployment guide](docs/deployment.md) covers account recovery, configuration,
HTTPS, backups, and restoration.

## Try a short walkthrough

1. Open the storage exposure finding and follow its links to the asset, risk,
   and control.
2. Read the control's test procedure. Decide what evidence would be sufficient
   for its scope.
3. Submit evidence as pending, then use a second account to review it. A local
   operator can create one with `create-user reviewer --role analyst`.
4. Try closing a finding without current approved evidence, then repeat with
   the required evidence and remediation notes.
5. Compare a critical supplier with a low-access supplier and explain the
   difference in due diligence.
6. Import [the synthetic cloud findings](sample-data/aws-securityhub.json) twice.
   The second import should recognize the same source observations.
7. Export a report and inspect its audit checkpoint.

Using two accounts yourself demonstrates the workflow. A real independent review
requires another person with the appropriate authority.

## NIST and ISO references

The library includes CSF 2.0, RMF, the SP 800-53 family, risk-assessment,
incident-response, supply-chain and CUI guidance, and ISO/IEC 27001, 27002 and
27005 references. Publication editions and primary sources are recorded in the
[framework guide](docs/frameworks.md).

The [crosswalk](docs/framework-crosswalk.md) explains why a local control relates
to a selected reference and what still needs assessment. These are project-authored
partial associations. Mapping a control does not satisfy the whole requirement
or make the application compliant.

Use the [CSF profile](templates/csf-organizational-profile.md),
[ISO Statement of Applicability](templates/iso-statement-of-applicability.md), and
[assessment plan](templates/framework-assessment-plan.md) to record scope,
evidence gaps, and decisions. ISO standards text is not bundled.

![Framework library](docs/images/frameworks.jpg)

## Read the reasoning

| If you want to understand… | Start here |
| --- | --- |
| The business and assessment boundary | [Northstar case study](docs/case-study.md) |
| The workflow from finding to decision | [Handbook](docs/handbook.md) |
| Why the application makes these tradeoffs | [Design decisions](docs/decisions.md) |
| Risk scales, treatment, and acceptance | [Risk methodology](docs/risk-methodology.md) |
| Cloud controls and supplier reviews | [Cloud assurance](docs/cloud-assurance.md), [vendor risk](docs/vendor-risk.md) |
| Evidence sampling and review | [Control testing](docs/control-testing.md) |
| Security boundaries and API behavior | [Architecture](docs/architecture.md), [API](docs/api.md) |
| Checks that have actually run | [Verification](docs/verification.md) |
| A demo and an honest portfolio description | [Portfolio guide](docs/portfolio.md) |
| The public references behind the work | [Sources](docs/sources.md) |

The [templates](templates/) also cover access reviews, risk decisions, exceptions,
incidents, and management reviews.

## Limits that matter

This is one organization on one application instance with SQLite. Every
authenticated user can read all registers. Administrators and analysts can edit
them; auditors have read-only access. Local operators manage accounts.

Evidence records hold references and hashes, not uploaded artifacts. The server
does not retrieve a file or verify that its contents match the supplied digest.
The local audit hash chain needs a trusted external checkpoint to detect a full
rewrite or truncation.

There is no built-in SSO/MFA, tenant isolation, high availability, or detailed
approval-authority matrix. An independent penetration test, load testing, and
target-environment recovery validation are still needed. The [deployment
checklist](docs/deployment.md) makes that adoption work explicit.

The [roadmap](ROADMAP.md) describes the next work and what would make each change ready to accept.

## Development

```sh
python -m pip install -r requirements-dev.lock
python -m pytest
python -m ruff check .
python -m build --no-isolation
```

The latest recorded local run passed **113 tests**. See
[verification notes](docs/verification.md) for the environment, scope, and known
warning. The GitHub workflow also defines Windows/Linux tests, packaging, and a
runtime dependency advisory check; check its actual result before relying on it.

Contributions should explain the workflow a change improves and test the relevant
failure cases. [CONTRIBUTING.md](CONTRIBUTING.md) has the setup and review guidance.

## Data and authorship

The scenario, suppliers, assessments, and evidence outcomes are fictional.
The code and documentation were developed with AI assistance. The goal is a
project whose decisions and limitations can be inspected and explained; no real
client engagement, certification, or independent assurance opinion is claimed.

MIT licensed. For security concerns, see [SECURITY.md](SECURITY.md).


