# Milestone 1 implementation plan

## Goal

Add a small, understandable, testable chatbot foundation to the existing feasibility microsite. The existing architecture brief remains at `/`. The new prototype lives at `/prototype` and is intentionally separate from the research page.

## Architecture

```text
Browser: prototype.html + prototype.css + prototype.js
                    |
                    | POST /api/chat
                    v
FastAPI: backend/main.py
  - validates ChatRequest
  - applies backend/policy.py before any model call
  - selects mock or Cloudflare provider from environment
  - returns a structured ChatResponse
                    |
        +-----------+-----------+
        |                       |
  MockProvider            CloudflareProvider
  deterministic            documented REST API
  no network               credentials server-side
```

The backend also serves the existing landing page and static assets. Chat messages are not persisted and are not printed in application logs.

## Selected tools

- Python 3 with FastAPI and Uvicorn for the API and lightweight local server.
- Pydantic models through FastAPI for request and response validation.
- `httpx` for the hosted provider call and timeout handling.
- `pytest` plus FastAPI's test client for automated tests.
- Plain HTML, CSS, and JavaScript for the prototype UI to keep the frontend lightweight and easy to understand.

## Provider design

`APP_MODE=mock` is the safe default. Mock responses are predetermined, labelled simulated, and contain no citations. `APP_MODE=cloudflare` uses the documented Cloudflare REST endpoint with a bearer token, account ID, configurable model name, and timeout. Missing credentials and provider failures return an error state; they never fall back to fabricated medication content.

## Safety scope

The policy layer runs before a provider call. It routes obvious emergency language to immediate emergency guidance, sends diagnosis/prescription-change/patient-specific-treatment requests to a pharmacist, and blocks clearly out-of-scope requests. These keyword and phrase rules are intentionally small and documented as incomplete. They are not a clinical safety system.

## Explicitly deferred

No database, RAG, embeddings, vector store, Llama Stack/OGX, Llama Guard, inventory processing, authentication, pharmacist dashboard, analytics, persistent chat history, or real patient data is added in this milestone.

## Resource expectations

The local setup uses a small Python environment and no model weights. Mock mode makes no network calls. Hosted mode requires an external account and API credentials but keeps them on the server. No paid service is enabled by this implementation.
