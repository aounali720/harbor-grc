# Starter control crosswalk

This is Harbor's **project-authored partial mapping**, not an official NIST/ISO crosswalk, equivalence determination, or assessment result. It connects the 12 fictional starter control topics with selected references. Most criteria are absent. An unmapped requirement has not been assessed; a mapped requirement has not automatically been satisfied.

The table below is derived from the canonical [mapping pack](../harbor_grc/data/control_mappings.json). Its source metadata and individual rationales remain in that file. The [publication catalogue](../harbor_grc/data/frameworks.json) records editions and source links. Topic keys identify starter content; they are not a requirement that every organization's controls use these IDs or titles.

**Mapping version:** `2026.10.27-2`. **References checked:** 2026-10-27. **Topic count:** 12. **Selected links:** 79. **Relationship:** partial for every link.

The selected CSF identifiers now touch all six Functions, including RS.MA-01 for the supplier-incident topic. This is breadth across selected topics, not coverage of every outcome. The extra incident link remains partial: an exercise may support a joint response after declaration, while thresholds, the full population, actual execution, and communications still need validation. SP 800-61 Rev. 3 is a reference-only publication; adding it did not create a complete incident-response mapping.

## Selected links

The headers fix the editions. Reference identifiers below retain the pack's exact strings. 800-53 catalogue references use Rev. 5 with the catalogued Release 5.2.0. The ISO amendment is recorded in the publication catalogue; these starter mappings do not assess it.

| Topic key / fictional control | CSF 2.0 | SP 800-53 Rev. 5 | ISO/IEC 27001:2022 | ISO/IEC 27002:2022 |
| --- | --- | --- | --- | --- |
| CTL-01: Quarterly privileged access review | NIST CSF 2.0 PR.AA-05 | NIST SP 800-53 Rev. 5 AC-2<br>NIST SP 800-53 Rev. 5 AC-6 | ISO/IEC 27001:2022 A.5.18<br>ISO/IEC 27001:2022 A.8.2 | ISO/IEC 27002:2022 5.18<br>ISO/IEC 27002:2022 8.2 |
| CTL-02: Production storage exposure | NIST CSF 2.0 PR.DS-01 | NIST SP 800-53 Rev. 5 AC-3<br>NIST SP 800-53 Rev. 5 SC-28 | ISO/IEC 27001:2022 A.8.3<br>ISO/IEC 27001:2022 A.8.24 | ISO/IEC 27002:2022 8.3<br>ISO/IEC 27002:2022 8.24 |
| CTL-03: Centralized cloud audit logging | NIST CSF 2.0 DE.CM-09 | NIST SP 800-53 Rev. 5 AU-2<br>NIST SP 800-53 Rev. 5 AU-6<br>NIST SP 800-53 Rev. 5 AU-12 | ISO/IEC 27001:2022 A.8.15<br>ISO/IEC 27001:2022 A.8.16 | ISO/IEC 27002:2022 8.15<br>ISO/IEC 27002:2022 8.16 |
| CTL-04: Restore testing | NIST CSF 2.0 RC.RP-03 | NIST SP 800-53 Rev. 5 CP-9<br>NIST SP 800-53 Rev. 5 CP-10 | ISO/IEC 27001:2022 A.8.13 | ISO/IEC 27002:2022 8.13 |
| CTL-05: Critical vendor due diligence | NIST CSF 2.0 GV.SC-06 | NIST SP 800-53 Rev. 5 SR-3<br>NIST SP 800-53 Rev. 5 SR-6<br>NIST SP 800-53 Rev. 5 SA-9 | ISO/IEC 27001:2022 A.5.19<br>ISO/IEC 27001:2022 A.5.20<br>ISO/IEC 27001:2022 A.5.23 | ISO/IEC 27002:2022 5.19<br>ISO/IEC 27002:2022 5.20<br>ISO/IEC 27002:2022 5.23 |
| CTL-06: Supplier incident coordination | NIST CSF 2.0 GV.SC-08<br>NIST CSF 2.0 RS.MA-01 | NIST SP 800-53 Rev. 5 IR-4<br>NIST SP 800-53 Rev. 5 IR-8<br>NIST SP 800-53 Rev. 5 SR-8 | ISO/IEC 27001:2022 A.5.24<br>ISO/IEC 27001:2022 A.5.26 | ISO/IEC 27002:2022 5.24<br>ISO/IEC 27002:2022 5.26 |
| CTL-07: Risk decisions and exceptions | NIST CSF 2.0 GV.RM-02 | NIST SP 800-53 Rev. 5 RA-3<br>NIST SP 800-53 Rev. 5 PM-9 | ISO/IEC 27001:2022 clause 6.1.2<br>ISO/IEC 27001:2022 clause 6.1.3 | No selected link |
| CTL-08: Vulnerability remediation | NIST CSF 2.0 ID.RA-01 | NIST SP 800-53 Rev. 5 RA-5<br>NIST SP 800-53 Rev. 5 SI-2 | ISO/IEC 27001:2022 A.8.8 | ISO/IEC 27002:2022 8.8 |
| CTL-09: Managed workforce authentication | NIST CSF 2.0 PR.AA-03 | NIST SP 800-53 Rev. 5 IA-2<br>NIST SP 800-53 Rev. 5 IA-5 | ISO/IEC 27001:2022 A.8.5 | ISO/IEC 27002:2022 8.5 |
| CTL-10: Data retention and deletion | NIST CSF 2.0 PR.DS-01 | NIST SP 800-53 Rev. 5 SI-12<br>NIST SP 800-53 Rev. 5 MP-6 | ISO/IEC 27001:2022 A.5.33<br>ISO/IEC 27001:2022 A.8.10 | ISO/IEC 27002:2022 5.33<br>ISO/IEC 27002:2022 8.10 |
| CTL-11: Production change authorization | NIST CSF 2.0 PR.PS-01 | NIST SP 800-53 Rev. 5 CM-3<br>NIST SP 800-53 Rev. 5 CM-5 | ISO/IEC 27001:2022 A.8.32 | ISO/IEC 27002:2022 8.32 |
| CTL-12: Security program oversight | NIST CSF 2.0 GV.OV-01 | NIST SP 800-53 Rev. 5 PM-1<br>NIST SP 800-53 Rev. 5 PM-9<br>NIST SP 800-53 Rev. 5 CA-7 | ISO/IEC 27001:2022 clause 9.1<br>ISO/IEC 27001:2022 clause 9.3 | No selected link |

