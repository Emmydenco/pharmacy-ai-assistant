# PROJECT HANDOVER
## Pharmacy Patient Assistant

Last updated: 9 November 2026

---

## 1. Project Purpose

The Pharmacy Patient Assistant is a safety-focused conversational AI project intended to support routine medication-information enquiries in community pharmacy settings.

The long-term objective is to provide accessible, understandable, evidence-grounded medication information while recognizing questions that require pharmacist or clinician involvement.

The application must not replace pharmacists or clinicians.

The initial target context is Nigerian community pharmacy practice.

---

## 2. Project Vision

The proposed system will eventually support:

- General medication information.
- Common side-effect explanations.
- Medication-label explanations.
- Source-grounded medication information.
- Deterministic OTC inventory lookup.
- Appropriate pharmacist escalation.

Potential future features include:
- WhatsApp integration.
- Refill reminders.
- Real-time pharmacy inventory.
- General wellness information.

These future features are not necessarily implemented.

---

## 3. Safety Requirements

The assistant must not:

- Diagnose illnesses.
- Prescribe medications.
- Recommend starting or stopping prescription medicines.
- Recommend changing doses.
- Recommend therapeutic substitutions.
- Create individualized treatment plans.
- Invent clinical facts or citations.
- Present unsupported model-generated claims as verified.

High-risk or uncertain questions must be escalated appropriately.

Emergencies must receive appropriate emergency guidance rather than ordinary model-generated responses.

Development and testing must use synthetic conversations only.

---

## 4. Existing Technology

### Backend
- Python.
- FastAPI.
- Provider abstraction.
- Deterministic safety screening.
- Knowledge-base governance modules.

### Frontend
- HTML.
- CSS.
- JavaScript.

### AI inference
- Cloudflare Workers AI.
- Model: `@cf/meta/llama-3.2-3b-instruct`.
- Mock provider for testing.

### Testing
- pytest.
- Automated unit and integration tests.

No local LLM inference is intended.

---

## 5. Completed Milestones

### Milestone 1 — Initial Application

Implemented:
- Responsive frontend.
- FastAPI backend.
- Basic chat endpoint.
- Deterministic safety screening.
- Mock provider.

### Milestone 2A — Hosted Provider Research

Compared hosted inference providers.

Cloudflare Workers AI was conditionally selected.

### Milestone 2B — Cloudflare Integration

Implemented:
- Cloudflare provider adapter.
- Environment-based configuration.
- Server-side credentials.
- Error handling.
- Mock provider preservation.

### Milestone 2C — Provider Audit

Reviewed:
- Authentication.
- Endpoint configuration.
- Error handling.
- Secret management.
- Logging.
- Safety screening.

### Cloudflare Connectivity Verification

A controlled live inference test succeeded.

The backend returned HTTP 200, and a meaningful response was received from Cloudflare.

This verified hosted inference connectivity, not clinical accuracy.

### Milestone 3A — Knowledge-Base Architecture

Designed:
- Approved-source ingestion.
- Provenance.
- Evidence retrieval.
- Citation handling.
- Abstention.
- Pharmacist oversight.

### Milestone 3B — Knowledge-Base Skeleton

Implemented:
- Knowledge models.
- Source registry.
- Processing pipeline.
- Retrieval service.
- Evidence bundles.
- Empty-by-default runtime knowledge service.

### Milestone 3C — Source Selection Research

Evaluated Nigerian and international medication-information sources.

Key conclusion: source permissions must be verified independently of public accessibility.

### Milestone 3D — Source Governance

Implemented:
- Source records.
- Source approval workflow.
- Permission-aware controls.
- Question-based source routing.

### Milestone 3E — Retrieval and Citation Reliability

Introduced evidence and citation validation.

The audit identified weaknesses in provider enforcement and generated-answer validation.

### Milestone 3E.1 — Corrective Hardening

Implemented:
- Governed provider wrapper.
- Structured answers and claims.
- Claim-to-evidence checks.
- Post-generation validation.
- Final source governance revalidation.
- Explicit synthetic-test pathway.
- Clinical source ID requirements.

Important limitation: lexical claim matching does not establish clinical truth.

### Milestone 3F — NAFDAC Source Permission Assessment

NAFDAC Greenbook was evaluated.

No approval for systematic ingestion was established.

### Milestone 3F.1 — openFDA Permission Assessment

openFDA was evaluated.

General metadata use appeared more feasible than unrestricted reuse of manufacturer-submitted label text.

No clinical label ingestion was approved.

### Milestone 3F.2 — Medication Source Discovery

Compared:
- RxNorm/RxNav.
- DailyMed.
- openFDA.
- WHO.
- EMA.
- MedlinePlus.
- NHS dm+d.
- NAFDAC Greenbook.

No primary clinical medication-information corpus was approved.

### Milestone 3F.3 — NHS dm+d Permission Research

Evaluated NHSBSA/TRUD item 24, release 11.0.0, Week 45.

The Open Government Licence was identified, but exact archive and field-level coverage remained unresolved.

