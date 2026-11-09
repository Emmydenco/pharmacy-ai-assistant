"""Runtime validation for evidence, citations, and future clinical ingestion."""

from dataclasses import dataclass
from datetime import date, timedelta
import re
from typing import Iterable, Literal

from backend.answers import StructuredAnswer
from backend.knowledge.models import Citation, DocumentMetadata, EvidenceBundle
from backend.knowledge.registry import DocumentRegistry
from backend.knowledge.source_registry import SourceRegistry, SourceRegistryError


class EvidenceValidationError(ValueError):
    """Raised when an evidence bundle cannot support provider inference."""


class AnswerValidationError(ValueError):
    """Raised when generated answer structure or claim support is unsafe."""


class CitationValidationError(AnswerValidationError):
    """Raised when a citation is not present in the retrieved evidence."""


class IngestionPolicyError(ValueError):
    """Raised when a document does not satisfy its declared ingestion mode."""


IngestionMode = Literal["test_synthetic", "clinical"]


@dataclass(frozen=True)
class IngestionPolicy:
    """Explicit boundary between backward-compatible fixtures and future clinical data."""

    mode: IngestionMode = "clinical"

    def validate_document(
        self,
        metadata: DocumentMetadata,
        *,
        source_registry: SourceRegistry | None,
    ) -> None:
        if (self.mode == "clinical" or metadata.clinical_content) and not metadata.source_id:
            raise IngestionPolicyError(
                "Clinical ingestion requires a valid source_id for every document"
            )
        if metadata.source_id is None:
            return
        if source_registry is None:
            raise IngestionPolicyError(
                "Source-linked ingestion requires a configured source registry"
            )
        try:
            source_registry.assert_indexing_allowed(metadata.source_id)
        except SourceRegistryError as exc:
            raise IngestionPolicyError(
                "The document source is not approved for internal indexing"
            ) from exc


class EvidenceValidator:
    """Validate evidence immediately before a provider can use it."""

    def __init__(
        self,
        *,
        registry: DocumentRegistry | None = None,
        max_verification_age_days: int = 365,
        as_of: date | None = None,
        clinical_mode: bool = False,
    ) -> None:
        if max_verification_age_days < 1:
            raise ValueError("max_verification_age_days must be positive")
        self.registry = registry
        self.max_verification_age_days = max_verification_age_days
        self.as_of = as_of or date.today()
        self.clinical_mode = clinical_mode

    def validate(self, evidence: EvidenceBundle) -> EvidenceBundle:
        if not isinstance(evidence, EvidenceBundle):
            raise EvidenceValidationError("A valid EvidenceBundle is required")
        if evidence.status != "sufficient" or not evidence.passages:
            raise EvidenceValidationError("Evidence must be sufficient and non-empty")
        if _has_conflicting_evidence(evidence):
            raise EvidenceValidationError("Evidence contains conflicting passages")
        cutoff = self.as_of - timedelta(days=self.max_verification_age_days)
        for passage in evidence.passages:
            chunk = passage.chunk
            if not chunk.document_id.strip() or not chunk.document_title.strip():
                raise EvidenceValidationError("Evidence is missing document provenance")
            if not chunk.publisher.strip() or not chunk.version.strip():
                raise EvidenceValidationError("Evidence is missing publisher or version provenance")
            if chunk.page_number < 1 or not chunk.section_heading.strip():
                raise EvidenceValidationError("Evidence has invalid page or section provenance")
            if not _valid_location(chunk.source_location):
                raise EvidenceValidationError("Evidence is missing a valid source location")
            if not chunk.content_hash.strip() or not chunk.text.strip():
                raise EvidenceValidationError("Evidence is missing content provenance")
            if chunk.last_verification_date is None:
                raise EvidenceValidationError("Evidence has no verification date")
            if chunk.last_verification_date < cutoff:
                raise EvidenceValidationError("Evidence is stale")
            self._validate_citation_matches_chunk(chunk)
            if chunk.source_id is None:
                if self.clinical_mode:
                    raise EvidenceValidationError(
                        "Clinical evidence requires a source_id"
                    )
            else:
                if self.registry is None or self.registry.source_registry is None:
                    raise EvidenceValidationError(
                        "Source-linked evidence requires source governance"
                    )
                try:
                    if not self.registry.source_registry.can_index(chunk.source_id, as_of=self.as_of):
                        raise EvidenceValidationError(
                            "Evidence source is not approved for internal indexing"
                        )
                except SourceRegistryError as exc:
                    raise EvidenceValidationError(
                        "Evidence source governance is not registered"
                    ) from exc
        return evidence

    @staticmethod
    def _validate_citation_matches_chunk(chunk) -> None:
        citation = chunk.citation
        if citation.publisher != chunk.publisher or citation.title != chunk.document_title:
            raise EvidenceValidationError("Citation does not match document provenance")
        if citation.version != chunk.version:
            raise EvidenceValidationError("Citation version does not match evidence")
        if citation.page_number != chunk.page_number:
            raise EvidenceValidationError("Citation page does not match evidence")
        if citation.section_heading != chunk.section_heading:
            raise EvidenceValidationError("Citation section does not match evidence")
        expected_location = chunk.source_reference or chunk.source_location
        if citation.source_location != expected_location:
            raise EvidenceValidationError("Citation source location does not match evidence")
        if citation.document_id not in (None, chunk.document_id):
            raise EvidenceValidationError("Citation document ID does not match evidence")
        if citation.source_id != chunk.source_id:
            raise EvidenceValidationError("Citation source ID does not match evidence")


