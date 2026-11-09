# Milestone 3E Read-Only Technical Audit

**Audit scope:** Commit `4ce3f717a75d2e8da89ac2d06178639a40b33135`

**Restrictions observed:** No implementation files, configuration, secrets, or packages were changed. No live Cloudflare or other provider request was made. This report is the only file written, as explicitly requested.

## Executive summary

The two shipped providers perform runtime evidence validation before model/network generation. The normal `/api/chat` path also abstains before provider construction when retrieval does not produce sufficient evidence. These controls reject empty, insufficient, stale, malformed, conflicting, and source-governance-invalid evidence.

However, Milestone 3E does **not** provide semantic claim verification. `CitationValidator` confirms that citation metadata identifies a retrieved passage; it does not determine whether the passage supports a factual statement. Generated provider text is not passed through `CitationValidator` or any claim-support checker before it is returned. A future provider can bypass validation because `Provider` is only a structural `Protocol` with a docstring, and `build_provider()` does not wrap or enforce implementations.

The default ingestion mode is also permissive for backward-compatible synthetic fixtures. A document marked `clinical_content=True` but lacking `source_id` can enter through the ordinary default `ApprovedDocumentIngestor(registry)` path if it satisfies the existing document approval checklist. The explicit `ApprovedDocumentIngestor.clinical()` path rejects that case, but selecting clinical mode is opt-in rather than automatic.

## Findings by question

### 1. Can either shipped provider generate with empty, invalid, stale, or insufficient evidence?

**Current answer: no for the shipped providers, with one ordering nuance.**

The normal path is `POST /api/chat` in `backend/main.py:92-180`. It calls `KnowledgeService.assess()` at lines 106–115. `KnowledgeDecision.can_answer` in `backend/knowledge/service.py:14-17` is true only for a sufficient bundle with passages. Otherwise the route returns `category=knowledge_abstention` before constructing a provider.

The providers independently validate evidence:

- `MockProvider.generate()` in `backend/providers/mock.py:16-45` calls `validate_evidence_bundle()` before producing its predetermined response.
- `CloudflareProvider.generate()` in `backend/providers/cloudflare.py:104-208` validates evidence at line 114 before creating the HTTP client or posting the request at lines 125–136.
- `EvidenceValidator.validate()` in `backend/knowledge/validation.py:75-117` rejects non-bundles, non-sufficient or empty bundles, missing provenance, invalid page/section data, missing content provenance, missing or stale verification, citation/chunk mismatches, and source-governance failures.

The Cloudflare provider checks credentials at lines 110–113 before evidence validation. Therefore, with missing Cloudflare credentials, an invalid evidence bundle produces a configuration error first; with configured credentials, invalid evidence is rejected before any network call. Neither shipped provider generates a response from such evidence.

This is metadata/governance validation, not proof that the passage semantically answers the question.

### 2. Can a future provider bypass the validator?

**Yes — high-severity extensibility gap.**

`backend/providers/base.py:53-64` defines `Provider` as a `Protocol`. Its requirement is descriptive: the docstring says implementations must validate evidence, but there is no runtime wrapper, abstract base class, decorator, or final validation layer.

`build_provider()` in `backend/main.py:82-89` returns any object selected by implementation, and `chat()` calls `provider.generate()` directly at lines 117–121. A future provider can therefore return `ProviderResult` without invoking `validate_evidence_bundle()`.

The existing test `tests/test_milestone3b.py:335-350` demonstrates this architectural fact: a stub provider that does not validate evidence is accepted and its response is returned.

### 3. Does `CitationValidator` establish semantic support?

**No. It validates metadata identity only.**

`CitationValidator.validate()` is in `backend/knowledge/validation.py:139-159`. It validates the evidence bundle, then checks each citation against at least one passage. `_matches()` at lines 178–191 compares publisher, title, version, publication date, page, section, source location, and optional document/source IDs.

It does not receive an answer, factual claim, or claim span. It does not compare claim language with passage text, perform entailment, evaluate query relevance, or determine whether the cited passage supports a particular statement.

