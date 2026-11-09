# Milestone 3D Implementation Report

**Project:** Pharmacy Patient Assistant

**Milestone:** 3D — Source Registry and Governance Implementation

**Status:** Implemented and tested with synthetic records only.

## Summary of changes

Milestone 3D adds a storage-independent Source Registry and Governance layer on top of the approved Milestone 3B knowledge-base skeleton. The new layer manages source metadata and permissions before any document can be linked to the internal knowledge index. It does not download, scrape, ingest, or seed real medication documents.

The implementation deliberately keeps the existing FastAPI, plain HTML/CSS/JavaScript, in-memory registry, lexical retrieval, provider interface, Cloudflare adapter, mock provider, deterministic safety checks, and `/api/chat` contract. No new framework, database, authentication system, dashboard, or external clinical data source was introduced.

## Files created

- `backend/knowledge/source_registry.py` — in-memory source registry, source workflow transitions, permission gates, review-date checks, withdrawal handling, and metadata conflict detection.
- `backend/knowledge/routing.py` — configurable question-category to source-category routing rules.
- `tests/test_milestone3d.py` — synthetic tests for source validation, permissions, workflow, routing, expiry, withdrawal, ingestion, and retrieval exclusion.
- `MILESTONE3D_IMPLEMENTATION_REPORT.md` — this report.

## Files modified

- `backend/knowledge/models.py` — adds `SourceRecord`, `SourcePermissions`, source workflow types, optional `source_id` document/chunk provenance, and runtime validation of source metadata and permission statuses.
- `backend/knowledge/registry.py` — accepts an optional `SourceRegistry` and rejects source-linked document registration unless the source is explicitly approved for internal indexing.
- `backend/knowledge/processing.py` — rechecks source indexing permission during processing and carries `source_id` into citations and chunks.
- `backend/knowledge/retrieval.py` — requires source-linked chunks to have explicit indexing permission when added and excludes them from retrieval if the source later becomes restricted, withdrawn, expired, or due for review.
- `backend/knowledge/__init__.py` — exports the new source-governance interfaces.
- `README.md` — documents the Milestone 3D architecture, workflow, routing boundary, permission separation, and limitations.
- `TODO.md` — records and marks the Milestone 3D outcomes complete.

## Source registry data model

`SourceRecord` contains the following groups of metadata:

- **Identity:** unique source ID, source name, publisher, official URL, and source category.
- **Jurisdiction:** jurisdiction, applicable market, and national/international classification.
- **Authority:** authoritative information categories, authority limitations, and primary/supplementary classification.
- **Permissions:** separate statuses for public accessibility, linking, downloading, extraction, internal indexing, and reproduction.
- **Verification and governance:** publication date, last verification date, next review date, workflow status, reviewer, approval date, review notes, and withdrawal flag.

Permission statuses are explicit: `confirmed_permitted`, `restricted`, `permission_required`, `not_verified`, and `prohibited`. Runtime validation rejects unsupported statuses. The registry never treats a public URL as permission to download, extract, internally index, reproduce, or train on content.

## Governance workflow

The source workflow is:

```text
draft
  -> pending_review
  -> approved_for_linking
  -> approved_for_indexing
```

The registry also supports `restricted`, `rejected`, and `expired` states. The transitions are intentionally narrower than a single approval flag:

- New records must begin in `draft`.
- `submit_for_review` moves a draft to `pending_review`.
- `approve_for_linking` requires a reviewer, verification date, next review date, and confirmed linking permission.
- `approve_for_indexing` can only follow linking approval and additionally requires confirmed extraction and internal-indexing permission.
- `restrict`, `reject`, `expire`, and `withdraw` record a reason or note and make the source unavailable for routing or indexing.

A source that is due for review, lacks a verification date, lacks a next review date, has withdrawn or rejected status, or has unverified/restricted/prohibited permissions is surfaced through `governance_issues`. Duplicate official URLs with inconsistent publisher, jurisdiction, market, or category metadata are reported by `metadata_conflicts`.

## Question-to-source routing

`SourceRouter` is configurable and ships with synthetic, category-level rules based on Milestone 3C:

- Nigerian drug registration, recalls, and safety alerts → `nigerian_regulatory`.
- Nigerian pharmacy practice and professional regulation → `nigerian_pharmacy_regulation`.
- Nigerian national health policy → `nigerian_health_policy`.
- International public-health recommendations → `international_public_health`.
- International regulatory product information → `international_regulatory_product_information`.
- Exact product information → `product_information` or `manufacturer_product_information`.
- General patient education → `patient_information`.

