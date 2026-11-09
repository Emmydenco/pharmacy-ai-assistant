from datetime import date, timedelta
from typing import cast

import pytest

from backend.knowledge.models import (
    ApprovalChecklist,
    DocumentMetadata,
    DocumentPage,
    DocumentPackage,
    DocumentSection,
    SourcePermissions,
    SourceRecord,
    PermissionStatus,
    SourceReviewStatus,
)
from backend.knowledge.processing import ApprovedDocumentIngestor, IngestionRejectedError
from backend.knowledge.registry import DocumentRegistry, RegistryError
from backend.knowledge.retrieval import InMemoryKnowledgeIndex
from backend.knowledge.routing import SourceRouter
from backend.knowledge.source_registry import (
    DuplicateSourceError,
    SourceRegistry,
    SourceTransitionError,
)


FUTURE_REVIEW = date.today() + timedelta(days=30)


def source(
    *,
    source_id: str = "synthetic-source",
    category: str = "nigerian_regulatory",
    review_status: SourceReviewStatus = "draft",
    last_verified: date | None = date.today(),
    next_review: date | None = FUTURE_REVIEW,
    linking: PermissionStatus = "confirmed_permitted",
    extraction: PermissionStatus = "not_verified",
    indexing: PermissionStatus = "not_verified",
    publisher: str = "Synthetic Publisher",
    jurisdiction: str = "Nigeria",
    official_url: str = "synthetic://source",
) -> SourceRecord:
    return SourceRecord(
        source_id=source_id,
        source_name="Synthetic Source",
        publisher=publisher,
        official_url=official_url,
        source_category=category,
        jurisdiction=jurisdiction,
        applicable_market="Nigeria",
        scope_classification="national",
        authoritative_for=("synthetic governance",),
        authority_limitations=("Synthetic fixture only",),
        authority_level="primary",
        permissions=SourcePermissions(
            public_accessibility="confirmed_permitted",
            linking=linking,
            downloading="not_verified",
            extraction=extraction,
            internal_indexing=indexing,
            reproduction="not_verified",
        ),
        publication_date=date(2026, 1, 1),
        last_verification_date=last_verified,
        next_review_date=next_review,
        review_status=review_status,
    )


def approve_linking(registry: SourceRegistry, source_id: str = "synthetic-source") -> None:
    registry.submit_for_review(source_id)
    registry.approve_for_linking(source_id, reviewer="Synthetic Reviewer")


def approve_indexing(registry: SourceRegistry, source_id: str = "synthetic-source") -> None:
    approve_linking(registry, source_id)
    registry.approve_for_indexing(source_id, reviewer="Synthetic Pharmacist")


def test_source_creation_validates_identity_and_unique_ids():
    registry = SourceRegistry()
    registry.register(source())
    with pytest.raises(DuplicateSourceError):
        registry.register(source())
    with pytest.raises(ValueError, match="official_url"):
        source(official_url="not-a-url")
    with pytest.raises(ValueError, match="permission status"):
        SourcePermissions(linking=cast(PermissionStatus, "unknown"))


def test_source_workflow_keeps_linking_separate_from_indexing():
    registry = SourceRegistry()
    registry.register(source())
    approve_linking(registry)
    assert registry.can_link("synthetic-source") is True
    assert registry.can_index("synthetic-source") is False
    with pytest.raises(SourceTransitionError, match="extraction permission"):
        registry.approve_for_indexing("synthetic-source", reviewer="Synthetic Reviewer")


def test_indexing_requires_explicit_extraction_and_indexing_permissions():
    registry = SourceRegistry()
    registry.register(source(extraction="confirmed_permitted", indexing="confirmed_permitted"))
    approve_indexing(registry)
    assert registry.can_index("synthetic-source") is True


def test_source_metadata_and_permission_governance_flags_unverified_or_expired_records():
    registry = SourceRegistry()
    registry.register(source(source_id="unverified", last_verified=None, next_review=None))
    registry.register(
        source(
            source_id="expired",
            last_verified=date.today() - timedelta(days=30),
            next_review=date.today() - timedelta(days=1),
        )
    )
    assert "missing_last_verification_date" in registry.governance_issues("unverified")
    assert "missing_next_review_date" in registry.governance_issues("unverified")
    assert "review_due" in registry.governance_issues("expired")
    assert registry.can_link("expired") is False


def test_rejected_restricted_and_conflicting_sources_are_not_routable():
    registry = SourceRegistry()
    registry.register(source(source_id="rejected"))
    registry.register(source(source_id="conflict", publisher="Different Publisher"))
    registry.register(source(source_id="routable", official_url="synthetic://routable"))
    registry.submit_for_review("rejected")
    registry.reject("rejected", note="Synthetic rejection")
    approve_linking(registry, "routable")
    assert registry.metadata_conflicts() == (("rejected", "conflict"),)
    router = SourceRouter()
    routed = router.route("nigerian_drug_registration_recalls_alerts", registry)
    assert [item.source_id for item in routed] == ["routable"]


def test_withdrawn_source_is_flagged_and_cannot_be_linked():
    registry = SourceRegistry()
    registry.register(source())
    approve_linking(registry)
    registry.withdraw("synthetic-source", note="Synthetic withdrawal")
    assert registry.can_link("synthetic-source") is False
    assert "source_withdrawn" in registry.governance_issues("synthetic-source")


def test_ingestion_rejects_source_without_indexing_approval():
    source_registry = SourceRegistry()
    source_registry.register(source())
    approve_linking(source_registry)
    document_registry = DocumentRegistry(source_registry=source_registry)
    metadata = DocumentMetadata(
        document_id="synthetic-document",
        title="Synthetic Document",
        publisher="Synthetic Publisher",
        publication_date=date(2026, 1, 1),
        version="1",
        source_location="synthetic://document",
        acquired_at=date.today(),
        licensing_status="synthetic-only",
        source_id="synthetic-source",
    )
    with pytest.raises(RegistryError, match="internal indexing"):
        document_registry.register(metadata)


def test_source_governance_is_checked_again_before_ingestion_and_retrieval():
    source_registry = SourceRegistry()
    source_registry.register(source(extraction="confirmed_permitted", indexing="confirmed_permitted"))
    approve_indexing(source_registry)
    document_registry = DocumentRegistry(source_registry=source_registry)
    metadata = DocumentMetadata(
        document_id="synthetic-document",
        title="Synthetic Document",
        publisher="Synthetic Publisher",
        publication_date=date(2026, 1, 1),
        version="1",
        source_location="synthetic://document",
        acquired_at=date.today(),
        licensing_status="synthetic-only",
        source_id="synthetic-source",
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
        ),
        reviewer="Synthetic Reviewer",
    )
    package = DocumentPackage(
        metadata=approved,
        pages=(
            DocumentPage(
                page_number=1,
                sections=(DocumentSection("Synthetic evidence", "A synthetic governance fact."),),
            ),
        ),
    )
    processed = ApprovedDocumentIngestor(document_registry).ingest(package)
    index = InMemoryKnowledgeIndex(document_registry, relevance_threshold=0.2)
    index.add(processed.chunks)
    assert index.retrieve("What is the synthetic governance fact?").is_sufficient

    source_registry.expire("synthetic-source")
    with pytest.raises(IngestionRejectedError, match="internal indexing"):
        ApprovedDocumentIngestor(document_registry).ingest(package)
    assert not index.retrieve("What is the synthetic governance fact?").is_sufficient
