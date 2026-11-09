from datetime import date

import pytest
from fastapi.testclient import TestClient

import backend.main as main
from backend.knowledge.models import (
    ApprovalChecklist,
    Citation,
    DocumentMetadata,
    DocumentPage,
    DocumentPackage,
    DocumentSection,
    EvidencePassage,
    KnowledgeChunk,
)
from backend.knowledge.processing import ApprovedDocumentIngestor, DocumentProcessor, IngestionRejectedError
from backend.knowledge.registry import ApprovalRejectedError, DocumentRegistry, RegistryError
from backend.knowledge.retrieval import InMemoryKnowledgeIndex
from backend.knowledge.service import KnowledgeService
from backend.providers.base import ProviderResult
from tests.helpers import synthetic_service


client = TestClient(main.app)


def metadata(
    *,
    document_id: str = "synthetic-document",
    version: str = "1.0",
    clinical_content: bool = False,
    last_verification_date: date | None = None,
) -> DocumentMetadata:
    return DocumentMetadata(
        document_id=document_id,
        title="Synthetic Governance Fixture",
        publisher="Synthetic Test Publisher",
        publication_date=date(2026, 1, 1),
        version=version,
        source_location=f"synthetic://{document_id}",
        acquired_at=date(2026, 1, 2),
        review_status="pending_review",
        licensing_status="test-only",
        clinical_content=clinical_content,
        last_verification_date=last_verification_date,
    )


def full_checklist(*, pharmacist: bool = False) -> ApprovalChecklist:
    return ApprovalChecklist(
        authenticity_verified=True,
        publisher_verified=True,
        relevance_assessed=True,
        currency_assessed=True,
        licensing_reviewed=True,
        content_quality_reviewed=True,
        pharmacist_approved=pharmacist,
    )


def package_for(source: DocumentMetadata) -> DocumentPackage:
    return DocumentPackage(
        metadata=source,
        pages=(
            DocumentPage(
                page_number=2,
                sections=(
                    DocumentSection(
                        heading="Synthetic section",
                        content="Synthetic evidence describes a fictional label field and its source reference.",
                        source_reference="synthetic://document#section",
                        claim_key="fictional-label-field",
                    ),
                ),
            ),
        ),
    )


def register_approved(
    registry: DocumentRegistry,
    *,
    document_id: str,
    verification_date: date,
) -> DocumentMetadata:
    source = metadata(
        document_id=document_id,
        version="1",
        last_verification_date=verification_date,
    )
    registry.register(source)
    return registry.approve(
        source.document_id,
        source.version,
        full_checklist(),
        reviewer="Synthetic Reviewer",
    )


def test_registry_captures_metadata_and_requires_governance_approval():
    registry = DocumentRegistry()
    source = metadata()
    registry.register(source)

    with pytest.raises(RegistryError, match="metadata are required"):
        registry.register(metadata(document_id=""))

    with pytest.raises(ApprovalRejectedError):
        registry.approve(source.document_id, source.version, ApprovalChecklist(), reviewer="")

    approved = registry.approve(
        source.document_id,
        source.version,
        full_checklist(),
        reviewer="Synthetic Reviewer",
    )
    assert approved.review_status == "approved"
    assert approved.reviewer == "Synthetic Reviewer"
    assert approved.source_location == "synthetic://synthetic-document"


def test_clinical_content_requires_pharmacist_approval():
    registry = DocumentRegistry()
    source = metadata(clinical_content=True)
    registry.register(source)
    with pytest.raises(ApprovalRejectedError):
        registry.approve(
            source.document_id,
            source.version,
            full_checklist(pharmacist=False),
            reviewer="Synthetic Reviewer",
        )

    approved = registry.approve(
        source.document_id,
        source.version,
        full_checklist(pharmacist=True),
        reviewer="Synthetic Pharmacist",
    )
    assert approved.review_status == "approved"


def test_ingestion_rejects_unapproved_and_preserves_provenance_after_approval():
    registry = DocumentRegistry()
    source = metadata()
    registry.register(source)
    package = package_for(source)
    processor = DocumentProcessor(registry, mode="test_synthetic")

    with pytest.raises(IngestionRejectedError, match="Only approved"):
        processor.process(package)

    registry.approve(source.document_id, source.version, full_checklist(), reviewer="Synthetic Reviewer")
    approved_package = package_for(registry.get(source.document_id, source.version))
    processed = processor.process(approved_package)
    chunk = processed.chunks[0]
    assert chunk.document_id == source.document_id
    assert chunk.document_title == source.title
    assert chunk.section_heading == "Synthetic section"
    assert chunk.page_number == 2
    assert chunk.source_reference == "synthetic://document#section"
    assert chunk.content_hash
    assert chunk.citation.publisher == source.publisher
    assert chunk.citation.version == source.version


def test_processing_rejects_duplicate_or_empty_page_structure():
    registry = DocumentRegistry()
    source = metadata(last_verification_date=date.today())
    registry.register(source)
    source = registry.approve(
        source.document_id,
        source.version,
        full_checklist(),
        reviewer="Synthetic Reviewer",
    )
    processor = DocumentProcessor(registry, mode="test_synthetic")
    duplicate_pages = DocumentPackage(
        metadata=source,
        pages=(
            DocumentPage(page_number=1, sections=(DocumentSection("A", "text"),)),
            DocumentPage(page_number=1, sections=(DocumentSection("B", "text"),)),
        ),
    )
    with pytest.raises(IngestionRejectedError, match="unique positive"):
        processor.process(duplicate_pages)

    duplicate_sections = DocumentPackage(
        metadata=source,
        pages=(
            DocumentPage(
                page_number=1,
                sections=(
                    DocumentSection("Same", "same content"),
                    DocumentSection("Same", "same content"),
                ),
            ),
        ),
    )
    with pytest.raises(IngestionRejectedError, match="duplicate sections"):
        processor.process(duplicate_sections)

    empty_section = DocumentPackage(
        metadata=source,
        pages=(DocumentPage(page_number=1, sections=(DocumentSection("", ""),)),),
    )
    with pytest.raises(IngestionRejectedError, match="headings and content"):
        processor.process(empty_section)