Routing returns currently link-approved source records in matching categories. It is only a source-selection aid. It does not grant permission to generate an answer, override deterministic safety checks, or replace pharmacist review.

## Integration with the existing knowledge base

Source-linked `DocumentMetadata` records may carry an optional `source_id`. When a source ID is present:

1. `DocumentRegistry.register` requires a configured `SourceRegistry`.
2. The source must already be `approved_for_indexing` and have explicit extraction and internal-indexing permission.
3. `ApprovedDocumentIngestor` and `DocumentProcessor` recheck the source gate before accepting or processing the package.
4. `KnowledgeChunk` and `Citation` preserve the source ID alongside the existing document, page, heading, version, hash, and source-reference provenance.
5. `InMemoryKnowledgeIndex.add` repeats the source gate.
6. Retrieval skips source-linked chunks if the source is later restricted, withdrawn, expired, or due for review.

This prevents a record from entering retrieval merely because it exists in the source registry. Linking approval is never treated as indexing approval. Existing Milestone 3B synthetic document fixtures without `source_id` remain compatible; no source-linked material is loaded by the application at startup.

## Testing and results

The test suite uses only synthetic source records and fictional document content. It covers:

- Source identity validation and unique source IDs.
- Runtime validation of permission statuses.
- Jurisdiction, authority, category, and primary/supplementary metadata.
- Draft → pending review → linking approval → indexing approval transitions.
- Separation of linking permission from extraction and internal-indexing permission.
- Missing verification dates, missing next review dates, due reviews, rejected sources, restricted/withdrawn sources, and metadata conflicts.
- Configurable question-to-source routing.
- Ingestion rejection when indexing permission is insufficient.
- Rechecking source approval during ingestion.
- Retrieval exclusion after source expiry.
- Existing Milestone 3B governance, provenance, citation, conflict, abstention, provider-gating, and API-compatibility tests.

Validation performed:

```text
python3 -m pytest -q --disable-warnings
54 passed

python3 -m compileall -q backend tests
success

git diff --check
success

GET /health using FastAPI TestClient
HTTP 200

GET /manus-routes.json using FastAPI TestClient
HTTP 200
```

## Known limitations

- The registry is in memory and is not durable across process restarts.
- There is no database, audit log, role-based reviewer identity, signed approval record, or automatic scheduled review job.
- Source metadata is not populated with real NAFDAC, PCN, FMoHSW, WHO, EMA, FDA, manufacturer, Martindale, BNF, or MedlinePlus records. The Milestone 3C report remains the research reference, but this milestone does not import its real source records into the runtime.
- Permission values are governance assertions supplied by a reviewer; the code does not independently prove copyright, contract, API, database-rights, or regulatory permission.
- Metadata conflict detection currently compares records sharing an official URL. It is not a general semantic conflict detector.
- Routing maps declared question categories to source categories; it does not classify arbitrary user questions and does not make clinical decisions.
- The existing lexical retrieval index and safety keyword policy remain prototypes. Passing tests do not establish clinical validation, legal compliance, medication accuracy, or production safety.
- Source currency is checked against stored dates. The system does not independently contact or verify external websites.
- Documents without a `source_id` remain supported for the earlier synthetic Milestone 3B fixtures. Future clinical ingestion should require source-linked records rather than relying on this backward-compatible path.

## Features deliberately deferred

The following are not part of Milestone 3D:

- Downloading, scraping, parsing, or ingesting real medication documents.
- Populating the registry with real source records or clinical facts.
- Patient accounts, patient-identifying information, inventory, dashboards, authentication, or pharmacist workflow tools.
- Durable database storage or a production audit trail.
- Automated clinical question classification, prescribing, diagnosis, dose changes, interaction clearance, or emergency triage.
- Legal conclusions about NDPA compliance, copyright, database rights, or source licences.
- Clinical validation or pharmacist-reviewed retrieval evaluation beyond synthetic tests.

## Safety and provider compatibility confirmation

The implementation does not change the Cloudflare provider adapter, server-side credential boundary, mock provider, deterministic safety checks, or provider error handling. `/api/chat` continues to run safety screening before knowledge retrieval and only constructs a provider after a sufficient evidence bundle is available. No live Cloudflare request was made for this milestone, and no credentials or patient information were accessed or modified.

## Git checkpoint

The implementation checkpoint is `00ede469f451f771456e5c792f116c7c96a9050a`. The checkpoint includes only the files listed above and the Milestone 3C research report; no generated clinical content or secrets are included.