class CitationValidator:
    """Validate structured citations against the exact retrieved evidence bundle."""

    def validate(
        self,
        citations: Iterable[Citation],
        evidence: EvidenceBundle,
        *,
        evidence_validator: EvidenceValidator | None = None,
        passage_ids: Iterable[str] | None = None,
    ) -> tuple[Citation, ...]:
        (evidence_validator or EvidenceValidator()).validate(evidence)
        validated: list[Citation] = []
        allowed_ids = set(passage_ids) if passage_ids is not None else None
        if allowed_ids is not None and not allowed_ids:
            raise CitationValidationError("Citation references no supporting passages")
        available = tuple(
            passage
            for passage in evidence.passages
            if allowed_ids is None or passage.chunk.chunk_id in allowed_ids
        )
        if allowed_ids is not None and len(available) != len(allowed_ids):
            raise CitationValidationError("Citation references an unknown passage")
        for citation in citations:
            self._validate_shape(citation)
            if not any(self._matches(citation, passage) for passage in available):
                raise CitationValidationError(
                    "Citation does not correspond to retrieved evidence"
                )
            validated.append(citation)
        return tuple(validated)

    @staticmethod
    def _validate_shape(citation: Citation) -> None:
        if not citation.publisher.strip() or not citation.title.strip():
            raise CitationValidationError("Citation is missing publisher or title")
        if citation.version is not None and not citation.version.strip():
            raise CitationValidationError("Citation version cannot be blank")
        if citation.page_number is not None and citation.page_number < 1:
            raise CitationValidationError("Citation page number must be positive")
        if citation.section_heading is not None and not citation.section_heading.strip():
            raise CitationValidationError("Citation section cannot be blank")
        if citation.source_location is not None and not _valid_location(citation.source_location):
            raise CitationValidationError("Citation source location is invalid")
        if citation.document_id is not None and not citation.document_id.strip():
            raise CitationValidationError("Citation document ID cannot be blank")
        if citation.source_id is not None and not citation.source_id.strip():
            raise CitationValidationError("Citation source ID cannot be blank")

    @staticmethod
    def _matches(citation: Citation, passage) -> bool:
        evidence_citation = passage.citation
        return (
            citation.publisher == evidence_citation.publisher
            and citation.title == evidence_citation.title
            and citation.version == evidence_citation.version
            and citation.publication_date == evidence_citation.publication_date
            and citation.page_number == evidence_citation.page_number
            and citation.section_heading == evidence_citation.section_heading
            and citation.source_location == evidence_citation.source_location
            and (citation.document_id is None or citation.document_id == passage.chunk.document_id)
            and (citation.source_id is None or citation.source_id == passage.chunk.source_id)
        )