def test_retrieval_returns_ranked_passage_provenance_and_citation():
    service = synthetic_service()
    decision = service.assess("What information is listed on a label?")
    assert decision.can_answer is True
    passage = decision.evidence.passages[0]
    assert passage.relevance_score >= 0.2
    assert passage.chunk.document_id == "synthetic-label-fixture"
    assert passage.citation.source_location.startswith("synthetic://")
    assert "Synthetic Test Publisher" in passage.citation.render()


def test_retrieval_abstains_when_no_approved_evidence_matches():
    service = synthetic_service()
    decision = service.assess("What is an unrelated fictional topic?")
    assert decision.can_answer is False
    assert decision.evidence.status == "insufficient"
    assert decision.evidence.abstention_reason == "no_relevant_approved_evidence"


def test_retrieval_abstains_when_matching_source_is_stale():
    registry = DocumentRegistry()
    source = register_approved(
        registry,
        document_id="stale-doc",
        verification_date=date(2020, 1, 2),
    )
    index = InMemoryKnowledgeIndex(
        registry,
        relevance_threshold=0.2,
        max_verification_age_days=30,
    )
    citation = Citation(
        publisher="Synthetic Publisher",
        title="Synthetic Stale Fixture",
        version="1",
        publication_date=date(2020, 1, 1),
        page_number=1,
        section_heading="Stale",
        source_location="synthetic://stale",
    )
    index.add(
        (
            KnowledgeChunk(
                chunk_id="stale-1",
                document_id="stale-doc",
                document_title="Synthetic Stale Fixture",
                publisher="Synthetic Publisher",
                version=source.version,
                section_heading="Stale",
                page_number=1,
                source_location="synthetic://stale",
                source_reference=None,
                content_hash="stale-hash",
                text="Synthetic label status is stale.",
                citation=citation,
                last_verification_date=date(2020, 1, 2),
            ),
        )
    )
    evidence = index.retrieve("What is the synthetic label status?")
    assert evidence.status == "insufficient"
    assert evidence.abstention_reason == "no_relevant_approved_evidence"


def test_retrieval_abstains_on_conflicting_claims():
    registry = DocumentRegistry()
    register_approved(registry, document_id="doc-1", verification_date=date.today())
    register_approved(registry, document_id="doc-2", verification_date=date.today())
    index = InMemoryKnowledgeIndex(registry, relevance_threshold=0.2)
    citation = Citation(
        publisher="Synthetic Publisher",
        title="Synthetic Conflict Fixture",
        version="1",
        publication_date=date(2026, 1, 1),
        page_number=1,
        section_heading="Conflict",
        source_location="synthetic://conflict",
    )
    chunks = tuple(
        KnowledgeChunk(
            chunk_id=f"conflict-{number}",
            document_id=f"doc-{number}",
            document_title="Synthetic Conflict Fixture",
            publisher="Synthetic Publisher",
            version="1",
            section_heading="Conflict",
            page_number=1,
            source_location="synthetic://conflict",
            source_reference=None,
            content_hash=f"hash-{number}",
            text=text,
            citation=citation,
            claim_key="same-fictional-claim",
            last_verification_date=date.today(),
        )
        for number, text in enumerate(
            ("Synthetic label status is amber.", "Synthetic label status is blue."),
            start=1,
        )
    )
    index.add(chunks)
    evidence = index.retrieve("What is the synthetic label status?", top_k=2)
    assert evidence.status == "conflicting"
    assert evidence.is_sufficient is False
    assert evidence.abstention_reason == "approved_sources_conflict"


def test_empty_runtime_abstains_before_provider_construction(monkeypatch):
    monkeypatch.setattr(main, "knowledge_service", KnowledgeService.empty())

    def provider_must_not_be_built(settings):
        raise AssertionError("provider must not be built without evidence")

    monkeypatch.setattr(main, "build_provider", provider_must_not_be_built)
    response = client.post("/api/chat", json={"message": "What information is listed on a label?"})
    payload = response.json()
    assert response.status_code == 200
    assert payload["status"] == "blocked"
    assert payload["category"] == "knowledge_abstention"
    assert payload["provider"] == "knowledge_base"
    assert payload["simulated"] is True


def test_provider_receives_evidence_only_after_retrieval(monkeypatch):
    monkeypatch.setattr(main, "knowledge_service", synthetic_service())
    captured = {}

    class StubProvider:
        async def generate(self, message, history, evidence):
            captured["message"] = message
            captured["evidence"] = evidence
            return ProviderResult(text="grounded synthetic response", simulated=True)

    monkeypatch.setattr(main, "build_provider", lambda settings: StubProvider())
    response = client.post("/api/chat", json={"message": "What information is listed on a label?"})
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["message"] == "grounded synthetic response"
    assert captured["evidence"].is_sufficient is True
