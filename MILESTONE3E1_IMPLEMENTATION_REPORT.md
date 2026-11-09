# Milestone 3E.1 — Evidence Enforcement and Answer Validation Hardening

## Status

Milestone 3E.1 is implemented against the read-only findings in `MILESTONE3E_READ_ONLY_AUDIT.md`. The change preserves the existing FastAPI application, plain HTML/CSS/JavaScript frontend, Cloudflare adapter, mock provider, deterministic safety checks, and `/api/chat` response contract. No real clinical or medication documents were added, no patient information was used, and no live Cloudflare request was made.

## Audit findings addressed

### 1. Provider bypass risk

The earlier provider interface was a structural `Protocol`; a future provider could technically be called without applying the evidence validator. `backend/providers/base.py` now defines `GovernedProvider` and `ensure_governed_provider`. The wrapper validates the `EvidenceBundle` before calling the underlying provider, validates the returned `ProviderResult`, and performs final evidence/source-governance validation before delivery. `backend/main.py` constructs both Cloudflare and mock providers through this boundary and wraps them again defensively at the route boundary. A deliberately non-compliant stub provider is tested to confirm invalid evidence is rejected before its `generate` method runs.

This is an application construction boundary, not a language-level guarantee against arbitrary code importing and directly instantiating an implementation outside the normal application path. The normal runtime path is governed.

### 2. Structured answers and claim relationships

`backend/answers.py` adds `StructuredAnswer` and `AnswerClaim`. Conversational text can remain general wording, while factual claims must include claim text, supporting evidence passage IDs, and citation references. The central provider boundary rejects empty or malformed results and normalizes plain provider text into conversational text with no factual claims. It does not treat plain text as verified medication information.

### 3. Claim-to-evidence validation

`backend/knowledge/validation.py` now keeps citation identity checking and claim-support checking as separate operations. `CitationValidator` verifies that a citation matches the exact retrieved passage metadata. `validate_structured_answer` additionally requires each claim to identify its own passages and citations and requires the meaningful claim terms to occur in at least one of those specific passages. Irrelevant but genuine citations, missing support, unknown passage IDs, and ambiguous multi-passage support fail closed. Explicit conflicting evidence is rejected before claim validation.

The claim-support check is deliberately conservative lexical matching. It is not semantic verification, clinical validation, or proof that a generated statement is medically correct. No claim is made that this prevents all unsupported or misleading language.

### 4. Post-generation validation and safe API behavior

The normal path is now:

`request → deterministic safety policy → retrieval → evidence assessment → governed provider → structured result validation → citation/claim validation → final source-governance check → response`.

`backend/main.py` catches evidence, answer, citation, and provider-result validation failures and returns the existing safe `blocked` response shape with `category=knowledge_abstention`. Internal validation details, raw provider content, credentials, and patient information are not returned. The API does not silently remove invalid citations while retaining an unsupported answer.

### 5. Final source-governance revalidation

`GovernedProvider` revalidates the evidence bundle after the underlying provider returns. This checks the same provenance and current source governance used before generation. A synthetic provider test changes a source to restricted during its simulated call; the generated result is suppressed and a validation error is raised instead of returning it.

### 6. Clinical ingestion boundary

`DocumentProcessor` and `IngestionPolicy` use `clinical` as the default mode. `ApprovedDocumentIngestor` always constructs a clinical-governed processor and no longer accepts an injectable processor that could silently select a compatibility mode. Clinical content requires a source ID, a configured source registry, an active source approved for internal indexing, and confirmed extraction and internal-indexing permissions.

Synthetic fixtures explicitly use `DocumentProcessor(..., mode="test_synthetic")` inside test helpers. The test-only mode is not an application setting, normal provider construction option, or FastAPI ingestion route. A clinical document without a source ID is covered by regression tests and is rejected.

## Files created or modified

Created:

- `backend/answers.py` — structured conversational answers and factual claims.
- `tests/test_milestone3e1.py` — synthetic hardening coverage.
- `MILESTONE3E1_IMPLEMENTATION_REPORT.md` — this report.

Modified:

- `backend/providers/base.py` — central governed provider wrapper and result validation.
- `backend/main.py` — governed provider construction and safe validation abstention handling.
- `backend/knowledge/validation.py` — claim support checks and explicit `test_synthetic` versus `clinical` modes.
- `backend/knowledge/processing.py` — clinical-governed default ingestion and non-injectable normal ingestor.
- `backend/knowledge/__init__.py` — exports validation interfaces.
- `tests/helpers.py` — explicit synthetic-only fixture mode.
- `tests/test_milestone3b.py` — legacy synthetic ingestion test updated to use the explicit test-only processor.
- `README.md` — Milestone 3E.1 architecture and limitations.
- `TODO.md` — Milestone 3E.1 acceptance outcomes marked complete.

The prior `MILESTONE3E_READ_ONLY_AUDIT.md` remains a read-only audit artifact and was not used as a source of clinical facts.

## Tests and checks

The complete suite was run with:

```text
python3 -m pytest -q --disable-warnings
........................................................................ [ 86%]
...........                                                              [100%]
```

Result: all 83 collected tests passed, including the new provider-boundary, malformed-result, claim-support, citation, API-abstention, source-revalidation, clinical-ingestion, permission, and test-only-pathway cases.

Additional checks passed:

```text
python3 -m compileall -q backend tests
 git diff --check
```

The checks used synthetic fixtures only. No live provider request was made.

## Known limitations and deliberately deferred work

- Lexical claim-to-passage matching is a conservative safeguard, not semantic, clinical, or pharmacist verification.
- Plain conversational text is not parsed into factual claims automatically; provider-produced factual claims must use the structured representation to be validated.
- The runtime knowledge base remains empty by default.
- No real medication documents were downloaded, scraped, indexed, or cited.
- No pharmacist-reviewed evaluation set, durable registry/index, extraction pipeline for real formats, legal/licensing decision, patient-data workflow, inventory integration, authentication, pharmacist dashboard, or clinical deployment was added.
- Cloudflare remains hosted-only and unchanged; the project makes no live connectivity claim in this milestone.

## Safety and privacy confirmation

The implementation does not expose API credentials, account identifiers, authorization headers, raw provider bodies, prompts, generated responses, or patient information through the new validation paths. The project remains a synthetic-only prototype and does not claim clinical validation or production readiness.