The source was considered a terminology/product-identity candidate, not clinical evidence.

### Milestone 3G — Controlled NHS dm+d Ingestion Assessment

The milestone stopped before retrieval and ingestion.

The audit identified missing architecture controls for:
- Release-specific provenance.
- Archive checksums.
- Licence and attribution tracking.
- File-level approval.
- Field-level approval.
- Source capability enforcement.
- Release-scoped rollback.

No real NHS data was retrieved or ingested.

---

## 6. Current Project Status

The project has:
- A working frontend/backend foundation.
- A functioning hosted inference integration.
- Deterministic safety screening.
- A governed knowledge-base architecture.
- Source registry and approval controls.
- Evidence and citation validation.
- Automated tests.

However:

**The runtime knowledge base remains empty of approved real clinical medication content.**

The project is not clinically validated and is not ready for real patient use.

---

## 7. Immediate Next Milestone

### Milestone 3G.1
Knowledge Governance Hardening for Release-Scoped Provenance and Source Capabilities.

Objectives:

1. Introduce typed source capabilities.
2. Enforce source capabilities in retrieval.
3. Enforce source capabilities in evidence validation.
4. Add release-specific provenance.
5. Track licence, attribution, archive filename and SHA-256.
6. Introduce file-level and field-level approval.
7. Preserve provenance throughout the evidence pipeline.
8. Implement release-scoped rollback.
9. Add synthetic negative tests.

Restrictions:

- No real NHS dataset retrieval.
- No TRUD account or API access.
- No external medication data.
- No live Cloudflare inference.
- No real patient data.

The milestone must preserve all existing safety and security controls.

---

## 8. Important Outstanding Work

### Knowledge governance
- Complete 3G.1.
- Audit the implementation.
- Inspect the exact NHS dm+d release.
- Only then consider controlled terminology ingestion.

### Clinical medication information
A separate, appropriately licensed clinical medication-information source is still required.

Terminology databases cannot replace clinical medication references.

### Nigerian regulatory information
A reliable, permission-cleared Nigerian regulatory source is still required.

Foreign datasets cannot establish NAFDAC registration or Nigerian availability.

### Clinical validation
Future work must include:
- Qualified pharmacist review.
- Evidence-quality evaluation.
- Clinical safety evaluation.
- Appropriate legal and privacy review.

### Other future development
- Deterministic inventory lookup.
- Pharmacist escalation workflow.
- Persistent storage where justified.
- Additional user-interface improvements.
- Evaluation dataset of 50–100 synthetic questions.

---

## 9. Repository Structure

Important directories:

- `backend/` — FastAPI application.
- `backend/knowledge/` — knowledge and source governance.
- `backend/providers/` — AI provider integrations.
- `tests/` — automated tests.
- `public/` — frontend assets.

Important files:

- `backend/main.py`
- `backend/config.py`
- `backend/policy.py`
- `backend/answers.py`
- `backend/schemas.py`
- `backend/knowledge/models.py`
- `backend/knowledge/source_registry.py`
- `backend/knowledge/registry.py`
- `backend/knowledge/processing.py`
- `backend/knowledge/retrieval.py`
- `backend/knowledge/validation.py`
- `backend/knowledge/service.py`
- `backend/providers/base.py`
- `backend/providers/cloudflare.py`
- `backend/providers/mock.py`

Read the actual source code before assuming that this handover fully describes current implementation details.

---

## 10. Git and Migration Status

The project was exported from Manus as a ZIP.

The original Manus Git history was not included in the ZIP.

A new local Git repository was initialized.

Initial import commit:

`8163889`

Commit message:

`Initial checkpoint: import Manus pharmacy assistant project`

The repository was pushed to a private GitHub repository.

This is a new Git history, not a restoration of the original Manus commit history.

Verify the current Git branch, HEAD, remote and working-tree status before making changes.

---

## 11. Working Method

The preferred workflow is:

1. ChatGPT helps define milestones and architecture.
2. OpenCode inspects and implements authorized tasks.
3. OpenCode runs tests and reports changes.
4. ChatGPT reviews the implementation and audit findings.
5. The user approves the next milestone.

Do not proceed automatically from one milestone to another.

The user wants to understand the architecture and implementation rather than blindly accept generated code.

Explain important technical decisions in understandable language.

---

## 12. Immediate Instruction to OpenCode

Begin with a READ-ONLY inspection of the repository.

Read:
- `AGENTS.md`
- `PROJECT_HANDOVER.md`
- `README.md`
- `TODO.md`
- Relevant backend modules.
- Existing tests.
- Milestone 3G report.

Then report:

1. Current Git branch and HEAD.
2. Repository structure.
3. Existing architecture.
4. Current test results.
5. Differences between the handover and actual code.
6. Whether the repository is ready for Milestone 3G.1.
7. Any risks or inconsistencies discovered.

Do not modify files.

Do not access external sources.

Do not retrieve medication datasets.

Do not use credentials.

Do not perform live Cloudflare inference.

Wait for explicit authorization before implementation.