import asyncio
from dataclasses import replace
from datetime import date

import pytest
from fastapi.testclient import TestClient

import backend.main as main
import backend.providers.cloudflare as cloudflare
from backend.knowledge.models import Citation, DocumentPackage, EvidencePassage
from backend.knowledge.registry import DocumentRegistry
from backend.knowledge.source_registry import SourceRegistry
from backend.knowledge.processing import IngestionRejectedError
from backend.knowledge.validation import (
    CitationValidationError,
    CitationValidator,
    EvidenceValidationError,
    EvidenceValidator,
)
from backend.providers.mock import MockProvider
from tests.helpers import synthetic_evidence, synthetic_service


class NeverCallClient:
    async def __aenter__(self):
        raise AssertionError("provider network call must not occur")

    async def __aexit__(self, exc_type, exc_value, traceback):
        return False


@pytest.mark.parametrize(
    "mutate, expected",
    [
        (lambda evidence: replace(evidence, passages=()), "sufficient and non-empty"),
        (lambda evidence: replace(evidence, status="insufficient"), "sufficient and non-empty"),
        (lambda evidence: replace(evidence, status="conflicting"), "sufficient and non-empty"),
        (
            lambda evidence: replace(
                evidence,
                passages=(
                    EvidencePassage(
                        chunk=replace(
                            evidence.passages[0].chunk,
                            last_verification_date=date(2020, 1, 1),
                        ),
                        relevance_score=1.0,
                    ),
                ),
            ),
            "stale",
        ),
        (
            lambda evidence: replace(
                evidence,
                passages=(
                    EvidencePassage(
                        chunk=replace(evidence.passages[0].chunk, page_number=0),
                        relevance_score=1.0,
                    ),
                ),
            ),
            "page or section",
        ),
        (
            lambda evidence: replace(
                evidence,
                passages=(
                    EvidencePassage(
                        chunk=replace(
                            evidence.passages[0].chunk,
                            source_id="unapproved-source",
                            citation=replace(
                                evidence.passages[0].citation,
                                source_id="unapproved-source",
                            ),
                        ),
                        relevance_score=1.0,
                    ),
                ),
            ),
            "source governance",
        ),
    ],
)
def test_evidence_validator_rejects_unsafe_bundles(mutate, expected):
    evidence = mutate(synthetic_evidence())
    registry = DocumentRegistry(source_registry=SourceRegistry())
    with pytest.raises(EvidenceValidationError, match=expected):
        EvidenceValidator(registry=registry).validate(evidence)


def test_both_providers_reject_invalid_evidence_before_generation(monkeypatch):
    invalid = replace(synthetic_evidence(), status="insufficient")
    with pytest.raises(EvidenceValidationError):
        asyncio.run(MockProvider().generate("Question", [], invalid))

    monkeypatch.setenv("LLM_PROVIDER", "cloudflare")
    monkeypatch.setenv("CLOUDFLARE_ACCOUNT_ID", "synthetic-account")
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "synthetic-token")
    monkeypatch.setattr(cloudflare.httpx, "AsyncClient", lambda timeout: NeverCallClient())
    with pytest.raises(EvidenceValidationError):
        asyncio.run(
            cloudflare.CloudflareProvider(main.get_settings()).generate(
                "Question", [], invalid
            )
        )


def test_valid_citation_must_match_retrieved_evidence():
    evidence = synthetic_evidence()
    citation = evidence.passages[0].citation
    assert CitationValidator().validate([citation], evidence) == (citation,)

    for fabricated in (
        replace(citation, document_id="unknown-document"),
        replace(citation, source_id="unknown-source"),
        replace(citation, page_number=99),
        replace(citation, section_heading="Invented section"),
        replace(citation, publisher="Unrelated publisher"),
    ):
        with pytest.raises(CitationValidationError):
            CitationValidator().validate([fabricated], evidence)


def test_citation_validator_rejects_citations_absent_from_bundle():
    evidence = synthetic_evidence()
    absent = Citation(
        publisher="Synthetic Test Publisher",
        title="Another Synthetic Document",
        version="1",
        publication_date=date(2026, 1, 1),
        page_number=1,
        section_heading="Other section",
        source_location="synthetic://other",
    )
    with pytest.raises(CitationValidationError, match="retrieved evidence"):
        CitationValidator().validate([absent], evidence)


def test_retrieval_rejects_weak_keyword_overlap_and_preserves_abstention():
    service = synthetic_service()
    assert service.index.retrieve("label unrelatedterm").is_sufficient is False
    assert service.index.retrieve("completely unrelated question").is_sufficient is False


def test_explicit_conflict_group_abstains_without_treating_all_wording_as_conflict():
    service = synthetic_service()
    base = service.index._chunks[next(iter(service.index._chunks))]
    first = replace(base, chunk_id="conflict-a", conflict_group="dose-group")
    second = replace(
        base,
        chunk_id="conflict-b",
        text="A synthetic information statement about the dose.",
        content_hash="different-hash",
        conflict_group="dose-group",
    )
    index = service.index.__class__(service.registry, relevance_threshold=0.2)
    index.add((first, second))
    result = index.retrieve("synthetic information")
    assert result.status == "conflicting"
    assert result.abstention_reason == "approved_sources_conflict"
    assert len(result.passages) == 2


def test_clinical_ingestion_mode_requires_source_id():
    service = synthetic_service()
    metadata = service.registry.get("synthetic-label-fixture", "test-1")
    package = DocumentPackage(metadata=metadata, pages=())
    from backend.knowledge.processing import DocumentProcessor

    with pytest.raises(IngestionRejectedError, match="requires a valid source_id"):
        DocumentProcessor(service.registry, mode="clinical").process(package)


def test_api_returns_safe_abstention_when_provider_validation_fails(monkeypatch):
    class InvalidEvidenceProvider:
        async def generate(self, message, history, evidence):
            raise EvidenceValidationError("internal validation detail")

    monkeypatch.setattr(main, "knowledge_service", synthetic_service())
    monkeypatch.setattr(main, "build_provider", lambda settings: InvalidEvidenceProvider())
    response = TestClient(main.app).post(
        "/api/chat", json={"message": "What information is listed on a label?"}
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "blocked"
    assert payload["category"] == "knowledge_abstention"
    assert "internal validation detail" not in response.text
