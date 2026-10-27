# Deployment, operations and recovery

The local walkthrough is runnable now. Workplace deployment is an acceptance
exercise owned by your organization. This release has not been independently
penetration-tested or accepted in a Linux container, and it has no availability
or throughput SLA.

## Choose a deployment boundary

Use one application instance on a maintained host with local encrypted storage.
Put it behind HTTPS and an organizational access gateway with MFA. Restrict the
application port to the proxy/loopback. SQLite files must not live on NFS/SMB or
be shared among replicas. If you need multiple organizations, tenant isolation,
several app replicas, or high availability, redesign storage and authorization
before adopting this release.

All authenticated people can read all records. Admin and analyst roles can both
change registers and approve other users' evidence. Review whether that fits
your separation-of-duties and approval-authority requirements. Host operators can
read the database, bypass workflows, and run account commands.

## Configuration

The application reads process environment variables. It does **not** automatically
load a .env file. Docker Compose can load .env for variable interpolation; do not
commit that file.

| Variable | Default | Meaning |
|---|---|---|
| GRC_ENV | local | local or production |
| GRC_DATABASE | data/harbor.db | Database filename |
| GRC_ORIGIN | http://127.0.0.1:8000 | Exact browser origin, without trailing slash or path |

Local mode permits loopback origins only. Production refuses an HTTP origin and
uses a Secure, HttpOnly, SameSite=Strict `__Host-harbor_session` cookie. Proxying
production HTTP internally is expected; only the external connection is HTTPS.
The proxy must preserve the external Host header.

Example PowerShell for a separate local assessment:

```powershell
$env:GRC_DATABASE = "data/my-assessment.db"
$env:GRC_ORIGIN = "http://127.0.0.1:8000"
.\.venv\Scripts\python.exe -m harbor_grc init
.\.venv\Scripts\python.exe -m harbor_grc serve
```

If you change the port, change the origin too. Sessions are database-backed,
expire after eight hours, and expire after thirty minutes without requests.
Idle timestamps refresh at most once per minute. Browser cookies alone cannot
extend the absolute expiry.

## Container deployment template

Docker is not installed in the project validation environment, so these files
are supplied as an unverified deployment template. Run and accept them in your
own staging environment before real records.

1. Set a DNS name and obtain a TLS endpoint. Keep the app private.
2. Set `GRC_ORIGIN=https://grc.example.com` in the shell/Compose environment,
   replacing the example with your actual hostname.
3. Build with `docker compose build`.
4. Initialize using `docker compose run --rm app python -m harbor_grc init --admin admin`.
   Choose a unique passphrase at the prompt.
5. Create reviewers with `docker compose run --rm app python -m harbor_grc create-user reviewer --role analyst`.
6. Start with `docker compose up -d`.
7. Configure a TLS reverse proxy. A minimal host Caddy example is in
   `deploy/Caddyfile`. It is not an access gateway or brute-force protection policy.
8. Check health, login, role restrictions, evidence approval, export, and restoration
   using synthetic data before adding organizational records.

The image runs as UID/GID 10001, writes only to the data volume, and the Compose
template drops capabilities, enables a read-only root filesystem and sets
resource limits. Validate volume ownership and host security updates. Pin the
base image to an approved digest in your own release process; the supplied
`python:3.11-slim` tag is mutable.

One worker and a concurrency limit of 32 are intentional. Scrypt uses approximately
128 MiB per calculation; login calculations hold a short SQLite write transaction
and serialize. Budget host memory, monitor latency, and configure upstream
connection/body/time limits. No load target has been validated.

## Proxy and login throttling

The server deliberately ignores forwarded IP headers. Account limits apply across
IP addresses; the direct-IP limit sees the proxy address when behind one. Thirty
failed logins through that proxy within fifteen minutes trigger a shared backstop,
which can deny legitimate users until the window ends. Configure real per-client
IP throttling at the access gateway and decide whether this tradeoff is acceptable.
Do not enable arbitrary forwarded-header trust to work around it.

There is no MFA or SSO integration in the app itself. A gateway is an additional
access boundary, not a replacement for application sessions. No public signup,
password-reset email, password manager, or external identity provider is configured.

