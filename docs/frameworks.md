# Selecting and using the framework library

Harbor's framework library gives the SaaS, cloud, and supplier program a shared reference structure. Start with the business scope and required decisions, then select the references that help answer them. Adding every framework to a record creates labels, not assurance.

This selected starter library was verified against the primary sources below on **2026-10-27**. It is not a complete catalogue of NIST publications or an official crosswalk. Identifiers and project-authored topic descriptions are provided; ISO standards text is not included. Use an authorized copy for an actual assessment.

## Choose the right kind of reference

| Need | Starting point | Result to produce |
| --- | --- | --- |
| Explain cybersecurity priorities | NIST CSF 2.0 | Scoped current/target profile, gaps, decisions, action plan |
| Manage a system's risk through its life cycle | RMF / SP 800-37 Rev. 2 | Roles, boundary, selected controls, assessment/authorization decisions, monitoring |
| Select detailed security/privacy safeguards | SP 800-53 Rev. 5 | Tailored controls with parameters, owners, implementation, evidence |
| Plan assessment of selected safeguards | SP 800-53A Rev. 5 | Assessment objectives, methods, scope, sampling, results, limitations |
| Use an appropriate defined baseline | SP 800-53B | Baseline selection and tailoring rationale |
| Reason about risk scenarios | SP 800-30 Rev. 1 or ISO/IEC 27005:2022 | Assessment method, assumptions, decisions, review triggers |
| Examine supply-chain risk | SP 800-161 Rev. 1 update 1 | Supplier lifecycle plan integrated with business risk |
| Improve incident readiness and response in the CSF context | SP 800-61 Rev. 3 | Scoped incident-response profile, exercised decisions, verified follow-up |
| Address a confirmed CUI requirement in a nonfederal scope | SP 800-171 Rev. 3, when the governing agreement calls for it | CUI boundary, applicable edition/obligations, implementation and assessment plan |
| Establish an information security management system | ISO/IEC 27001:2022 + Amd 1:2024 | Operated ISMS, treatment, applicability decisions, evaluation, improvement |
| Develop selected information-security controls | ISO/IEC 27002:2022 | Organization-specific controls and implementation/test procedures |

CSF outcomes express desired posture; control references support implementation; assessments test it; business owners decide what residual risk is acceptable. ISO/IEC 27001 adds management-system requirements. Reuse an artifact only after checking its relevance and sufficiency for each criterion and scope.

## Edition register

