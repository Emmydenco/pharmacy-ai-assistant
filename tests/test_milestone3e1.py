import asyncio
from dataclasses import replace
from datetime import date, timedelta
from typing import cast

import pytest
from fastapi.testclient import TestClient

import backend.main as main
from backend.answers import AnswerClaim, StructuredAnswer
from backend.knowledge.models import (
    ApprovalChecklist,
    DocumentMetadata,
    DocumentPage,
    DocumentPackage,
    DocumentSection,
    SourcePermissions,
    SourceRecord,
    PermissionStatus,
)
from backend.knowledge.processing import (
    ApprovedDocumentIngestor,
    DocumentProcessor,
    IngestionRejectedError,
)
from backend.knowledge.registry import DocumentRegistry, RegistryError
from backend.knowledge.retrieval import InMemoryKnowledgeIndex
from backend.knowledge.source_registry import SourceRegistry
from backend.knowledge.validation import (
    AnswerValidationError,
    CitationValidationError,
    EvidenceValidationError,
    CitationValidator,
    validate_structured_answer,
)
from backend.providers.base import (
    ProviderResult,
    ProviderResultValidationError,
    ensure_governed_provider,
)
from tests.helpers import synthetic_evidence, synthetic_service


class NonCompliantProvider:
    def __init__(self, result):
        self.result = result
        self.called = False

    async def generate(self, message, history, evidence):
        del message, history, evidence
        self.called = True
        return self.result


def claim_for(evidence, text: str, *, claim_id: str = "claim-1", passage_ids=None):
    passage = evidence.passages[0]
    return AnswerClaim(
        claim_id=claim_id,
        text=text,
        evidence_passage_ids=tuple(passage_ids or (passage.chunk.chunk_id,)),
        citations=(passage.citation,),
    )


def source_record(
    *,
    source_id: str = "synthetic-clinical-source",
    extraction: PermissionStatus = "confirmed_permitted",
    indexing: PermissionStatus = "confirmed_permitted",
) -> SourceRecord:
    return SourceRecord(
        source_id=source_id,
        source_name="Synthetic Clinical Source",
        publisher="Synthetic Clinical Publisher",
        official_url="synthetic://clinical-source",
        source_category="synthetic_clinical_fixture",
        jurisdiction="Nigeria",
        applicable_market="Nigeria",
        scope_classification="national",
        authoritative_for=("synthetic clinical facts",),
        authority_limitations=("Synthetic fixture only",),
        authority_level="primary",
        permissions=SourcePermissions(
            public_accessibility="confirmed_permitted",
            linking="confirmed_permitted",
            downloading="confirmed_permitted",
            extraction=extraction,
            internal_indexing=indexing,
            reproduction="confirmed_permitted",
        ),
        publication_date=date(2026, 1, 1),
        last_verification_date=date.today(),
        next_review_date=date.today() + timedelta(days=30),
    )


def approved_source_registry(source=None) -> SourceRegistry:
    registry = SourceRegistry()
    registry.register(source or source_record())
    source_id = (source or source_record()).source_id
    registry.submit_for_review(source_id)
    registry.approve_for_linking(source_id, reviewer="Synthetic Reviewer")
    registry.approve_for_indexing(source_id, reviewer="Synthetic Pharmacist")
    return registry


def source_linked_evidence():
    source_registry = approved_source_registry()
    document_registry = DocumentRegistry(source_registry=source_registry)
    metadata = DocumentMetadata(
        document_id="synthetic-clinical-document",
        title="Synthetic Clinical Document",
        publisher="Synthetic Clinical Publisher",
        publication_date=date(2026, 1, 1),
        version="1",
        source_location="synthetic://clinical-document",
        acquired_at=date.today(),
        licensing_status="test-only",
        clinical_content=True,
        source_id="synthetic-clinical-source",
    )
    document_registry.register(metadata)
    approved = document_registry.approve(
        metadata.document_id,
        metadata.version,
        ApprovalChecklist(
            authenticity_verified=True,
            publisher_verified=True,
            relevance_assessed=True,
            currency_assessed=True,
            licensing_reviewed=True,
            content_quality_reviewed=True,
            pharmacist_approved=True,
        ),
        reviewer="Synthetic Pharmacist",
    )
    package = DocumentPackage(
        metadata=approved,
        pages=(
            DocumentPage(
                page_number=1,
                sections=(
                    DocumentSection(
                        heading="Synthetic fact",
                        content="The synthetic label lists directions and storage information.",
                        source_reference="synthetic://clinical-document#fact",
                    ),
                ),
            ),
        ),
    )
    processed = ApprovedDocumentIngestor(document_registry).ingest(package)
    index = InMemoryKnowledgeIndex(document_registry, relevance_threshold=0.2)
    index.add(processed.chunks)
    return source_registry, document_registry, index.retrieve("directions storage information")


