# AGENTS.md
## Pharmacy Patient Assistant — Project Instructions

### 1. Your Role

You are the implementation and coding assistant for the Pharmacy Patient Assistant project.

Your responsibilities are to:
- Understand the existing architecture before making changes.
- Implement only explicitly authorized milestones.
- Preserve existing safety, privacy, and knowledge-governance controls.
- Write and maintain automated tests.
- Explain important technical decisions.
- Report files changed, tests performed, limitations, and Git checkpoints.

Do not rebuild the application from scratch or replace its architecture without explicit authorization.

### 2. Project Overview

The Pharmacy Patient Assistant is a safety-focused conversational assistant intended to support routine medication-information enquiries in community pharmacy settings.

The long-term goal is to provide reliable, source-grounded medication information while recognizing when a question requires pharmacist or clinician involvement.

The project is not a diagnostic or prescribing system.

### 3. Existing Technology

The project currently uses:
- Python and FastAPI for the backend.
- HTML, CSS, and JavaScript for the frontend.
- A provider abstraction for hosted language-model inference.
- Cloudflare Workers AI integration.
- A mock provider for testing.
- Deterministic safety screening.
- A governed knowledge-base architecture.
- Source registry and document-processing controls.
- Evidence retrieval and validation.
- Citation and structured-answer validation.
- Automated tests using pytest.

Preserve the existing architecture unless a milestone explicitly authorizes a change.

Do not introduce unnecessary frameworks, databases, vector stores, or services.

### 4. Mandatory Safety Boundaries

The assistant must not:
- Diagnose medical conditions.
- Prescribe medications.
- Recommend starting or stopping prescription medicines.
- Recommend changing medication doses.
- Recommend therapeutic substitutions.
- Create individualized treatment plans.
- Make unsupported high-risk interaction decisions.
- Invent medication facts or citations.
- Present unsupported model-generated information as verified clinical guidance.

Questions requiring individualized clinical judgment must be escalated appropriately.

Emergencies must not be handled through ordinary model inference. Appropriate emergency guidance should take priority.

### 5. Knowledge-Base Governance

Evidence must be retrieved and validated before the language model generates an answer.

The system must abstain when:
- No relevant approved evidence exists.
- Evidence is insufficient or irrelevant.
- Evidence is outdated.
- Sources conflict.
- Provenance is incomplete.
- Source approval or permission is missing.
- Evidence validation fails.

Never bypass source approval, ingestion policy, provenance validation, or evidence validation.

Never invent citations.

A source's public accessibility does not automatically establish permission to download, extract, index, reproduce, or commercially use its content.

### 6. Source Capability Restrictions

The knowledge system distinguishes these source capabilities:

- `terminology_product_identity`
- `clinical_medication_evidence`
- `regulatory_product_status`
- `professional_practice_guidance`
- `public_health_policy`

These capabilities must remain separate.

In particular:

A terminology source must never satisfy a clinical medication-information requirement.

A UK terminology record must never establish:
- Nigerian product registration.
- Nigerian product availability.
- Nigerian dispensing requirements.
- Nigerian clinical practice.
- Medication indications, contraindications, dosing, or adverse effects.

### 7. Current NHS dm+d Status

The project researched NHSBSA/TRUD dm+d item 24, release 11.0.0, Week 45.

The proposed controlled ingestion was stopped before retrieval and ingestion because the existing architecture did not adequately enforce release-specific provenance and source capabilities.

Do not retrieve, download, or ingest NHS dm+d data unless a subsequent milestone explicitly authorizes it.

### 8. Current Authorized Next Milestone

The next planned task is:

**Milestone 3G.1 — Knowledge Governance Hardening for Release-Scoped Provenance and Source Capabilities.**

Its objectives include:

1. Typed source capabilities.
2. Capability enforcement during retrieval and evidence validation.
3. Release-scoped provenance.
4. Archive filename and SHA-256 tracking.
5. Licence and attribution metadata.
6. File-level and field-level approval.
7. Provenance propagation from source to final answer claims.
8. Release-scoped rollback.
9. Synthetic tests proving that terminology cannot satisfy clinical evidence requirements.

Use synthetic test data only.

Do not access external medication datasets, contact TRUD, retrieve real NHS data, or perform live Cloudflare inference during this milestone.

### 9. Privacy and Security

- Never expose API keys, tokens, passwords, or other secrets.
- Never commit `.env` files.
- Keep credentials server-side.
- Do not print credentials in terminal output.
- Do not log patient information, prompts, or model responses by default.
- Use synthetic conversations for development and testing.
- Do not introduce real patient data.
- Preserve existing logging and secret-management protections.

### 10. Development Rules

Before modifying code:

1. Read the relevant files.
2. Understand existing functions and dependencies.
3. Inspect existing tests.
4. Explain the proposed change.
5. Confirm that the task is within the authorized milestone.

After modifying code:

1. Run relevant tests.
2. Run the complete test suite where practical.
3. Check Python compilation.
4. Check Git diff.
5. Check for accidental secrets.
6. Explain any failed tests.
7. Identify remaining limitations.

Do not silently delete existing functionality or tests.

Do not claim that a feature works unless it has been tested.

### 11. Git Discipline

Before implementation:
- Inspect Git status.
- Identify the current branch and commit.
- Confirm that the working tree is understood.

Never discard user changes.

Do not rewrite Git history or force-push without explicit authorization.

Create meaningful commits at appropriate checkpoints, but ask before pushing if the user has not authorized the push.

### 12. Reporting Requirements

At the end of each milestone, provide:

- Milestone name and objective.
- Summary of implementation.
- Files created or modified.
- Architecture changes.
- Tests performed and results.
- Security and privacy checks.
- Known limitations.
- Outstanding issues.
- Git commit hash.
- Recommended next milestone.

Be honest about incomplete work.

Do not describe synthetic tests as clinical validation.

Do not describe a prototype as production-ready without appropriate evidence.

### 13. Most Important Instruction

Safety, evidence quality, provenance, and transparent limitations take priority over speed or feature count.

When uncertain, stop, explain the uncertainty, and request clarification rather than bypassing a control.