## Account lifecycle

Use local operator commands from the virtual environment or a trusted container
exec session. Passwords are prompted; do not pass them in command arguments.

```sh
python -m harbor_grc create-user auditor --role auditor
python -m harbor_grc reset-user reviewer --role analyst
python -m harbor_grc disable-user departing-user
```

Reset rotates the password/role, revokes all sessions, and clears only that
username's login-failure window. Shared IP failure limits remain in force. Disabling also revokes
sessions. CLI guards prevent disabling or demoting the last active administrator.
Keep two authorized host operators and a documented break-glass process.
The host OS must attribute who invoked the generic `local-operator` audit identity.
No application UI account-management endpoint exists.

## Backups and restoration

Back up at the frequency justified by your organization's RPO. The example target
is daily backups with a tested recovery within one business day; it is not an
observed SLA. Store backups encrypted, restrict access, and test restoration.

```sh
python -m harbor_grc backup backups/harbor-2026-10-26.db
python -m harbor_grc export reports/assessment-2026-10-26.json
python -m harbor_grc verify-audit
```

Backup uses SQLite's online backup API, which captures WAL consistently. A raw copy
of only the .db file can miss active WAL changes. Backup includes password hashes
and session records. Exports exclude users and sessions but can still contain
sensitive organizational metadata. Do not publish either.

To restore:

1. Stop the application and identify the intended database path.
2. Preserve the existing database, WAL and SHM files as an incident/recovery copy.
3. Check the backup in an isolated location with `PRAGMA integrity_check`.
4. Restore the backup to a new filename and point GRC_DATABASE at it. Do not reuse
   stale WAL/SHM files from a different database.
5. Before exposing the application, revoke restored sessions through a trusted
   SQLite operator session using `DELETE FROM sessions;`; record a recovery event
   in your operator log.
6. Start the compatible application release, verify audit count/head against
   the last external checkpoint, and test expected records and permissions.
7. Record actual recovery duration, data loss, and approval to reopen service.

The automated backup test verifies record and chain restoration from a temporary
database. It does not exercise your infrastructure, backup encryption, or RTO.

## Audit and evidence operations

Keep periodic audit checkpoints (count, head hash, timestamp) outside the application
in a protected, independently controlled location. A chain verified against itself
cannot detect truncation or complete rewriting. Do not call it immutable storage.

Evidence files stay in your approved repository with its own permissions, retention,
encryption, legal hold and immutable-history controls. A SHA-256 field is an operator
declaration; Harbor cannot prove that a file at a reference matches the digest.
Avoid signed URL query strings, personal data and account secrets in evidence metadata.

## Acceptance before workplace use

- Document system owner, data classification, authorized readers, risk appetite,
  approval authorities, and records retention.
- Review privacy/legal obligations with your own specialists; no jurisdiction is assumed.
- Complete threat review and independent security testing appropriate to exposure.
- Validate HTTPS, host/origin checks, cookie flags, account lifecycle and upstream MFA.
- Confirm gateway limits and the direct-proxy lockout behavior.
- Test every reviewer/auditor workflow with separate people and negative cases.
- Verify encrypted storage, backup permissions, restoration and session revocation.
- Set alerts for health failures, DB capacity, latency, backup failures and audit discrepancies.
- Run the test suite and advisory scan on the target Python/OS; build and inspect the image.
- Approve or close documented limitations before adding real data.

The project makes these gaps visible so an adopter can make a defensible release
decision. A polished dashboard is not evidence of operational readiness.


### Alternative to hidden password input

Account commands `init`, `create-user`, and `reset-user` accept
`--generate-password`. The local operator explicitly requests generation and the
new random passphrase appears in that terminal only after the account transaction
commits. It is never accepted as a command argument, written to a credential file,
or placed in the audit event. Protect terminal output and store the credential in
your approved password manager. Existing browser sessions are revoked on reset.

```sh
python -m harbor_grc reset-user admin --role admin --generate-password
```

Do not reset a preview database when recovering an account in a live workspace.
Confirm GRC_DATABASE, GRC_ORIGIN and the target username before running recovery.