def test_boundary_rejects_invalid_evidence_before_noncompliant_provider_runs():
    provider = NonCompliantProvider(ProviderResult(text="unexpected", simulated=True))
    governed = ensure_governed_provider(provider, DocumentRegistry())
    invalid = replace(synthetic_evidence(), status="insufficient")

    with pytest.raises(EvidenceValidationError):
        asyncio.run(governed.generate("Question", [], invalid))
    assert provider.called is False


@pytest.mark.parametrize(
    "result",
    [
        object(),
        ProviderResult(text="", simulated=True),
        ProviderResult(text="answer", simulated=cast(bool, "yes")),
    ],
)
def test_boundary_rejects_malformed_provider_results(result):
    provider = NonCompliantProvider(result)
    governed = ensure_governed_provider(provider, DocumentRegistry())

    with pytest.raises(ProviderResultValidationError):
        asyncio.run(governed.generate("Question", [], synthetic_evidence()))


def test_boundary_normalizes_plain_provider_text_as_unverified_conversational_text():
    provider = NonCompliantProvider(ProviderResult(text="General wording only.", simulated=True))
    result = asyncio.run(
        ensure_governed_provider(provider, DocumentRegistry()).generate(
            "Question", [], synthetic_evidence()
        )
    )

    assert result.answer is not None
    assert result.answer.claims == ()
    assert result.text == "General wording only."


def test_supported_claim_requires_its_own_passage_and_citation():
    evidence = synthetic_evidence()
    answer = StructuredAnswer(
        conversational_text="The label includes general information.",
        claims=(
            claim_for(
                evidence,
                "A synthetic label example lists a product name, directions, warnings, and storage information.",
            ),
        ),
    )

    assert validate_structured_answer(answer, evidence) == answer


def test_irrelevant_or_unsupported_claim_fails_even_with_valid_citation():
    evidence = synthetic_evidence()
    answer = StructuredAnswer(
        conversational_text="Unsupported factual claim.",
        claims=(claim_for(evidence, "The label contains a contraindication dosage schedule."),),
    )

    with pytest.raises(AnswerValidationError, match="does not conservatively support"):
        validate_structured_answer(answer, evidence)


def test_claim_without_evidence_or_with_irrelevant_citation_fails_closed():
    evidence = synthetic_evidence()
    passage = evidence.passages[0]
    no_evidence = StructuredAnswer(
        conversational_text="Missing support.",
        claims=(
            AnswerClaim(
                claim_id="missing",
                text="A synthetic label lists directions.",
                evidence_passage_ids=(),
                citations=(passage.citation,),
            ),
        ),
    )
    with pytest.raises(AnswerValidationError, match="requires supporting evidence"):
        validate_structured_answer(no_evidence, evidence)

    with pytest.raises(CitationValidationError):
        CitationValidator().validate(
            [passage.citation, replace(passage.citation, page_number=999)],
            evidence,
        )


def test_multiple_claims_must_validate_against_their_specific_passages():
    evidence = synthetic_evidence()
    first = replace(
        evidence.passages[0],
        chunk=replace(
            evidence.passages[0].chunk,
            text="A synthetic label example lists directions and warnings.",
            content_hash="first-hash",
        ),
    )
    second = replace(
        first,
        chunk=replace(
            first.chunk,
            chunk_id="synthetic-label-fixture:second",
            section_heading="Second synthetic section",
                source_reference="synthetic://label-fixture#second",
                text="The synthetic package lists storage information.",
                content_hash="second-hash",
                claim_key="synthetic-storage-information",
                citation=replace(
                    first.chunk.citation,
                    section_heading="Second synthetic section",
                    source_location="synthetic://label-fixture#second",
                ),
            ),
        )
    multi = replace(evidence, passages=(first, second))
    answer = StructuredAnswer(
        conversational_text="Two separately supported synthetic statements.",
        claims=(
            claim_for(multi, "A synthetic label lists directions and warnings.", claim_id="one"),
            AnswerClaim(
                claim_id="two",
                text="A synthetic package lists storage information.",
                evidence_passage_ids=(second.chunk.chunk_id,),
                citations=(second.citation,),
            ),
        ),
    )
    assert validate_structured_answer(answer, multi) == answer

    ambiguous = replace(
        answer,
        claims=(
            AnswerClaim(
                claim_id="ambiguous",
                text="A synthetic label lists directions storage information.",
                evidence_passage_ids=(first.chunk.chunk_id, second.chunk.chunk_id),
                citations=(first.citation, second.citation),
            ),
        ),
    )
    with pytest.raises(AnswerValidationError, match="does not conservatively support"):
        validate_structured_answer(ambiguous, multi)


