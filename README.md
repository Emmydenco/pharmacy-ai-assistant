# Pharmacy Patient Assistant — Milestones 3B–3E.1

This repository contains a responsive pharmacy product overview at `/` and a small hosted-inference prototype at `/prototype`. Milestones 3B–3E add a governed knowledge-base skeleton, source-governance layer, and evidence-reliability boundary while preserving the existing FastAPI API contract, Cloudflare boundary, and deterministic safety checks.

This remains a prototype, not a clinical system. The runtime knowledge index is empty by default. The application does not diagnose, prescribe, recommend prescription changes, ingest clinical documents, cite verified medication sources, query inventory, persist conversations, authenticate users, or store patient data. Use only synthetic test conversations and fixtures.

## What Cloudflare does here

When explicitly selected with `LLM_PROVIDER=cloudflare`, the server sends a non-streaming request to Cloudflare Workers AI using `@cf/meta/llama-3.2-3b-instruct`. The current official model documentation shows the account-qualified REST endpoint, Bearer authentication, a `messages` request, `max_tokens`, and a synchronous `result.response` output:

- [Cloudflare Workers AI REST API](https://developers.cloudflare.com/workers-ai/get-started/rest-api/)
- [Cloudflare Llama 3.2 3B Instruct model page](https://developers.cloudflare.com/workers-ai/models/llama-3.2-3b-instruct/)

The adapter does not assume streaming, tool calling, or strict structured output. The prompt tells the model to provide unverified educational information only and to direct professional-judgement questions to a licensed pharmacist. That prompt is not a clinical safety control; deterministic routing remains before inference, and output is not treated as verified guidance.

## Provider modes and environment variables

The default is mock mode. `LLM_PROVIDER=mock` makes no external request and returns visibly simulated text. To select hosted inference, set `LLM_PROVIDER=cloudflare`, provide `CLOUDFLARE_ACCOUNT_ID` and `CLOUDFLARE_API_TOKEN` on the server, and restart the application. A configured live-provider failure returns a safe error; it never silently falls back to mock output.

The supported variables are:

```dotenv
LLM_PROVIDER=mock
LLM_MODEL=@cf/meta/llama-3.2-3b-instruct
CLOUDFLARE_ACCOUNT_ID=
CLOUDFLARE_API_TOKEN=
LLM_TIMEOUT_SECONDS=20
LLM_MAX_OUTPUT_TOKENS=500
```

The prototype also accepts the earlier aliases `APP_MODE`, `CLOUDFLARE_MODEL`, and `PROVIDER_TIMEOUT_SECONDS` to avoid breaking existing local setups. Never commit `.env`, real keys, or provider responses containing sensitive content. Credentials are read only by the backend and are never returned to the browser.

## Ubuntu/WSL setup

```bash
cd /home/ubuntu/pharmaplan
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
cp .env.example .env
pytest -q
uvicorn backend.main:app --host 0.0.0.0 --port 3000
```

Open `http://localhost:3000/` for the product overview or `http://localhost:3000/prototype` for the chat. For mock mode, leave `LLM_PROVIDER=mock`. For a real Cloudflare request, edit `.env` with protected credentials, set `LLM_PROVIDER=cloudflare`, and restart Uvicorn. The automated suite uses mocked HTTP responses and does not require credentials.

## Windows PowerShell setup

These commands assume a native Windows checkout:

```powershell
cd C:\path\to\pharmaplan
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Copy-Item .env.example .env
pytest -q
uvicorn backend.main:app --host 127.0.0.1 --port 3000
```

To select Cloudflare for the current PowerShell session without putting secrets in frontend code:

```powershell
$env:LLM_PROVIDER = "cloudflare"
$env:CLOUDFLARE_ACCOUNT_ID = "your-account-id"
$env:CLOUDFLARE_API_TOKEN = "your-server-side-token"
uvicorn backend.main:app --host 127.0.0.1 --port 3000
```

## Estimated inference cost

Cloudflare's model page currently lists `$0.0509` per million input tokens and `$0.335` per million output tokens. Using an engineering estimate of 2,000 input tokens and 500 output tokens per conversation, the estimated model inference cost is about `$0.0002693` per conversation, `$0.02693` for 100 conversations, `$0.13465` for 500, and `$0.26930` for 1,000. These are estimates, not quotes. They exclude plan charges, taxes, retries, longer conversation history, storage, gateways, prompt changes, and future price changes.

## Files delivered through Milestone 3B

- `backend/config.py` reads the requested `LLM_*` settings, keeps the safe mock default, and supports the previous environment aliases.
- `backend/providers/cloudflare.py` sends the documented non-streaming `messages` request, applies `max_tokens` and a timeout, parses `result.response` defensively, and classifies credential, model, rate-limit, timeout, server, and malformed-response failures without exposing provider details.
- `tests/test_milestone2b.py` uses mocked HTTP clients and responses to cover request construction, Bearer authentication, successful parsing, empty and malformed payloads, missing credentials, HTTP failures, timeout behavior, safety-before-provider routing, API compatibility, and frontend secret boundaries.
- `.env.example` documents safe mock mode, live-mode variables, and compatibility aliases using placeholders only.
- `README.md` documents provider behavior, setup, costs, file responsibilities, and limitations.
- `backend/knowledge/` contains the registry, approval checklist, structured-page processor, provenance-rich chunk models, citations, in-memory retrieval index, conflict assessment, and empty-by-default service.
- `backend/providers/base.py`, `backend/providers/mock.py`, `backend/providers/cloudflare.py`, and `backend/main.py` require and pass approved evidence before any provider call; the existing response shape and safety checks remain intact.
- `tests/helpers.py` and `tests/test_milestone3b.py` contain synthetic-only fixtures and coverage for governance, ingestion, provenance, retrieval, conflict detection, abstention, and provider gating.
- `MILESTONE3B_PLAN.md` documents the approved structure, governance decisions, and non-goals.
- `TODO.md` records the Milestone 2B and Milestone 3B acceptance outcomes.

No local model weights, Ollama, vLLM, SGLang, database, vector store, arbitrary web crawler, real clinical content, inventory lookup, authentication, pharmacist dashboard, or later Milestone 3 work was added.

## Verification and limitations

Run `pytest -q` from the project root. Passing tests establish mocked integration behavior only. They do not establish clinical safety, legal compliance, medication correctness, provider availability, or production readiness. A real Cloudflare request is not claimed unless valid credentials are supplied and a separate live smoke test succeeds; the current automated suite does not make that request.

The deterministic keyword policy is intentionally incomplete and is not a clinical safety system. Emergency messages are routed before provider construction and receive general emergency direction without invented local emergency or poison-control numbers. The knowledge layer now provides a governed skeleton, but it contains no production documents. Missing, weak, or conflicting evidence produces abstention, and the model is not called without a sufficient evidence bundle. Pharmacist-reviewed evaluation, approved source acquisition, source versioning, privacy review, and operational controls remain future work.

## Milestone 3B knowledge-base boundary

The new knowledge package is deliberately storage-independent and in memory. `DocumentRegistry` records source identity, publisher, version, publication and verification dates, source location, licensing state, reviewer, and approval status. Approval requires authenticity, publisher, relevance, currency, licensing, and content-quality checks; records marked as clinical also require pharmacist approval.

`ApprovedDocumentIngestor` accepts only a structured `DocumentPackage` whose exact document version is approved in the registry. It does not download URLs or scrape the web. `DocumentProcessor` validates page and section structure and creates chunks that retain document ID, title, publisher, version, section heading, page number, source references, content hashes, and citations.

`InMemoryKnowledgeIndex` performs a simple deterministic lexical match for this infrastructure milestone. It applies a relevance threshold and returns sufficient, insufficient, or conflicting evidence. The application starts with an empty index. When evidence is missing or conflicting, `/api/chat` keeps its existing response fields but returns a safe `blocked` response with `category=knowledge_abstention`; no provider is constructed. When synthetic approved evidence is injected in tests, the provider receives the question, safety instructions, evidence text, and citation metadata.

Before future clinical ingestion can begin, the project still needs an approved source list, licensing decisions, a durable registry/index, extraction quality controls for real document formats, pharmacist governance, version and currency policy, conflict-resolution rules, privacy review, and a retrieval evaluation set. This milestone does not claim clinical validation or medication accuracy.

## Milestone 3D source registry and governance

Milestone 3D adds a storage-independent `SourceRegistry` for source metadata only. A `SourceRecord` identifies the publisher, official URL, source category, jurisdiction, applicable market, authority scope and limitations, primary/supplementary status, verification and review dates, reviewer, approval state, notes, and separate permission statuses for public access, linking, downloading, extraction, internal indexing, and reproduction. Public accessibility is never treated as permission to ingest content.

The source workflow is explicit: `draft` → `pending_review` → `approved_for_linking` → `approved_for_indexing`, with `restricted`, `rejected`, and `expired` states. Linking approval does not grant indexing approval. Indexing requires confirmed extraction permission, confirmed internal-indexing permission, a current verification window, and an active `approved_for_indexing` state. Missing dates, due reviews, unverified permissions, withdrawn/rejected/expired records, and conflicting metadata are surfaced as governance issues.

`SourceRouter` maps question categories to source categories such as Nigerian regulatory status → NAFDAC, Nigerian pharmacy practice → PCN, national policy → FMoHSW, international public-health recommendations → WHO, and exact product information → a verified product-specific or manufacturer source. Routing only identifies candidate sources; it does not authorize clinical answers or bypass evidence gating.

Source-linked `DocumentMetadata` records must reference a source that is explicitly approved for internal indexing. The document processor and in-memory retrieval index check that approval again, so a source that later becomes restricted or expired is excluded from ingestion and retrieval. Existing provenance now carries the optional `source_id` through citations and knowledge chunks. Documents without a source ID remain compatible with the Milestone 3B synthetic fixtures; no real sources or medication documents are seeded at runtime.

The implementation remains in memory and synthetic-only. It does not scrape websites, download clinical documents, introduce patient information, claim licensing permission, add a database, or activate clinical medication responses. See `MILESTONE3D_IMPLEMENTATION_REPORT.md` for the implementation record and limitations.

## Milestone 3E evidence reliability boundary

Milestone 3E adds runtime validation rather than relying on provider callers to follow a convention. `EvidenceValidator` rejects empty, insufficient, conflicting, stale, incomplete, or provenance-inconsistent evidence before either the mock or Cloudflare provider can produce output. Source-linked evidence must also be backed by an active source record approved for internal indexing. Validation failures become safe knowledge abstentions at the API boundary and do not expose internal details.

`CitationValidator` checks that every citation corresponds to a passage in the exact retrieved evidence bundle, including publisher, title, version, publication date, page, section, source location, and optional document/source identity. A formatted or model-generated citation is not treated as verified unless it matches retrieved evidence. `StructuredAnswer` keeps conversational wording separate from factual claims, and each factual claim must name its supporting passage IDs and citations. A conservative lexical claim-to-passage check rejects genuine-but-irrelevant citations; this is not semantic or clinical verification.

Retrieval now requires a minimum amount of query-term coverage, supports optional jurisdiction filtering, gives a bounded preference to primary sources, and uses an explicit `conflict_group` when available. Existing synthetic `claim_key` fixtures remain supported. Normal `ApprovedDocumentIngestor` construction is clinical-governed by default; synthetic fixtures use the explicit `test_synthetic` processor mode only inside tests. No test-only ingestion mode is exposed through application configuration or routes.

The `GovernedProvider` boundary validates evidence before every normal provider call, validates structured provider results after generation, and rechecks source governance before delivery. Invalid claims, citations, evidence, or source state become safe knowledge abstentions at `/api/chat`; the frontend does not receive internal validation details. The implementation and limitations are recorded in `MILESTONE3E_IMPLEMENTATION_REPORT.md` and `MILESTONE3E1_IMPLEMENTATION_REPORT.md`. The full automated suite is synthetic and does not establish clinical safety, medication accuracy, legal compliance, semantic truth, or production readiness.

## Container deployment

The existing `Dockerfile` installs `requirements.txt`, copies the application, starts Uvicorn on `0.0.0.0`, honors the platform `PORT` value with `3000` as the local default, and exposes `/health` as the readiness path. Provider credentials must be supplied as protected runtime environment values rather than baked into the image.

## Milestone 3F controlled-source gate

Milestone 3F assessed the NAFDAC Greenbook as the first Nigerian primary-source candidate, but did not ingest it. The official Greenbook and NAFDAC Drugs pages establish public access and regulatory relevance, not permission for automated extraction, internal indexing, or reproduction in AI answers. A linked product-information PDF also contains a third-party copyright notice. Because item-specific extraction and indexing permission could not be established, the project stopped before source registration, download, extraction, hashing, indexing, or retrieval. See `MILESTONE3F_IMPLEMENTATION_REPORT.md` for the factual assessment and references.

The runtime knowledge base therefore remains empty by default and the project remains synthetic-only for indexed content. Written permission or an explicit licence covering the exact source and intended use, followed by pharmacist and legal/licensing review, is required before controlled ingestion can begin. This milestone does not claim clinical accuracy, legal compliance, regulatory compliance, pharmacist validation, or production readiness.

## Milestone 3F.1 openFDA verification

Milestone 3F.1 researched openFDA as a possible first medication-specific source without modifying application code or registering a source. The official openFDA terms provide a CC0 basis for material not otherwise noted, but also exclude or qualify privately supplied and third-party material. The assessed acetaminophen OTC SPL record is manufacturer-submitted U.S. labeling, not Nigerian-approved product information; its record-level rights and permission for internal AI indexing and user-facing reproduction remain unresolved. It is therefore suitable for future linking and metadata review only, not approved for indexing. See `MILESTONE3F1_OPENFDA_SOURCE_VERIFICATION_REPORT.md`.
