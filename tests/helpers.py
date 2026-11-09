"""Synthetic-only fixtures; never loaded by the application runtime."""

from datetime import date

from backend.knowledge.models import (
    ApprovalChecklist,
    Citation,
    DocumentMetadata,
    DocumentPage,
    DocumentPackage,
    DocumentSection,
    EvidenceBundle,
    EvidencePassage,
    KnowledgeChunk,
)
from backend.knowledge.processing import DocumentProcessor
from backend.knowledge.registry import DocumentRegistry
from backend.knowledge.retrieval import InMemoryKnowledgeIndex
from backend.knowledge.service import KnowledgeService


def synthetic_evidence() -> EvidenceBundle:
    metadata = DocumentMetadata(
        document_id="synthetic-label-fixture",
        title="Synthetic Label Information Fixture",
        publisher="Synthetic Test Publisher",
        publication_date=date(2026, 1, 1),
        version="test-1",
        source_location="synthetic://label-fixture",
        acquired_at=date(2026, 1, 2),
        review_status="approved",
        reviewer="Synthetic Reviewer",
        licensing_status="test-only",
        last_verification_date=date(2026, 1, 3),
    )
    chunk = KnowledgeChunk(
        chunk_id="synthetic-label-fixture:test-1:1:0:1",
        document_id=metadata.document_id,
        document_title=metadata.title,
        publisher=metadata.publisher,
        version=metadata.version,
        section_heading="Label information",
        page_number=1,
        source_location=metadata.source_location,
        source_reference="synthetic://label-fixture#label-information",
        content_hash="synthetic-content-hash",
        text="A synthetic label example lists a product name, directions, warnings, and storage information.",
        citation=Citation(
            publisher=metadata.publisher,
            title=metadata.title,
            version=metadata.version,
            publication_date=metadata.publication_date,
            page_number=1,
            section_heading="Label information",
            source_location="synthetic://label-fixture#label-information",
            document_id=metadata.document_id,
        ),
        claim_key="synthetic-label-fields",
        last_verification_date=metadata.last_verification_date,
    )
    return EvidenceBundle(
        query="What information is listed on a label?",
        status="sufficient",
        passages=(EvidencePassage(chunk=chunk, relevance_score=1.0),),
    )


def synthetic_service() -> KnowledgeService:
    metadata = DocumentMetadata(
        document_id="synthetic-label-fixture",
        title="Synthetic Label Information Fixture",
        publisher="Synthetic Test Publisher",
        publication_date=date(2026, 1, 1),
        version="test-1",
        source_location="synthetic://label-fixture",
        acquired_at=date(2026, 1, 2),
        reviewer="Synthetic Reviewer",
        licensing_status="test-only",
        last_verification_date=date(2026, 1, 3),
    )
    registry = DocumentRegistry()
    registry.register(metadata)
    registry.approve(
        metadata.document_id,
        metadata.version,
        ApprovalChecklist(
            authenticity_verified=True,
            publisher_verified=True,
            relevance_assessed=True,
            currency_assessed=True,
            licensing_reviewed=True,
            content_quality_reviewed=True,
        ),
        reviewer="Synthetic Reviewer",
    )
    package = DocumentPackage(
        metadata=registry.get(metadata.document_id, metadata.version),
        pages=(
            DocumentPage(
                page_number=1,
                sections=(
                    DocumentSection(
                        heading="Label information",
                        content="A synthetic label example lists a product name, directions, warnings, and storage information.",
                        source_reference="synthetic://label-fixture#label-information",
                        claim_key="synthetic-label-fields",
                    ),
                ),
            ),
        ),
    )
    # Synthetic fixtures intentionally use the explicit test-only compatibility mode.
    processed = DocumentProcessor(registry, mode="test_synthetic").process(package)
    index = InMemoryKnowledgeIndex(registry, relevance_threshold=0.2)
    index.add(processed.chunks)
    return KnowledgeService(index=index, registry=registry)
