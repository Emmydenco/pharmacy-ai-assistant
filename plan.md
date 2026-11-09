# Milestone 3G.1 Implementation Plan

## Objective

Harden the existing governed knowledge pipeline using synthetic metadata and records only. Do not access TRUD, request credentials, retrieve NHS dm+d, add real medication content, or make live provider calls.

## Implementation approach

1. Add typed source capabilities and capability-aware evidence requirements while preserving existing source approval, jurisdiction, permissions, freshness, and citation checks.
2. Add a structured release-provenance object containing the exact release, checksum, licence, manifest, approved files, approved fields, and source-status snapshot.
3. Propagate that object from source/document/package through parsed records, chunks, citations, evidence passages, and structured answer claims where applicable.
4. Add file-level and field-level approval records with fail-closed ingestion checks for rejected or unresolved files/fields.
5. Add release-scoped index rollback that removes only chunks belonging to one exact release and verifies citation/reference cleanup.
6. Create synthetic release fixtures that resemble the future TRUD structure without copying NHS dm+d or using real clinical medication content.
7. Add negative and regression tests for capability separation, incomplete provenance, unapproved fields/files, source status, rollback isolation, and existing Milestone 3E.1 behavior.

## Project structure

- `backend/knowledge/models.py`: typed capabilities, release provenance, scope approvals, and propagated provenance fields.
- `backend/knowledge/source_registry.py`: source capability and release approval checks.
- `backend/knowledge/registry.py`: document/package registration against exact release scope.
- `backend/knowledge/processing.py`: fail-closed file/field validation and provenance propagation.
- `backend/knowledge/retrieval.py`: capability-aware retrieval and release-scoped rollback.
- `backend/knowledge/validation.py`: independent evidence-capability and provenance validation.
- `backend/knowledge/__init__.py`: public exports.
- `tests/test_milestone3g1.py`: synthetic fixtures, negative tests, and rollback tests.
- `MILESTONE3G1_GOVERNANCE_HARDENING_REPORT.md`: audit and verification report.

## Compatibility decisions

Existing synthetic fixtures remain valid through explicit defaults for legacy, source-less test data. New release-scoped records must provide complete structured provenance and exact approved scope. Existing providers, API contracts, deterministic safety checks, and secret handling remain unchanged.

## Validation

Run the full pytest suite, compile all backend/tests modules, run `git diff --check`, and inspect the final diff. No external request or credential operation is permitted.
