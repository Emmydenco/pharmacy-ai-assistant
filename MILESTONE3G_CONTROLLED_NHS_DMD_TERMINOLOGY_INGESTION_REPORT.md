# Milestone 3G — Controlled NHS dm+d Terminology Ingestion Report

**Date:** 6 November 2026  
**Status:** **STOPPED BEFORE RETRIEVAL AND INGESTION**  
**Source proposed:** NHSBSA dm+d, TRUD item 24, Release 11.0.0, Week 45, released 2 November 2026  
**Current Git checkpoint:** `d2da46891b0923ef93e6111688b36aaac0b53104`

## Executive summary

Milestone 3G did not proceed to TRUD authentication, release retrieval, archive inspection, record selection, or ingestion.

The existing governed knowledge architecture cannot currently preserve all mandatory provenance and approval metadata required by this milestone. In particular, it cannot safely represent, on the source/document/chunk path:

- the exact archive filename;
- the archive SHA-256 checksum;
- the authenticated TRUD release metadata;
- the exact file manifest;
- licence URL and required attribution as structured provenance;
- file-level or field-level rights approval; or
- a typed distinction that prevents terminology-only evidence from satisfying clinical evidence requirements.

The instructions require stopping if existing governance cannot represent the source safely. Continuing would require either modifying application code or bypassing the governed ingestion path, both of which are prohibited for this milestone.

**Result:** no credentials were requested, no TRUD API key was used, no external package was retrieved, no medication content was added, no source was approved, no registry permissions changed, no live Cloudflare request was made, and no application code was modified.

## 1. Exact source/release intended for the experiment

The intended candidate remains the exact release verified in Milestone 3F.3:

- **Publisher:** NHS Business Services Authority (NHSBSA)
- **Dataset:** NHS dm+d — “dm+d in a vendor-neutral format”
- **TRUD item:** 24
- **Release:** 11.0.0
- **Week:** 45
- **Release date:** 2 November 2026
- **Format:** XML dm+d release, with supporting release/mapping material described by NHSBSA
- **Jurisdiction:** United Kingdom
- **Licence listed by TRUD:** Open Government Licence for TRUD
- **Release page:** https://isd.digital.nhs.uk/trud/user/guest/group/0/pack/6/subpack/24/releases
- **Licence page:** https://isd.digital.nhs.uk/trud/users/guest/filters/0/categories/6/items/24/licences

These identifiers were not used to retrieve the release in this milestone. No archive filename or checksum is claimed because no authenticated TRUD release response was obtained.

## 2. Hard-stop findings

### 2.1 Required release and licence metadata cannot be stored completely

The current `SourceRecord` in `backend/knowledge/models.py` stores general source identity, including `source_id`, `source_name`, `publisher`, `official_url`, `source_category`, `jurisdiction`, market, authority information, permissions, review dates, and review status.

It does **not** contain fields for:

- licence name;
- licence URL;
- required attribution text;
- TRUD item number;
- exact release number and week;
- release date separate from general publication date;
- archive filename;
- archive SHA-256 checksum;
- manifest/file list;
- approved file identifiers;
- approved field identifiers; or
- source-status metadata tied to a specific release.

The `SourceRegistry.approve_for_indexing()` transition in `backend/knowledge/source_registry.py` approves a source at the source-record level. It checks general extraction and internal-indexing permission statuses, but it cannot scope approval to item 24, Release 11.0.0, exact files, or exact fields.

This is insufficient for the milestone requirement that approval be limited to the exact inspected release, exact files, exact fields, and exact terminology use case.

### 2.2 Document and chunk provenance cannot carry the required checksum and licence data

`DocumentMetadata` in `backend/knowledge/models.py` contains document identity, title, publisher, publication date, version, source location, acquisition date, review status, licensing status, verification date, clinical-content flag, and optional `source_id`.

`KnowledgeChunk` and `Citation` contain document and passage coordinates, source location/reference, source ID, version, publisher, and verification date. They do not contain:

- archive filename;
- archive SHA-256 checksum;
- TRUD item number;
- release week/date as dedicated source metadata;
- licence name or licence URL;
- attribution text;
- approved file/field identifiers; or
- a durable source-status snapshot.

Putting these values into an unstructured `source_reference` string would not meet the required structured provenance guarantee and would be a bypass rather than a safe implementation.

### 2.3 The ingestion path cannot enforce file-level or field-level approval

`DocumentProcessor.process()` in `backend/knowledge/processing.py` verifies that:

1. the package matches a registered document;
2. the document is approved;
3. a verification date exists;
4. the ingestion policy accepts the document; and
5. pages and sections have valid structure.

It does not verify a release manifest, archive checksum, approved XML file, approved field set, or field-level licence decision. The existing policy is document/source-level, not file/field-level.

The milestone explicitly requires excluding any field or file with unresolved rights. The current processor cannot prove that only rights-cleared dm+d fields entered the index.

### 2.4 Terminology-only records cannot be prevented from satisfying clinical evidence requirements

The current models have a free-form `source_category` field and an `authority_limitations` tuple, but they do not define a typed `source_type` such as `terminology_product_identity` versus `clinical_medication_evidence`.

`EvidenceValidator` in `backend/knowledge/validation.py` validates evidence status, freshness, document provenance, citation matching, source registration, and indexing approval. It does not inspect a source category/type to reject terminology-only evidence when a clinical evidence bundle is required.

