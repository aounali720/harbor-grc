# Public source register

References checked on **2026-10-26**. These are primary sources used for framework context, cloud check scope, and terminology. Project-authored procedures, scoring bands, review intervals, RACI, sample sizes, and sample organizational facts are design choices unless explicitly stated otherwise. Public documentation can change; verify relevant details when updating the project.

| Reference | Use in this project | Boundary |
| --- | --- | --- |
| [NIST Cybersecurity Framework 2.0](https://www.nist.gov/cyberframework) | Organizing vocabulary for governance and cybersecurity outcomes | Selected project mappings do not establish complete coverage or conformance |
| [NIST CSF 2.0 Organizational Profiles](https://www.nist.gov/cyberframework/profiles) | Scope and current/target posture discussion | The project does not supply an authoritative NIST profile or approved crosswalk |
| [NIST SP 800-30 Rev. 1](https://csrc.nist.gov/pubs/sp/800/30/r1/final) | Background for risk assessment planning and review | The project's 1–5 scales and multiplication bands are its own simplified method |
| [NIST SP 800-161 Rev. 1, November 2024 update](https://csrc.nist.gov/pubs/sp/800/161/r1/upd1/final) | Supplier lifecycle and risk-management context | Tier rules and the five-domain questionnaire are project-defined |
| [AWS shared responsibility model](https://aws.amazon.com/compliance/shared-responsibility-model/) | Distinguishing provider and customer responsibilities | Responsibility still depends on actual services and configurations |
| [AWS Security Hub CSPM S3 controls](https://docs.aws.amazon.com/securityhub/latest/userguide/s3-controls.html) | Scope of account/bucket access checks | One passing check does not establish complete data access assurance |
| [AWS Security Hub CSPM IAM controls](https://docs.aws.amazon.com/securityhub/latest/userguide/iam-controls.html) | Identity/policy check context | Specific checks do not assess every permission path |
| [AWS Security Hub CSPM CloudTrail controls](https://docs.aws.amazon.com/securityhub/latest/userguide/cloudtrail-controls.html) | Logging configuration test context | Delivery, usability, and organization-wide coverage need additional review |
| [AWS Security Hub CSPM RDS controls](https://docs.aws.amazon.com/securityhub/latest/userguide/rds-controls.html) | Database configuration and recovery planning | Configuration checks are distinct from measured service restoration |
| [AWS Security Finding Format](https://docs.aws.amazon.com/securityhub/latest/userguide/securityhub-findings-format.html) | Finding import terminology and format context | Harbor implements a bounded subset, not the entire specification |

The linked NIST SP 800-161 publication is the revision including updates dated November 1, 2024. No claim is made that a later draft replaces a final publication without review. AWS control identifiers and availability should be checked against the account/region and enabled standards in actual use.

No ISO, AICPA/SOC 2, CIS, or other proprietary standard text is reproduced. Any future assessment against such criteria must use the authorized criteria and a qualified engagement process. This source list is not legal advice or a compliance applicability determination.

## Framework-library additions checked 2026-10-27

The original 2026-10-26 source register above is preserved. The following checks support the added framework catalogue, project crosswalk, and assessment templates. These metadata references do not establish applicability to an organization. New drafts and publication releases need review before an approved baseline or contract is changed.

| Primary reference | Metadata / specific use checked | Limit of use |
| --- | --- | --- |
| [NIST CSF 2.0 publication](https://www.nist.gov/publications/nist-cybersecurity-framework-csf-20) | Publication date 2024-02-26; outcome framework context | Project profile examples are original and incomplete |
| [SP 800-37 Rev. 2](https://csrc.nist.gov/pubs/sp/800/37/r2/final) | Published 2018-12; RMF lifecycle role | Harbor does not supply an authorization decision |
| [SP 800-53 Rev. 5](https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final) | Base publication 2020-09 with 2020-12-10 updates; Release 5.2.0 noted 2025-08-27 | Selected identifiers are partial reference links |
| [SP 800-53A Rev. 5](https://csrc.nist.gov/pubs/sp/800/53/a/r5/final) | Base 2022-01; assessment-procedure Release 5.2.0 noted 2025-08-27 | Assessment methods and rigor still need a scoped plan |
| [SP 800-53B](https://csrc.nist.gov/pubs/sp/800/53/b/upd1/final) | Base 2020-09 with 2020-12-10 updates; Release 5.2.0 made no baseline changes | An organization must select/tailor an applicable baseline |
| [NIST 5.2.0 release announcement](https://csrc.nist.gov/News/2025/nist-releases-revision-to-sp-800-53-controls) | Release date and relationship among the three publication artifacts | Does not change an agreement-specific edition automatically |
| [SP 800-30 Rev. 1](https://csrc.nist.gov/pubs/sp/800/30/r1/final) | Published 2012-09; risk-assessment role | Project scoring bands are not NIST requirements |
| [SP 800-161 Rev. 1 update 1](https://csrc.nist.gov/pubs/sp/800/161/r1/upd1/final) | Published 2022-05; updates through 2024-11-01 | Project tiers/questionnaire remain project choices |
| [SP 800-61 Rev. 3](https://csrc.nist.gov/pubs/sp/800/61/r3/final) | Final 2025-04-03; supersedes Rev. 2; incident-response CSF 2.0 Community Profile | Reference-only addition; no new starter mapping or complete profile assessment |
| [SP 800-171 Rev. 3](https://csrc.nist.gov/pubs/sp/800/171/r3/final) | Published 2024-05; CUI confidentiality scope in nonfederal systems | No CUI/contractual mandate is inferred for the fictional SaaS scenario |
| [SP 1302 Tier guide](https://csrc.nist.gov/pubs/sp/1302/final) | Final 2024-10; context for Tier judgment | Tier is not calculated from Harbor's evidence coverage |
| [CSF Profile resources](https://www.nist.gov/cyberframework/profiles) | Current/target profile resources | The new Markdown template is project-authored |
| [CSF reference tool](https://csrc.nist.gov/projects/cybersecurity-framework/filters) | Official Core/outcome discovery | Selected starter links omit most of the Core |
| [CSF Informative References](https://www.nist.gov/cyberframework/informative-references) | Mapping discovery; contributor/edition/version and non-NIST submission caveats | Our 12-topic pack is separate project content; catalogue listing does not endorse third-party correctness |
| [ISO/IEC 27001:2022](https://www.iso.org/standard/27001) | Edition 3, 2022-10; ISMS requirements role | Use the authorized standard for full criteria, including Clauses 4–10 |
| [ISO/IEC 27001:2022/Amd 1:2024](https://www.iso.org/standard/88435.html) | Published 2024-02; climate-context amendment | Recorded in the catalogue; not assessed by the 12 starter mappings |
| [ISO/IEC 27002:2022](https://www.iso.org/standard/75652.html) | Edition 3, 2022-02, corrected version 2022-03; control guidance | Identifier/topic references do not reproduce licensed implementation guidance |
| [ISO/IEC 27005:2022](https://www.iso.org/standard/80585.html) | Edition 4, 2022-10; information-security risk guidance | Templates are original working aids, not a substitute for the standard |
| [ISO/IAF climate communication](https://www.iso.org/files/live/sites/isoorg/files/standards/popular_standards/management_systems/ISO-IAF%20Joint%20Communique%20Feb%202024.pdf) | Management-system intent of climate consideration | Does not establish a generic emissions control for every ISMS |
| [ISO committee SoA discussion note](https://committee.iso.org/files/live/sites/jtc1sc27/files/resources/ISO-IECJTC1-SC27-WG1_N3298_Auditing%20Practices%20Note%20-%20SoA.pdf) | Explanatory context for applicability and custom controls | Committee discussion material, not the normative standard or a certification opinion |

The framework docs use selected identifiers and original project prose. The SoA template intentionally omits the complete Annex A list and requires comparison using an authorized copy. No full ISO standards text, complete 93-control list, or proprietary assessment report is distributed.

## Follow-up verification on 2026-10-27

The official ISO publication records were rechecked: ISO/IEC 27002:2022 remains Edition 3 with the 2022-03 corrected version; ISO/IEC 27005:2022 remains Edition 4, published 2022-10. The official NIST record confirms SP 800-171 Rev. 3 was finalized on 2024-05-14; its inclusion still does not decide agreement-specific applicability. SP 800-61 Rev. 3 is now included as a reference-only publication for the existing incident exercise. The project starter crosswalk remains 12 topics and 79 partial links.
