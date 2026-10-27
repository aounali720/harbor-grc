# Working with Harbor GRC

Harbor follows a piece of GRC work from the first observation to the decision that closes it. The useful part is the connection: a cloud finding belongs to an asset, the asset supports a service, the service has a business risk, and someone needs enough evidence to decide what to do next.

The demo uses Northstar Metrics, a fictional SaaS company. Its data gives you a starting point for SaaS governance, cloud assurance, and supplier reviews without needing an employer's records.

## Start with one finding

Open **FND-01 Public storage exception lacks sign-off**, then follow its linked asset, risk, and control. The records answer different parts of the same problem:

| Record | What to establish |
| --- | --- |
| Asset | Which export service or storage location is affected, what it holds, and who owns it |
| Finding | What was observed, the affected scope, the owner, and the required action |
| Risk | How an exposure could harm customers or the business |
| Control | What should prevent or detect that exposure and how it is tested |
| Evidence | Which retained artifact supports the result, who reviewed it, and whether it is still current |

Before changing a status, write a closure condition the reviewer can test. For this example, that could mean reconciling the export-storage population, checking the approved access paths, resolving the exception, and retaining the results. Use synthetic objects for any demonstration test.

The seed includes an effective storage control while the related finding remains open and residual risk is unrated. Those fields need separate review. Evidence for a control does not automatically resolve every exception, and linking a control does not calculate remaining risk.

## Finish the loop

1. Give the finding an owner, due date, and specific remediation notes.
2. Keep the actual artifact in a controlled evidence repository. Enter its stable HTTPS reference, SHA-256, collection date, expiry, and control in Harbor.
3. Have a different reviewer assess the evidence and record the conclusion. The application prevents the creator or current submitter from approving it.
4. Link relevant, current approved evidence when closing the finding. Freshness depends on both expiry and the control's test cadence.
5. Reassess residual likelihood and impact with a reason and review date. If the remaining exposure is accepted, record a separate authorized decision with an expiry.

The workflow enforces these record checks. People still establish evidence quality, reviewer competence, and actual business authority. The [control-testing guide](control-testing.md) explains that work in more detail.

## Use the same approach for suppliers

For a supplier, begin with the proposed service, data, access, and business dependency. Those inputs determine review tier. A questionnaire score can summarize the review, but the decision needs a reason: the arrangement may be acceptable, conditional on an action, or unsuitable. Track an unresolved supplier issue as a finding and connect the business consequence to a risk.

The [vendor guide](vendor-risk.md) walks through that lifecycle. The [tabletop](incident-tabletop.md) brings supplier access, cloud evidence, and incident decisions into one exercise.

## Find the right guide

| Work at hand | Read |
| --- | --- |
| Set the boundary and understand the fictional service | [Case study](case-study.md) |
| Rate a scenario or record acceptance | [Risk method](risk-methodology.md) |
| Assign decision owners and review cadence | [Governance](governance.md) |
| Plan cloud checks and evidence collection | [Cloud assurance](cloud-assurance.md) |
| Select NIST/ISO references and review partial mappings | [Framework guide](frameworks.md) and [crosswalk](framework-crosswalk.md) |
| Plan a rollout | [90-day plan](implementation-plan.md) |
| Understand implementation choices | [Design decisions](decisions.md) and [architecture](architecture.md) |
| Run, validate, or demonstrate the project | [Deployment](deployment.md), [verification](verification.md), and [portfolio walkthrough](portfolio.md) |

The [templates](../templates/) hold the longer reasoning: scope, test plans, assessments, and approvals. The [source register](sources.md) records the public references. Framework links help you find relevant criteria; evidence coverage remains a count of this project's controls with current support, not a certification result.
