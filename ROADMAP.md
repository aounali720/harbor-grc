# Next steps

These are proposed improvements, not shipped features. The current release is
intended for a portfolio and controlled pilots.

| Work | What would make it ready to accept? |
| --- | --- |
| Identity integration | An approved provider or access gateway supplies MFA; session, revocation and recovery flows pass an independent review. |
| Approval authority | The application enforces the organization's allowed risk approvers and reviewer roles, including denial and delegation cases. |
| Evidence repository | Scoped access, file integrity, version retention and retrieval failures are tested with the chosen storage provider. |
| Independent audit checkpoints | Checkpoints are stored under separate administrative control; truncation and full-history rewrite detection are demonstrated. |
| Deployment acceptance | The container and HTTPS proxy pass staging tests; backup restoration, monitoring and failure response are exercised on the target host. |
| Capacity | Load tests establish a supported operating range for one SQLite instance and identify when another storage design is needed. |

Start each change with a workflow and a failure case. For example, evidence
integration should answer what a reviewer sees when an artifact is replaced,
deleted or no longer accessible. A new integration is useful when the team can
explain what it proves and what it leaves unresolved.

