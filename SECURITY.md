# Security

Harbor GRC is a portfolio project and a foundation for controlled pilots. It has
not had an independent penetration test. Read the [deployment guide](docs/deployment.md)
before adding sensitive organizational records.

## Reporting a problem

Use [GitHub's private vulnerability reporting page](https://github.com/aounali720/harbor-grc/security/advisories/new)
when it is available. If that page is unavailable, open an issue asking the
[repository owner](https://github.com/aounali720) for a private reporting channel,
without including exploit details, credentials, or sensitive records.

Public bug reports should contain only synthetic examples. Never post a database,
password, session cookie, real evidence export, or signed evidence URL.

## Application boundary

The application serves one organization. Every authenticated account can read
all registers. Administrator and analyst accounts can create and update records;
auditors can read and export. Trusted local operators manage accounts. Host and
database access are administrative privileges.

Passwords use scrypt (N=131072, r=8, p=1). Random session identifiers are stored as
SHA-256 digests and sent in HttpOnly, SameSite=Strict cookies. Production mode
requires HTTPS and Secure cookies. Origin and CSRF checks protect state changes.
Credential creation/reset clears only the selected username's failure window;
shared IP throttles remain in force.

Evidence is metadata only: Harbor does not fetch artifacts or verify their bytes.
The audit chain is unkeyed. Store trusted checkpoints independently; a database
administrator can rewrite or truncate local history. Audit events retain changed
field names rather than a full sensitive record history.

See the [threat model](docs/architecture.md) for the controls and remaining gaps.