## Read the rationale and the gap together

These short gap statements come from the same pack, using the CSF relationship for each topic. Read all link-specific rationales in the JSON before reusing a mapping; the wider references may have additional caveats.

| Topic | Why the starter evidence is only partial |
| --- | --- |
| CTL-01 | Review the entitlement sample as one input to access-governance outcomes; provisioning, separation of duties and enforcement need broader testing. |
| CTL-02 | An unauthorized-read test examines one stored-data exposure path; other confidentiality, integrity and availability protections remain in scope. |
| CTL-03 | The sample tests visibility from selected cloud activity; detection coverage, alert use and all computing environments need separate assessment. |
| CTL-04 | A representative restore provides evidence about recovery data and integrity; all scoped dependencies and recovery decisions still need validation. |
| CTL-05 | A preapproval supplier review informs third-party risk decisions; ongoing service oversight and supply-chain dependencies remain separate work. |
| CTL-06 | A supplier tabletop examines coordinated response assumptions; production communications, recovery capability and lessons must be validated separately. |
| CTL-07 | Bounded exceptions record one part of risk appetite and tolerance decisions; strategy, criteria and governance authority need separate approval. |
| CTL-08 | Inventory reconciliation and retesting address selected vulnerability identification; the full asset population and other assessment methods need review. |
| CTL-09 | Authentication-path samples test selected identity safeguards; device, service and recovery-path coverage need separate confirmation. |
| CTL-10 | A deletion trace relates to stored-data lifecycle protection; retention authority, integrity, availability and remaining copies need assessment. |
| CTL-11 | Release sampling examines part of configuration management; the full lifecycle, baseline integrity and emergency paths require separate review. |
| CTL-12 | Committee review examines selected oversight decisions; organizational objectives, risk strategy and resulting policy changes need broader evidence. |

Some links are deliberately broad context. For storage exposure, a failed or passing anonymous-read test does not test cryptographic choices or key lifecycle, even though the topic relates to stored-data protection. For data deletion, a logical deletion trace does not establish physical media sanitization. For logging, delivery of an event does not prove detection/analysis. Treat those as assessment prompts and obtain separate relevant evidence before making the broader claim.

The selected ISO clause links for risk decisions and management review address portions of the ISMS. They do not assess every requirement in those clauses, the other Clauses 4–10, or the entire Statement of Applicability. Annex A identifiers and the corresponding 27002 guidance identifiers refer to related material with different roles; they are not two independent certifications.

## Review a proposed link before using it

1. Fix the service boundary, assessment period, exact criterion edition, and internal control implementation.
2. Read the actual criterion from the authoritative/authorized source. Check the full scope, relevant enhancements, parameters, and retained responsibilities.
3. Explain what the internal control actually contributes. Name what is untested rather than writing “equivalent.”
4. Define the source population, procedure, evidence, and independent reviewer for the intended claim.
5. Record a gap or additional control when the contribution is incomplete. Preserve the mapping decision and version.
6. Review the mapping when the criterion, service, implementation, or test changes.

Use this decision record when extending the pack:

| Internal control / implementation | Exact target reference and edition | Proposed contribution / direction | Untested scope and limits | Required additional evidence/control | Reviewer/date/version |
| --- | --- | --- | --- | --- | --- |
| [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |

These links do not map every catalogue entry. RMF, risk guidance, assessment procedures, baseline selection, CUI scope, and ISO risk guidance require their own adoption/assessment decisions rather than a forced link on each starter control. See [framework selection](frameworks.md) and the [assessment plan](../templates/framework-assessment-plan.md).

## Find broader reference mappings

Use [NIST's Informative References page](https://www.nist.gov/cyberframework/informative-references) to discover reference tools, downloads, and OLIR catalogue entries. It lists CSF links to 800-53 and ISO among other publications. Examine the contributor, mapping direction, exact editions, relationship model, version, and caveats for each entry. NIST states that non-NIST submissions are not correctness-tested and listing does not imply endorsement. Our starter pack is separate project content and is not presented as a NIST submission or approved mapping.

## Report coverage honestly

When reporting from these links, state the mapping version, selected reference population, in-scope internal controls, evidence freshness rule, and unknown-to-pack references. A valid reference outside this curated pack may remain visible as unknown until reviewed. Do not discard it or classify it as a failed framework requirement.

The coverage view counts distinct local controls per framework; several references to the same framework on one control count once. Evidence-backed counts require effective status and approved, unexpired evidence collected within the associated control test cadence. Catalogue entries used only as reference guidance can have zero mapped controls; zero is not a pass or failure. Unknown-to-pack references remain visible and are not treated as invalid. Evidence coverage answers whether the selected internal controls have current approved evidence under the application's rules. It does not measure every requirement in a framework, assess all relevant criteria, calculate a CSF Tier, or establish an ISO certificate. Multiple internal controls can share a reference and a single control can relate to several criteria; neither counts as multiple independent assurance conclusions.