| Library entry | Edition/release metadata checked | Role and boundary | Primary source |
| --- | --- | --- | --- |
| NIST CSF 2.0 | Published 2024-02-26 | Outcomes, Profiles, Tiers; no prescribed technical implementation | [CSF publication](https://www.nist.gov/publications/nist-cybersecurity-framework-csf-20) |
| NIST SP 800-37 Rev. 2 | Published 2018-12 | RMF lifecycle process; Harbor does not confer government authorization | [Publication](https://csrc.nist.gov/pubs/sp/800/37/r2/final) |
| NIST SP 800-53 Rev. 5 | Base 2020-09; updates 2020-12-10; catalogue Release 5.2.0 dated 2025-08-27 | Select and tailor the security/privacy control catalogue | [Publication/release note](https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final) |
| NIST SP 800-53A Rev. 5 | Base 2022-01; assessment-procedure Release 5.2.0 dated 2025-08-27 | Assessment procedures still need scoped methods and rigor | [Publication](https://csrc.nist.gov/pubs/sp/800/53/a/r5/final) |
| NIST SP 800-53B | Base 2020-09; updates 2020-12-10; Release 5.2.0 dated 2025-08-27 | Baselines/tailoring; 5.2.0 made no baseline changes | [Publication](https://csrc.nist.gov/pubs/sp/800/53/b/upd1/final) |
| NIST SP 800-30 Rev. 1 | Published 2012-09 | Risk-assessment guidance; Harbor's ordinal matrix is project-defined | [Publication](https://csrc.nist.gov/pubs/sp/800/30/r1/final) |
| NIST SP 800-161 Rev. 1, update 1 | Published 2022-05; updated through 2024-11-01 | Cybersecurity supply-chain risk guidance | [Updated publication](https://csrc.nist.gov/pubs/sp/800/161/r1/upd1/final) |
| NIST SP 800-61 Rev. 3 | Final 2025-04-03; supersedes Rev. 2 | Incident-response guidance expressed as a CSF 2.0 Community Profile; reference guidance, not a new mapped control set | [Publication](https://csrc.nist.gov/pubs/sp/800/61/r3/final) |
| NIST SP 800-171 Rev. 3 | Published 2024-05 | CUI confidentiality in nonfederal systems; verify applicable agreement/revision | [Publication](https://csrc.nist.gov/pubs/sp/800/171/r3/final) |
| ISO/IEC 27001:2022 + Amd 1:2024 | Edition 3, 2022-10; amendment 2024-02 | ISMS requirements and climate-context amendment | [Standard](https://www.iso.org/standard/27001), [amendment](https://www.iso.org/standard/88435.html) |
| ISO/IEC 27002:2022 | Edition 3, 2022-02; corrected version 2022-03 | Control guidance, distinct from the requirements standard | [Standard](https://www.iso.org/standard/75652.html) |
| ISO/IEC 27005:2022 | Edition 4, 2022-10 | Information-security risk guidance supporting ISMS work | [Standard](https://www.iso.org/standard/80585.html) |

Keep publication revision, data release, and project mapping version separate. A new release does not silently change a contract or approved assessment baseline. The [2025 NIST release announcement](https://csrc.nist.gov/News/2025/nist-releases-revision-to-sp-800-53-controls) confirms corresponding 800-53/800-53A changes and unchanged 800-53B baselines. Record source artifacts and review changes before adoption.

SP 800-171 Rev. 3 is available for a possible future CUI scope. The fictional SaaS scenario establishes neither CUI handling nor a federal contract, CMMC scope, or revision mandate. Determine governing agreements, data flows, responsibility, and effective requirements with the appropriate authority. A newer publication alone does not settle applicability.

## Apply CSF as an outcome profile

The six Functions are **Govern, Identify, Protect, Detect, Respond, and Recover**. Consider all six when scoping, then select relevant outcomes. Describe the present condition with evidence and uncertainty; define a verifiable target; prioritize gaps. Use the [organizational profile template](../templates/csf-organizational-profile.md).

For example, a supplier oversight target may require each privileged production integration to have an approved use decision, tested revocation, and a dated review. The current posture might have an incomplete inventory and evidence for only two services. Reconciling the population is an action; writing the policy does not mean the target was achieved.

Tiers characterize governance and risk-management rigor: **Partial (1), Risk Informed (2), Repeatable (3), Adaptive (4)**. Leadership selects a current/target Tier with evidence and reasons for the relevant scope. Do not derive it from average control percentages or risk scores. See [NIST's Tier guide](https://csrc.nist.gov/pubs/sp/1302/final). Harbor's evidence coverage is a project metric, not a Tier or certification score.

### Keep current, target, and action distinct

Freeze the current Profile at an as-of date. Link each selected outcome to observed conditions, evidence, and limitations; an unknown population stays unknown. Write the target as a condition the service owner could verify. Then create dated work to close the gap and define the evidence needed to update the current posture.

For a cloud-storage outcome, the current condition could be that two export buckets were inspected while the account inventory is unreconciled. The target is a reconciled export population with approved access configuration and verified authorized/unauthorized behavior. The action is to reconcile inventory and test every scoped access path. One passing bucket result does not achieve that target. This is a project example, not a new CSF requirement.

Keep the previous Profile, approved target, and action history. Update the current Profile only after evidence review; revise the target when business needs change with an explicit decision. The [template](../templates/csf-organizational-profile.md) provides the working fields. Harbor's control statuses and evidence counts support that review but do not construct or approve an entire Profile automatically.

## Use SP 800-61 Rev. 3 for incident-response planning

[NIST SP 800-61 Rev. 3](https://csrc.nist.gov/pubs/sp/800/61/r3/final), finalized on 2025-04-03, supersedes Rev. 2 and is a CSF 2.0 Community Profile. It relates incident response to broader cybersecurity risk management. Use the current publication when updating the program rather than presenting the older revision as current.

For Northstar, apply it through a scoped exercise and improvement cycle:

1. Identify the affected service, supplier access, data, detection sources, decision authority, and dependencies before designing the exercise.
2. State current readiness using actual contacts, access, logging coverage, recovery tests, and known gaps. Set a target that the business can resource.
3. Run the [supplier-token tabletop](incident-tabletop.md). Label discussed, simulated, demonstrated, and verified actions separately.
4. Capture decisions and uncertainty with the [incident action log](../templates/incident-action-log.md). Assign findings for incomplete scope, missing logs, unusable supplier contacts, or untested revocation.
5. Retest corrective work, review residual risk, and update the scoped Profile. Do not close a business incident solely because a provider alert is marked resolved.

The publication is a reference-only catalogue entry in Harbor. The 12-topic/79-link starter pack remains unchanged. No full community profile, automated incident assessment, notification deadline, or incident-handling certification is supplied.

## Apply ISO/IEC 27001 as an ISMS

Clauses 4–10 extend across organizational context/scope, leadership, planning, support, operation, evaluation, and improvement. Assess the management processes as well as selected safeguards. A table of Annex A links cannot establish an operated ISMS. The [ISO overview](https://www.iso.org/standard/27001) describes its management-system role; assess detailed criteria using the authorized standard.

Use the [Statement of Applicability template](../templates/iso-statement-of-applicability.md) to record necessary controls, inclusion reasons, implementation state, and justified Annex A exclusions. Compare the risk-selected set with Annex A to identify omissions; include custom controls when needed, such as tenant-isolation tests. The [ISO committee's SoA discussion](https://committee.iso.org/files/live/sites/jtc1sc27/files/resources/ISO-IECJTC1-SC27-WG1_N3298_Auditing%20Practices%20Note%20-%20SoA.pdf) is explanatory material rather than the normative standard.

The 2024 amendment adds climate relevance to context/interested-party consideration. Record whether and how climate issues affect the ISMS and relevant requirements. In this scenario examine hosting resilience, working arrangements, and customer requirements before reaching a reasoned conclusion. Do not assume every organization must add generic emissions controls to its security library. See the [joint ISO/IAF communication](https://www.iso.org/files/live/sites/isoorg/files/standards/popular_standards/management_systems/ISO-IAF%20Joint%20Communique%20Feb%202024.pdf) and [published amendment](https://www.iso.org/standard/88435.html).

### Translate ISMS work into owned evidence

The following are original Northstar work-product suggestions arranged by clause area. They are not a reproduction or exhaustive interpretation of ISO requirements. Consult the authorized criteria for the assessment, and record the activities and gaps independently of Annex A control coverage.

| Clause area | Suggested project work product | Accountable owner | Example gap to record instead of claiming completion |
| --- | --- | --- | --- |
| 4 | Approved service boundary, data-flow diagram, stakeholder/obligation log, climate-relevance decision | ISMS sponsor | Supplier interfaces or relevant requirements have not been reconciled |
| 5 | Approved policy, delegated authority, resourcing decisions, role matrix | Executive sponsor | Technical admin permissions are being used as a substitute for business authority |
| 6 | Approved risk method, assessment/treatment decisions, SoA, dated objectives and change plan | GRC lead with risk owners | Necessary controls lack inclusion rationale or planned work is reported as implemented |
| 7 | Competence evidence, communications plan, document ownership/version/access records | Process owners | A policy exists but operators lack training or cannot locate the controlled version |
| 8 | Completed operating records, reviewed assessment updates, treatment execution and tests | Service/control owners | The procedure is documented but operating-period evidence is missing |
| 9 | Defined measures, internal assessment results, management decisions and follow-through | Independent reviewer and sponsor | A green dashboard is presented without scoped evaluation or management action |
| 10 | Corrective-action records, cause analysis where supported, retest and program changes | Responsible service owner | Finding closed after editing a document without verifying the failure is addressed |

Use the evidence-gap section in the [SoA template](../templates/iso-statement-of-applicability.md) and the [assessment plan](../templates/framework-assessment-plan.md) to assign work. These are coordination aids; completing the tables does not itself establish ISMS conformance.

## Adoption workflow

1. **Approve the boundary:** services, data, accounts/regions, suppliers, interfaces, exclusions, obligations, and owners.
2. **Record objectives and criteria:** why each reference matters, exact edition/release, decision authority, and assessment period. Use the [assessment plan](../templates/framework-assessment-plan.md).
3. **Select and tailor controls:** start with scenarios/requirements, set parameters, define actions, compare relevant reference sets, and justify exclusions. An identifier needs an implementation description.
4. **Review mappings:** challenge the [starter crosswalk](framework-crosswalk.md), explain partial links, and identify gaps. A relationship is not equivalence.
5. **Operate and assess:** define populations, coverage, methods, sampling, cadence, and independent review. Preserve failures and unknowns. A passing setting does not prove an operated management system.
6. **Decide and improve:** record findings, treatments, reviewed residual risk, authorized time-limited acceptance, and management decisions. Update the Profile and SoA when scope changes; preserve history.
7. **Maintain versions:** review source updates, record approvals, reconcile mappings, and retest affected work before reporting against a new edition.

For Northstar, begin with a scoped CSF Profile and the existing risk/evidence workflow. Use selected 800-53 and ISO topics to make priority controls precise. If an ISO objective is adopted, establish the ISMS processes separately. Use RMF or federal baselines when the actual scope and authority call for them.

## Mapping provenance and limitations

Harbor's 12-control crosswalk is project-authored and partial. For broader mapping research, use [NIST's Informative References page](https://www.nist.gov/cyberframework/informative-references), which offers reference tools and catalogue discovery. Check the contributor, direction, exact editions, relationship, and limitations of a mapping before using it. NIST's listing of a non-NIST submission is not an endorsement or correctness test.

A library link does not establish full coverage, conformance, certification, legal applicability, or effectiveness over a period. These references and templates support organization-specific assessment and authorized decisions; they do not replace them.
