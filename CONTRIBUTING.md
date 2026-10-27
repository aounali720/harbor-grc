# Contributing

Start with a small change you can explain and demonstrate. Harbor connects risk
judgment to controls, evidence, and accountable decisions, so a useful contribution
should make one of those steps clearer or more reliable.

Use Python 3.11 or later and a virtual environment. Install the development lock
with `python -m pip install -r requirements-dev.lock`, then run
`python -m pytest` and `python -m ruff check .` from the repository root. Use your
virtual environment's Python for these commands. Add a regression test when a
change fixes a meaningful workflow or security failure.

Describe the problem, the resulting behavior, and what you verified in your pull
request. Explain changes to authorization, review gates, evidence freshness, or
risk decisions. Keep the independent-review checks in place when building a demo.
If a change alters the stored database schema, include a versioned migration,
backup and recovery instructions, and a test against an existing database.

Framework mappings need a primary-source reference, the relevant edition, and an
explanation of the relationship and its limits. A related control is not proof
that a requirement has been satisfied. Do not copy licensed ISO standard text
into the project.

Use fictional examples. Keep actual databases, evidence, credentials, exports,
and employer-specific material outside the public repository. Before a pull
request, inspect the staged files and screenshots as well as the visible diff;
ignore rules cannot remove a secret that was already committed. Report security
issues through the private route described in [SECURITY.md](SECURITY.md).

AI assistance is welcome. Describe what you checked yourself, and keep the
project's fictional scenario and AI provenance clear. Do not describe generated
sample evidence as an assessment performed for a real organization.