def validate_evidence_bundle(
    evidence: EvidenceBundle,
    *,
    registry: DocumentRegistry | None = None,
    max_verification_age_days: int = 365,
    as_of: date | None = None,
    clinical_mode: bool = False,
) -> EvidenceBundle:
    """Convenience wrapper used by every provider before inference."""

    return EvidenceValidator(
        registry=registry,
        max_verification_age_days=max_verification_age_days,
        as_of=as_of,
        clinical_mode=clinical_mode,
    ).validate(evidence)


def validate_structured_answer(
    answer: StructuredAnswer,
    evidence: EvidenceBundle,
    *,
    evidence_validator: EvidenceValidator | None = None,
) -> StructuredAnswer:
    """Validate claim relationships without claiming clinical semantic certainty.

    Claim support is intentionally conservative and deterministic: every claim must
    point to known passages, cite those same passages, and have all meaningful claim
    terms present in at least one of its cited passage texts. This is a lexical
    safeguard, not semantic or clinical verification.
    """

    validator = evidence_validator or EvidenceValidator()
    validator.validate(evidence)
    if not isinstance(answer, StructuredAnswer) or not answer.conversational_text.strip():
        raise AnswerValidationError("Generated answer text is missing")

    passage_by_id = {passage.chunk.chunk_id: passage for passage in evidence.passages}
    seen_claim_ids: set[str] = set()
    for claim in answer.claims:
        if not claim.claim_id.strip() or claim.claim_id in seen_claim_ids:
            raise AnswerValidationError("Generated claims require unique IDs")
        seen_claim_ids.add(claim.claim_id)
        if not claim.text.strip():
            raise AnswerValidationError("Generated claims require text")
        if not claim.evidence_passage_ids:
            raise AnswerValidationError("Every factual claim requires supporting evidence")
        if any(passage_id not in passage_by_id for passage_id in claim.evidence_passage_ids):
            raise AnswerValidationError("A factual claim references unknown evidence")
        if not claim.citations:
            raise CitationValidationError("Every factual claim requires a citation")
        CitationValidator().validate(
            claim.citations,
            evidence,
            evidence_validator=validator,
            passage_ids=claim.evidence_passage_ids,
        )
        claim_terms = _claim_terms(claim.text)
        if not claim_terms:
            raise AnswerValidationError("A factual claim has no meaningful searchable terms")
        supporting_passages = tuple(
            passage_by_id[passage_id] for passage_id in claim.evidence_passage_ids
        )
        if not any(
            claim_terms <= _claim_terms(passage.chunk.text)
            for passage in supporting_passages
        ):
            raise AnswerValidationError(
                "The cited evidence does not conservatively support the factual claim"
            )
    return answer


def _valid_location(value: str | None) -> bool:
    return bool(
        value
        and value.strip()
        and value.startswith(("https://", "http://", "synthetic://"))
    )


def _has_conflicting_evidence(evidence: EvidenceBundle) -> bool:
    grouped: dict[str, set[str]] = {}
    for passage in evidence.passages:
        key = passage.chunk.conflict_group or passage.chunk.claim_key
        if key:
            grouped.setdefault(key, set()).add(passage.chunk.content_hash)
    return any(len(content_hashes) > 1 for content_hashes in grouped.values())


_CLAIM_STOPWORDS = frozenset(
    {
        "about",
        "after",
        "also",
        "and",
        "are",
        "because",
        "before",
        "being",
        "contains",
        "could",
        "does",
        "from",
        "have",
        "into",
        "might",
        "more",
        "that",
        "their",
        "there",
        "these",
        "they",
        "this",
        "those",
        "with",
    }
)


def _claim_terms(value: str) -> set[str]:
    return {
        term
        for term in re.findall(r"[a-z0-9]{3,}", value.lower())
        if term not in _CLAIM_STOPWORDS
    }
