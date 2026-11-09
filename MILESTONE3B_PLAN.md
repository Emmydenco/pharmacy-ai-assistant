# Milestone 3B — Knowledge-base infrastructure skeleton

## Objective

Add a governed, empty-by-default knowledge-base boundary so the Pharmacy Patient Assistant cannot send an allowed question to an LLM unless approved evidence has been retrieved. This milestone adds infrastructure and tests only. It does not ingest real clinical documents or add medication content.

## Proposed structure

```text
backend/knowledge/
  __init__.py       Public knowledge-base types and service exports
  models.py         Document metadata, approval checks, pages, sections,
                    knowledge chunks, citations and evidence bundles
  registry.py       In-memory document registry and approval gate
  processing.py     Approved-document ingestion interface and page/section
                    validation with provenance-preserving chunk creation
  retrieval.py      In-memory lexical index, relevance thresholding and
                    deterministic conflict detection
  service.py        Empty-by-default knowledge service and abstention decisions

tests/test_milestone3b.py  Synthetic-only registry, ingestion, provenance,
                           retrieval, citation, conflict and API-gating tests
```

The existing provider interface will accept an `EvidenceBundle`. The Cloudflare adapter will include the approved evidence and citation metadata in the model context, while the mock provider will retain its clearly simulated behavior. The FastAPI route will run policy screening first, then require a sufficient evidence bundle; an empty or conflicting index returns the existing `blocked` response shape with a knowledge-abstention category and never constructs a provider.

## Governance decisions

- Documents enter the registry as pending and must pass authenticity, publisher, relevance, currency, licensing, content-quality and—when clinical—pharmacist approval checks.
- Only registry records with approved status may be processed or indexed.
- The processor accepts structured synthetic document pages and sections, not arbitrary URLs or scraped content.
- Every chunk retains document identity, title, publisher, version, page, section, source location, content hash and citation metadata.
- Retrieval returns sufficient, insufficient or conflicting evidence. Missing, weak, outdated, incomplete or conflicting evidence produces abstention.
- The production service starts with an empty index. Synthetic fixtures exist only in tests and are not seeded into runtime state.

## Non-goals

No database, vector store, embeddings, web crawler, arbitrary document downloader, clinical knowledge content, patient data, accounts, inventory, pharmacist dashboard or Milestone 3C work is included.