### 4. Can a factual claim receive a valid but irrelevant citation and pass?

**Yes.**

If a citation exactly identifies any retrieved passage, `CitationValidator` can accept it even if that passage is irrelevant to a particular factual claim in the answer. The validator proves only that the citation points to retrieved evidence, not that the evidence supports the claim.

The current Cloudflare system also asks the model not to invent citations in `backend/providers/cloudflare.py:28-36`, but that is an instruction, not an enforcement mechanism.

### 5. Is generated answer text passed through `CitationValidator`?

**No.**

There is no production call site that sends generated answer text or generated citations to `CitationValidator`. The route calls the provider and returns `result.text` directly at `backend/main.py:117-120` and `172-180`.

`ProviderResult` in `backend/providers/base.py:46-50` contains only `text`, `simulated`, and an optional API-level `SourceReference`; it has no structured claim/citation representation for post-generation validation. `CloudflareProvider` only checks that `result.response` is a non-empty string at lines 194–208.

### 6. What happens when one citation is invalid and the rest are valid?

`CitationValidator.validate()` raises `CitationValidationError` on the first citation that does not match a retrieved passage at `backend/knowledge/validation.py:151-159`. It returns no partial tuple because the tuple is returned only after the loop completes.

This behavior is covered indirectly by the direct validator tests in `tests/test_milestone3e.py:110-138`, which use fabricated citations. There is no API/provider integration path for this behavior. `main.py` catches `EvidenceValidationError`, but not `CitationValidationError`, because citation validation is not currently invoked by the route.

### 7. Can unsupported factual claims still be returned?

**Yes.**

The route trusts `ProviderResult.text` and returns it as `status="ok"` at `backend/main.py:172-180`. There is no claim-to-evidence verification, unsupported-claim detector, or post-generation abstention.

The prompt instructions in the Cloudflare provider discourage unsupported claims, but prompts are not a safety boundary. A future provider, a test-injected provider, or a model response can return unsupported factual content after the input evidence gate has passed. The stub-provider test in `tests/test_milestone3b.py:335-350` accepts arbitrary provider text.

In the default application runtime, the knowledge index starts empty (`backend/main.py:39-41`), so normal requests abstain. Tests or future application code can inject approved synthetic evidence, after which this output-validation gap is reachable.

### 8. Can a clinical document without `source_id` enter normal ingestion?

**Yes through the default programmatic ingestion path; no public ingestion HTTP route currently exists.**

`DocumentProcessor` defaults to `mode="synthetic"` at `backend/knowledge/processing.py:25-36`. `IngestionPolicy.validate_document()` requires `source_id` only when `mode == "clinical"` at `backend/knowledge/validation.py:33-43`.

`ApprovedDocumentIngestor(registry)` constructs the default processor at `backend/knowledge/processing.py:136-142`. Therefore, an approved document marked `clinical_content=True` but lacking `source_id` can be processed through that ordinary constructor. `clinical_content` affects pharmacist approval checklist requirements in `backend/knowledge/models.py:186-195`, but it does not automatically select clinical ingestion mode.

`ApprovedDocumentIngestor.clinical()` at `processing.py:143-146` is stricter and rejects missing source identity, but it is opt-in. The existing test `tests/test_milestone3e.py:166-173` tests only explicit clinical mode, leaving the default-path gap uncovered.

### 9. Are synthetic test-only ingestion exceptions accessible through production routes?

**There is no production ingestion route in the current application.**

`backend/main.py` exposes landing, prototype, health, asset, route-manifest, and `/api/chat` routes only. The runtime initializes `KnowledgeService.empty()` and does not seed synthetic fixtures.

The fixture module declares itself synthetic-only in `tests/helpers.py:1`, and tests inject it by monkeypatching `main.knowledge_service`. Therefore, the current published application does not expose a route that accepts arbitrary synthetic documents.

The isolation is architectural rather than enforced by a production-mode guard: the public Python classes still expose default synthetic-compatible ingestion behavior, and `/api/chat` has no check distinguishing synthetic from clinical evidence if application code later injects such evidence. This is a medium-severity future configuration risk, not a currently exposed HTTP ingestion route.

