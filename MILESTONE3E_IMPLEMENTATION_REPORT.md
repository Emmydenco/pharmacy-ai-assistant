# Milestone 3E Implementation Report

## Scope

Milestone 3E strengthens the synthetic-only knowledge-base skeleton without ingesting real clinical documents, scraping the web, adding patient data, or making a live provider request. The work focuses on evidence validation, provenance-safe citations, retrieval reliability, explicit ingestion modes, and provider-boundary enforcement.

## Implemented changes

### Runtime evidence validation

`backend/knowledge/validation.py` adds `EvidenceValidator`. Before either provider can generate, it checks that the bundle is a real `EvidenceBundle`, is sufficient and non-empty, has complete document/page/section/source/content provenance, has a recent verification date, and has citations matching the retrieved chunk. Source-linked evidence additionally requires an active source registry record that is approved for internal indexing.

`backend/providers/mock.py` and `backend/providers/cloudflare.py` call this validator before producing output or making an HTTP request. `backend/main.py` converts an internal validation failure into a safe knowledge abstention without returning validation details. The provider protocol documents this runtime obligation rather than treating it as convention only.

### Citation integrity

`CitationValidator` accepts citations only when their publisher, title, version, publication date, page, section, source location, and optional document/source identifiers match a passage in the retrieved evidence bundle. A citation supplied by a model or caller cannot become verified merely because it is well formatted; it must correspond to retrieved evidence.

`Citation` now carries an optional `document_id`, and `KnowledgeChunk`/`DocumentSection` carry an explicit optional `conflict_group` for future structured conflict review.

### Retrieval reliability

`InMemoryKnowledgeIndex` now supports a minimum term-match requirement in addition to the relevance threshold, optional jurisdiction filtering, and a small ranking preference for primary sources. Conflict detection uses `conflict_group` when present and falls back to the existing `claim_key` for backward-compatible synthetic fixtures. Existing abstention behavior remains in place for no-match, stale, unapproved, or conflicting results.

### Ingestion policy boundary

`IngestionPolicy` makes the boundary explicit between the current `synthetic` mode and a future `clinical` mode. `ApprovedDocumentIngestor.clinical()` is an opt-in constructor that requires source identity and source-governance checks. The default fixtures remain synthetic and do not seed application runtime data.

## Files created or modified

- Created `backend/knowledge/validation.py`.
- Created `tests/test_milestone3e.py`.
- Modified `backend/knowledge/models.py` for document identity and conflict provenance.
- Modified `backend/knowledge/processing.py` for explicit ingestion modes and preserved provenance.
- Modified `backend/knowledge/retrieval.py` for match coverage, jurisdiction filtering, primary-source ranking, and explicit conflict groups.
- Modified `backend/providers/base.py`, `backend/providers/mock.py`, and `backend/providers/cloudflare.py` for provider-level evidence enforcement.
- Modified `backend/main.py` for safe validation abstention and registry-bound provider construction.
- Modified `backend/knowledge/__init__.py` to export the new policy and validator interfaces.
- Modified `tests/helpers.py` to keep synthetic fixture provenance complete.

## Validation

- Focused Milestone 3E, 3B, and 3D tests: **31 passed**.
- Full repository test suite: **67 passed**.
- Python compilation: passed with `python3 -m compileall -q backend tests`.
- Whitespace check: passed with `git diff --check`.
- No live Cloudflare request was made.

## Known limitations

The retrieval engine remains deterministic lexical matching over an in-memory index; it is not a clinical-grade semantic retrieval system. Authority ranking is a bounded heuristic, not a clinical adjudication process. Jurisdiction metadata is only useful when source records are populated and correctly reviewed. The clinical ingestion constructor establishes a boundary but does not implement PDF/HTML extraction, licensing review, pharmacist approval operations, durable storage, or production source acquisition. The project still requires pharmacist-reviewed evaluation data and operational governance before any real medication documents are considered.

This milestone does not establish clinical safety, medication accuracy, legal permission, or production readiness.