`InMemoryKnowledgeIndex.retrieve()` in `backend/knowledge/retrieval.py` can return any approved, relevant source-linked chunk. It applies source approval, freshness, jurisdiction, and lexical relevance, but not an evidence-capability rule that excludes terminology sources from clinical claims.

Therefore, ingesting NHS dm+d records now could create a governance failure in which terminology passages are treated as generally sufficient evidence by later clinical runtime paths. Preventing that requires a code-level source-capability boundary, which this milestone forbids us from adding.

### 2.5 Rollback cannot be proven for the required release identity

The current index uses an in-memory dictionary keyed by `chunk_id`. It can reject duplicate chunk IDs, but there is no existing release-scoped rollback operation that can:

- identify all chunks by TRUD item, release, archive checksum, and approved file;
- remove only the selected real-source records;
- verify no orphaned citations or source references remain; and
- prove synthetic fixtures were unaffected.

A manual deletion of guessed chunk IDs would not satisfy the required rollback guarantee. Implementing safe rollback requires structured release identity on indexed records and a tested removal operation.

## 3. Existing governance path reviewed

The intended path would be:

`SourceRegistry → DocumentRegistry → IngestionPolicy → DocumentProcessor → InMemoryKnowledgeIndex → Retrieval → EvidenceValidator → Citation/answer validation → provider boundary`

The path is correctly fail-closed for general source approval and evidence freshness. However, it lacks the exact-release and terminology-capability controls required for this experiment. The safe conclusion is to stop rather than create a parallel one-off ingestion route.

## 4. Security and access result

No TRUD account or API key was requested or used.

Consequently:

- no credential was entered into chat;
- no credential was placed in source code, environment files, README files, or terminal commands;
- no credential was printed, logged, hashed, or exposed;
- no release archive was downloaded;
- no external medication data entered the project; and
- no recurring downloader was created.

This is intentional because the architecture hard stop occurred before the access step.

## 5. Retrieval, abstention, citation, and rollback results

These tests were **not executed against real dm+d data**, because no data was retrieved or ingested.

| Required test | Result | Reason |
|---|---|---|
| Terminology retrieval | Not run | No real records entered the index. |
| Clinical-question abstention | Not run against dm+d | Current architecture lacks an explicit typed terminology-vs-clinical evidence boundary. |
| Nigerian-regulatory abstention | Not run against dm+d | No real records entered the index; source capability boundary remains incomplete. |
| Dosing-question abstention | Not run against dm+d | No real records entered the index; source capability boundary remains incomplete. |
| Complete provenance | Not demonstrated | Required checksum/licence/release fields are not representable end-to-end. |
| Citation integrity | Not demonstrated against dm+d | No real citation was created. Existing citation identity checks remain synthetic/test-scoped. |
| Complete rollback | Not demonstrated | No release-scoped rollback operation exists. |

## 6. Local test results

The existing test suite was run without changing application behavior:

- **Pytest:** passed; all collected tests passed.
- **Compile check:** passed with `python3 -m compileall -q backend tests`.
- **Whitespace check:** passed with `git diff --check`.
- **Live Cloudflare request:** not made.
- **TRUD request:** not made.
- **Application code changes:** none.

The current working tree contains only the research/report artifacts from the preceding source-verification milestones and this report; no application implementation was modified.

## 7. Required changes before Milestone 3G can proceed

A future approved implementation milestone must add and test, at minimum:

1. **Typed source capabilities:** represent `terminology_product_identity` separately from clinical evidence and enforce the distinction in retrieval and evidence validation.
2. **Release identity:** store TRUD item number, release number, week, release date, archive filename, and SHA-256 checksum as structured metadata.
3. **Licence provenance:** store licence name, licence URL, attribution text, verification date, and source-status snapshot.
4. **File/field approval:** represent the exact approved files and fields; reject any package containing unapproved or unresolved components.
5. **Provenance propagation:** carry release/checksum/licence/file/field metadata into every derived record, chunk, and citation.
6. **Release-scoped rollback:** remove and verify all records for one source/release without affecting synthetic fixtures or unrelated sources.
7. **Safe TRUD access:** use a protected secret only after the implementation can safely consume the release metadata; do not place credentials in code or logs.
8. **Tests:** add tests proving that terminology evidence cannot satisfy clinical or Nigerian-regulatory questions, that incomplete provenance is rejected, and that rollback leaves no orphaned references.

Those are application-code and governance changes outside the current milestone’s permitted scope.

## 8. Recommendation for the next milestone

Do not retrieve or ingest NHS dm+d yet. Begin a narrowly scoped architecture-hardening milestone first. That milestone should be approved to modify the existing knowledge models, registry, ingestion policy, retrieval filters, and rollback tests—but should still use synthetic release metadata until the new controls pass review.

Only after those controls are implemented and reviewed should a separate milestone request one protected TRUD credential, retrieve exactly item 24 Release 11.0.0, inspect the archive, and approve a 20–30-record terminology sample.

Successful future terminology ingestion would not establish clinical validation, Nigerian regulatory compliance, Nigerian availability, or readiness for patient use.

## Final result

**Milestone 3G: STOPPED BEFORE INGESTION due to an existing-governance capability gap.**

No hard-stop condition was worked around.