### 10. Are withdrawn, expired, or restricted sources rechecked immediately before final answer delivery?

**They are rechecked before provider generation, but not after generation and before response delivery.**

Retrieval filters source eligibility in `backend/knowledge/retrieval.py:72-88` and `_source_can_index()` at lines 102–110. The provider then revalidates source governance through `EvidenceValidator` at `backend/knowledge/validation.py:98-116`. `main.build_provider()` passes the active registry to both shipped providers at `backend/main.py:82-86`.

The source registry correctly treats restricted, rejected, expired, due, withdrawn, and permission-invalid sources as unavailable through `SourceRegistry.can_index()` and `governance_issues()` in `backend/knowledge/source_registry.py:133-175`.

There is no revalidation after the model returns. If source status changes while a provider request is in flight, or if generated output is unsupported despite valid input evidence, `main.py:172-180` returns the text without a final source or claim check. This is a high-severity race/output-governance gap for a future clinical runtime.

### 11. Do existing tests cover these scenarios?

They cover the shipped-provider input boundary well, but leave the output and extensibility gaps open.

Covered:

- Empty, insufficient, conflicting, stale, malformed, and source-governance-invalid evidence rejection in `tests/test_milestone3e.py:32-107`.
- Citation metadata mismatch and absent-citation rejection in `tests/test_milestone3e.py:110-138`.
- Weak retrieval overlap and explicit conflict groups in `tests/test_milestone3e.py:141-163`.
- Explicit clinical-mode source requirement in `tests/test_milestone3e.py:166-173`.
- Safe API abstention on `EvidenceValidationError` in `tests/test_milestone3e.py:176-190`.
- Empty runtime abstention before provider construction in `tests/test_milestone3b.py:319-333`.
- Existing source governance, approval, withdrawal, expiry, and retrieval exclusion behavior in `tests/test_milestone3d.py`.

Important gaps:

- No test proves that a future provider lacking validation is rejected; the current stub test demonstrates that it is accepted.
- No test passes generated answer claims through `CitationValidator` because no such production path exists.
- No semantic entailment, claim relevance, unsupported-claim, or irrelevant-but-metadata-valid citation test exists.
- No API-level test covers one invalid citation among otherwise valid citations.
- No test changes source governance during provider execution and checks final-answer suppression.
- No test proves that a `clinical_content=True` document without `source_id` is rejected by the default `ApprovedDocumentIngestor(registry)` path.
- No production-route test distinguishes synthetic evidence from clinical evidence.
- No test maps a future `CitationValidationError` safely at the API boundary.

## Full test results

Command executed:

```text
python3 -m pytest -q --disable-warnings
```

Result:

```text
67 passed
```

No live provider request was made. The Cloudflare HTTP client was not used by the audit; the test suite uses mocked/no-network paths.

## Final audit conclusion

Milestone 3E is effective as an **input evidence and provenance-governance skeleton for the two current providers**. It is not yet an answer-verification system. The highest-priority gaps before real clinical ingestion are:

1. Enforce evidence validation in a final provider wrapper or non-bypassable base implementation.
2. Introduce a structured answer/claim representation if citation validation is required.
3. Validate every generated claim against retrieved evidence; metadata matching alone is insufficient.
4. Add a final source/evidence validity check before returning an answer, while defining behavior for changes during provider execution.
5. Make clinical ingestion the safe default for `clinical_content=True`, or prohibit source-less clinical records in all ingestion modes.
6. Keep synthetic fixtures explicitly unavailable to production configuration and routes.

This audit does not claim clinical safety, semantic factuality, medication accuracy, or production readiness.

## Change and credential confirmation

- Implementation files modified during this audit: **none**.
- Configuration or secret changes: **none**.
- Packages installed: **none**.
- Live provider requests: **none**.
- Audit report created: `MILESTONE3E_READ_ONLY_AUDIT.md`.
- Git commit inspected: `4ce3f717a75d2e8da89ac2d06178639a40b33135`.