def test_conflicting_evidence_is_rejected_before_claim_validation():
    evidence = synthetic_evidence()
    first = evidence.passages[0]
    conflict = replace(
        first,
        chunk=replace(
            first.chunk,
            chunk_id="conflict-second",
            text="A synthetic information statement with a different answer.",
            content_hash="conflicting-hash",
            conflict_group="same-question",
        ),
    )
    conflicted = replace(
        evidence,
        passages=(
            replace(first, chunk=replace(first.chunk, conflict_group="same-question")),
            conflict,
        ),
    )
    with pytest.raises(EvidenceValidationError, match="conflicting"):
        validate_structured_answer(
            StructuredAnswer("Conflicting wording."), conflicted
        )


def test_api_abstains_on_unsupported_structured_claim(monkeypatch):
    evidence = synthetic_evidence()
    bad_answer = StructuredAnswer(
        conversational_text="Unsupported claim.",
        claims=(claim_for(evidence, "A synthetic label contains an unsupported dosage."),),
    )

    class BadProvider:
        async def generate(self, message, history, evidence):
            del message, history, evidence
            return ProviderResult(text=bad_answer.conversational_text, simulated=True, answer=bad_answer)

    monkeypatch.setattr(main, "knowledge_service", synthetic_service())
    monkeypatch.setattr(main, "build_provider", lambda settings: BadProvider())
    response = TestClient(main.app).post(
        "/api/chat", json={"message": "What information is listed on a label?"}
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "blocked"
    assert payload["category"] == "knowledge_abstention"
    assert "unsupported dosage" not in payload["message"]


def test_source_governance_is_revalidated_after_provider_returns():
    source_registry, document_registry, evidence = source_linked_evidence()

    class MutatingProvider:
        async def generate(self, message, history, evidence):
            del message, history, evidence
            source_registry.restrict(
                "synthetic-clinical-source", note="Synthetic restriction during generation"
            )
            return ProviderResult(text="Synthetic response.", simulated=True)

    governed = ensure_governed_provider(MutatingProvider(), document_registry)
    with pytest.raises(ProviderResultValidationError):
        asyncio.run(governed.generate("Question", [], evidence))



def test_default_ingestor_rejects_source_less_clinical_document():
    registry = DocumentRegistry()
    metadata = DocumentMetadata(
        document_id="source-less-clinical",
        title="Source-less Clinical Fixture",
        publisher="Synthetic Publisher",
        publication_date=date(2026, 1, 1),
        version="1",
        source_location="synthetic://source-less-clinical",
        acquired_at=date.today(),
        licensing_status="test-only",
        clinical_content=True,
        last_verification_date=date.today(),
    )
    registry.register(metadata)
    approved = registry.approve(
        metadata.document_id,
        metadata.version,
        ApprovalChecklist(
            authenticity_verified=True,
            publisher_verified=True,
            relevance_assessed=True,
            currency_assessed=True,
            licensing_reviewed=True,
            content_quality_reviewed=True,
            pharmacist_approved=True,
        ),
        reviewer="Synthetic Pharmacist",
    )
    package = DocumentPackage(
        metadata=approved,
        pages=(DocumentPage(1, (DocumentSection("Fact", "Synthetic content."),)),),
    )
    with pytest.raises(IngestionRejectedError, match="source_id"):
        ApprovedDocumentIngestor(registry).ingest(package)


def test_source_linked_clinical_fixture_uses_approved_permissions():
    _, document_registry, evidence = source_linked_evidence()
    assert evidence.is_sufficient is True
    assert evidence.passages[0].chunk.source_id == "synthetic-clinical-source"
    assert document_registry.all_documents()[0].clinical_content is True


def test_unapproved_or_permission_limited_sources_cannot_register_documents():
    cases: tuple[tuple[PermissionStatus, PermissionStatus], ...] = (
        ("not_verified", "not_verified"),
        ("confirmed_permitted", "not_verified"),
    )
    for permissions in cases:
        source = source_record(extraction=permissions[0], indexing=permissions[1])
        sources = SourceRegistry()
        sources.register(source)
        documents = DocumentRegistry(source_registry=sources)
        metadata = DocumentMetadata(
            document_id=f"limited-{permissions[0]}-{permissions[1]}",
            title="Limited Synthetic Source",
            publisher=source.publisher,
            publication_date=date(2026, 1, 1),
            version="1",
            source_location="synthetic://limited-source",
            acquired_at=date.today(),
            licensing_status="test-only",
            clinical_content=True,
            source_id=source.source_id,
        )
        with pytest.raises(RegistryError, match="internal indexing"):
            documents.register(metadata)


def test_test_synthetic_path_is_explicit_and_not_an_application_route():
    service = synthetic_service()
    assert service.index.retrieve("label directions warnings").is_sufficient
    route_paths = {
        getattr(route, "path", None) for route in main.app.routes
    }
    assert "/api/ingest" not in route_paths
    assert "/api/knowledge/ingest" not in route_paths
    # The normal production constructor remains clinical-governed; this explicit
    # test_synthetic mode appears only in test fixture construction.
    from backend.knowledge.validation import IngestionPolicy

    assert IngestionPolicy().mode == "clinical"
