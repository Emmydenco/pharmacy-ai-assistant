

## Milestone 3G.1 — Knowledge governance hardening for release-scoped provenance and source capabilities

- [ ] **Typed source capabilities and independent evidence enforcement**
  - Support `terminology_product_identity`, `clinical_medication_evidence`, `regulatory_product_status`, `professional_practice_guidance`, and `public_health_policy` as explicit machine-enforceable capabilities.
  - Each source must declare its evidence capabilities without treating a capability declaration as universal authority; existing authority, jurisdiction, permissions, and approval controls remain active.
  - Retrieval and evidence validation must both fail closed when the required capability is absent.
  - Terminology-only evidence must not satisfy clinical medication evidence or Nigerian regulatory questions.

- [ ] **Structured release provenance and scoped approval**
  - Represent publisher, dataset name, source ID, source type/capability, jurisdiction, licence name and URL, required attribution, TRUD item, release number/week/date, archive filename, archive SHA-256, acquisition and verification dates, source-status snapshot, manifest/file identifiers, approved file identifiers, and approved field identifiers as typed data.
  - Scope approval to the exact source, dataset, release, archive/checksum, file, field, and permitted capability/use.
  - Represent approved, rejected, and unresolved files and fields, and reject content outside the approved scope.

- [ ] **Provenance propagation and release-scoped rollback**
  - Preserve exact source/release/checksum/file/field/licence/jurisdiction/verification provenance from source record through document/package, parsed record, chunk, citation, evidence bundle, and answer claim where applicable.
  - Remove one exact source/release identity without deleting synthetic fixtures, unrelated sources, other releases, or unrelated chunks.
  - Verify no selected records, orphaned citations, or orphaned evidence references remain and that rollback is deterministic and repeatable.

- [ ] **Synthetic-only governance fixtures and regression coverage**
  - Use only synthetic release metadata and records; do not retrieve, authenticate to, download, or ingest NHS dm+d or any external medication content.
  - Include synthetic TRUD item/release/week/date, archive filename, deterministic SHA-256, manifest, multiple files, approved/unapproved fields, terminology/product-identity records, and at least one unresolved file or field.
  - Add negative tests for missing provenance, unapproved fields/files, absent terminology capability for clinical/regulatory questions, source status changes, and release-scoped rollback isolation.
  - Preserve deterministic safety screening, abstention, governed provider wrapper, structured answer/claim validation, citation validation, source revalidation, Cloudflare/mock behavior, secret handling, sanitized logging, synthetic pathways, and no local inference.

- [ ] **Milestone report and verification**
  - Create `MILESTONE3G1_GOVERNANCE_HARDENING_REPORT.md` containing modified files, data-model changes, capability model, release provenance, file/field approval, retrieval/evidence enforcement, rollback, synthetic dataset design, negative tests, full test results, compile and diff checks, and explicit confirmation that no real external data, credentials, or Cloudflare inference were used.
