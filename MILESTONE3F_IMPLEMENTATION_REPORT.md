# Milestone 3F — Controlled Authoritative-Source Ingestion Report

## Outcome

Milestone 3F did **not** proceed to real-source ingestion because the required permission to download, extract, internally index, and reproduce source content could not be established from the available official source information. The implementation correctly stops at the permission boundary rather than assuming that public accessibility authorizes automated ingestion.

No real document was downloaded into the repository, no real clinical or medication text was indexed, no source was registered as approved for internal indexing, and no patient information or live Cloudflare request was used.

## Candidate source assessed

The candidate selected from the Milestone 3C source-selection report was the **NAFDAC Greenbook — Nigeria’s Registered Product Database**:

- **Source name:** NAFDAC Greenbook.
- **Publisher/authority:** National Agency for Food and Drug Administration and Control (NAFDAC), Nigeria.
- **Exact source URL:** https://greenbook.nafdac.gov.ng/
- **Jurisdiction:** Nigeria.
- **Authority classification:** Nigerian primary regulatory source for public registered-product status information. NAFDAC’s official Drugs page identifies the Greenbook as its drug database and describes NAFDAC Public Assessment Reports as regulatory information about medicinal products granted marketing authorization in Nigeria.[1]
- **Intended use:** A narrowly scoped registration-status and product-identity reference, not a clinical counselling source and not proof of clinical suitability, authenticity, supply legality, storage conditions, or patient-specific appropriateness.
- **Access date:** 2026-11-05.

The Greenbook page exposes fields including product name, active ingredients, product category, NAFDAC registration number, applicant name, approval date, and status.[2] This is sufficient to identify a possible one-record demonstration, but it does not by itself establish permission to copy the data into an internal AI retrieval index.

## Exact content considered

No document or product record was ingested. The proposed first target was one Greenbook registration page or one exact product-information page, but an item was deliberately not selected for extraction because the permission requirements remained unresolved.

A linked Greenbook product-information PDF was inspected only as a rights-risk signal through its public search result. The result identifies a product document for Chlomacol (Chloramphenicol Capsules 250 mg) and includes a notice that material was selected from data included with permission and copyrighted by First Databank, Inc. That third-party notice makes the document unsuitable for ingestion without confirming the applicable licence and downstream indexing/reproduction rights.[3]

The project therefore did not preserve, paraphrase, hash, or store the contents of that document.

## Governance and permission findings

Public readability was confirmed for the NAFDAC Drugs page and Greenbook landing page.[1] [2] Public readability establishes permission to view the page, but not permission to:

- systematically download records or documents;
- extract and transform text or data;
- store source content in an internal retrieval index;
- use the content as evidence for AI-generated answers; or
- reproduce source wording or derived content in user-facing responses.

The Greenbook privacy page refers to separate Terms and Conditions but does not itself provide a clear licence granting automated extraction, internal indexing, or reproduction rights.[4] The prior Milestone 3C research also recorded that no general NAFDAC open licence or automated-ingestion permission had been verified. No new official permission statement was found during this assessment.

The existing `SourceRegistry` was not bypassed. No source was promoted to `approved_for_indexing`, because the required extraction and internal-indexing permissions were not confirmed. The correct registry representation, if the project later receives permission, is a draft or restricted record with unresolved permission fields until a responsible reviewer records the licence basis.

## Pipeline status

The intended pipeline remains unchanged:

`source → metadata → approval → extraction → provenance → index → retrieval → evidence bundle → governed answer → citation/claim validation`

The run stopped before extraction. Consequently:

- no real source record was approved;
- no real document was processed;
- no real chunks or hashes were added;
- no real content entered the lexical index;
- no real-source retrieval evaluation was run;
- no real-source answer was generated; and
- no citation or claim-support result is claimed for a real source.

The existing synthetic test fixtures and Milestone 3E.1 governance tests remain the only searchable knowledge content used by tests. The application runtime remains empty by default.

## Decision

**Permission limitation: stop and do not ingest.** This is a deliberate fail-closed result required by Milestone 3F. NAFDAC remains the appropriate Nigerian primary candidate for registration-status questions, but the project needs an item-specific permission decision or written authorization before any automated extraction or internal indexing.

The smallest corrective action is to obtain written permission from the relevant NAFDAC/Greenbook authority, or an explicit licence/official machine-readable service whose terms clearly authorize the intended internal indexing and user-facing use. The permission record must identify the exact endpoint or document, permitted actions, attribution requirements, retention limits, restrictions on derivative use, and whether third-party material is excluded. Until then, use a link-first workflow only and do not present copied source content as an indexed knowledge-base passage.

## Tests

No application code was changed for this blocked assessment. Existing project validation remains the prior Milestone 3E.1 result: 83 synthetic tests passed, compilation passed, and whitespace checks passed. No live provider request was made for Milestone 3F.

## Limitations and unresolved questions

- The public Greenbook interface does not establish the legal terms for automated collection or internal indexing.
- The privacy page is not a content licence and does not resolve copyright or database-right questions.
- The linked product document contains a third-party rights notice; its content cannot be treated as freely reusable.
- No legal conclusion is made about Nigerian copyright, database rights, government information reuse, or any third-party licence.
- Pharmacist and legal/licensing review remain required before controlled ingestion can begin.
- This report does not claim clinical accuracy, regulatory compliance, legal compliance, pharmacist validation, or production readiness.

## References

[1]: https://nafdac.gov.ng/drugs/ "NAFDAC Drugs — official drug database and regulatory resources"
[2]: https://greenbook.nafdac.gov.ng/ "NAFDAC Greenbook — Nigeria’s Registered Product Database"
[3]: https://admin.greenbook.nafdac.gov.ng/uploadImage/smpc_files/2024/09/23/20240923c315adff-9f0d-5c7d-bd6b-2d8215a02047.pdf "NAFDAC Greenbook product-information PDF with third-party rights notice"
[4]: https://greenbook.nafdac.gov.ng/privacy_policy.html "NAFDAC Greenbook privacy policy referring to Terms and Conditions"
