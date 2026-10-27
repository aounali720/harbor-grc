# Showing the project

A good Harbor demo follows one decision far enough that another person can check the reasoning. Start with the fictional company's export-storage finding, explain the possible customer harm, and show what the owner and reviewer would need before closing it. That tells a clearer story than opening every screen.

## A short walkthrough

| Step | Show | Point to explain |
| --- | --- | --- |
| 1 | [Northstar's service boundary](case-study.md) | Where customer data flows and which responsibilities belong to the service owner |
| 2 | **FND-01 Public storage exception lacks sign-off** and its linked risk/control | An observed issue, a potential loss, and a safeguard are different records |
| 3 | The evidence record and its review fields | The artifact stays in a controlled repository; Harbor records identity, dates, reference, digest, and review |
| 4 | A supplier's data/access/criticality inputs | Tier sets review priority; the reviewer still explains the use decision |
| 5 | A self-approval attempt or stale edit in a fresh demo database | A workflow boundary that the application actually enforces |
| 6 | The report and activity history | What can be traced, what remains uncertain, and the work still needed |

Keep the example small. Explain why the storage control can have evidence while the finding still needs action and residual risk still needs assessment. A scanner result or control status cannot make the business decision on its own.

For a review demonstration, two accounts operated by one presenter simulate the workflow; they do not provide independent assurance. Use the fictional data and synthetic test artifacts throughout.

## Explain one tradeoff well

The [design decisions](decisions.md) give six useful starting points. Evidence metadata is a good example: keeping files outside Harbor avoids building another confidential-document store, but it leaves access, retention, and availability to that repository. The next useful question is how to test that the reviewer can retrieve the right artifact.

For implementation details, use [architecture](architecture.md). For checks actually performed on the build, use [verification](verification.md). For workplace setup, use [deployment](deployment.md). These separate the delivered behavior from the requirements of a particular environment.

## Describe the work accurately

A project description you can adapt to your own contribution:

> I built Harbor GRC to explore how a technical finding turns into a documented risk decision. It links findings, controls, evidence, supplier reviews and ownership in a fictional SaaS environment. The repository includes runnable code, workflow tests and setup notes.

In an interview or repository description, name the parts you reviewed, changed, tested, or deployed. This project demonstrates a working process and implementation; it is not experience running a real company's audit or a certificate for the sample company.

## Where the material comes from

AI assistance was used in developing this project. Northstar Metrics and its people, suppliers, assessments and decisions are fictional. Example domains use `.example`; artifact references and hashes are demonstration markers, not collected evidence. Framework mappings are selected project-authored links, with primary sources in the [source register](sources.md).

The public repository is intended to contain that fictional material. Keep workplace databases, reports, logs, screenshots, credentials, signed links, and actual evidence out of it. When adapting this project, review every file and the commit history before publishing anything from a real workplace.

## Put it to use

For a personal project, replace the scenario with your own service boundary, identify a few material risks, and complete one evidence-and-review cycle. For a team, first validate access, recovery, retention, and support arrangements against the [deployment guide](deployment.md). Harbor starts with one organization and a small-team deployment; broader isolation or availability needs require additional engineering.
