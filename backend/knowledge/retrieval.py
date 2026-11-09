"""Deterministic retrieval for approved, provenance-rich knowledge chunks."""

from collections import defaultdict
from datetime import date, timedelta
import re
from typing import Protocol

from backend.knowledge.models import (
    EvidenceBundle,
    EvidencePassage,
    KnowledgeChunk,
    ReleaseProvenance,
    SourceCapability,
)
from backend.knowledge.registry import DocumentRegistry
from backend.knowledge.source_registry import SourceRegistryError


class RetrievalIndex(Protocol):
    def add(self, chunks: tuple[KnowledgeChunk, ...]) -> None:
        """Add already processed and approved chunks."""

    def retrieve(
        self,
        query: str,
        *,
        top_k: int = 5,
        jurisdiction: str | None = None,
        required_capability: SourceCapability | None = None,
    ) -> EvidenceBundle:
        """Return ranked evidence or a capability-aware abstention result."""

    def rollback_release(self, provenance: ReleaseProvenance) -> int:
        """Remove chunks belonging to one exact release identity."""


class InMemoryKnowledgeIndex:
    def __init__(
        self,
        registry: DocumentRegistry,
        *,
        relevance_threshold: float = 0.25,
        max_verification_age_days: int = 365,
        minimum_term_matches: int = 2,
    ) -> None:
        if not 0 < relevance_threshold <= 1:
            raise ValueError("relevance_threshold must be between 0 and 1")
        if max_verification_age_days < 1:
            raise ValueError("max_verification_age_days must be positive")
        if minimum_term_matches < 1:
            raise ValueError("minimum_term_matches must be positive")
        self.registry = registry
        self.relevance_threshold = relevance_threshold
        self.minimum_term_matches = minimum_term_matches
        self.verification_cutoff = date.today() - timedelta(days=max_verification_age_days)
        self._chunks: dict[str, KnowledgeChunk] = {}

    def add(self, chunks: tuple[KnowledgeChunk, ...]) -> None:
        for chunk in chunks:
            metadata = self.registry.get(chunk.document_id, chunk.version)
            if not self.registry.is_approved(chunk.document_id, chunk.version):
                raise ValueError("Only registry-approved document chunks may be indexed")
            if chunk.last_verification_date is None:
                raise ValueError("Indexed chunks require a verification date")
            self._assert_source_indexing_allowed(chunk.source_id)
            self._assert_chunk_provenance_matches_document(chunk, metadata)
            if chunk.chunk_id in self._chunks:
                raise ValueError(f"Duplicate knowledge chunk: {chunk.chunk_id}")
            self._chunks[chunk.chunk_id] = chunk

    def retrieve(
        self,
        query: str,
        *,
        top_k: int = 5,
        jurisdiction: str | None = None,
        required_capability: SourceCapability | None = None,
    ) -> EvidenceBundle:
        if top_k < 1:
            raise ValueError("top_k must be positive")
        query_terms = _terms(query)
        if not query_terms:
            return EvidenceBundle.abstain(
                query,
                "question_has_no_searchable_terms",
                required_capability=required_capability,
            )

        candidates: list[EvidencePassage] = []
        for chunk in self._chunks.values():
            if (
                chunk.last_verification_date is None
                or chunk.last_verification_date < self.verification_cutoff
                or not self._source_can_index(chunk.source_id)
                or not self._jurisdiction_matches(chunk.source_id, jurisdiction)
                or not self._capability_matches(chunk, required_capability)
            ):
                continue
            match_count = len(query_terms & _terms(chunk.text))
            required_matches = min(self.minimum_term_matches, len(query_terms))
            score = match_count / len(query_terms)
            source = self._source(chunk.source_id)
            if source is not None and source.authority_level == "primary":
                score = min(1.0, score + 0.05)
            if match_count >= required_matches and score >= self.relevance_threshold:
                candidates.append(EvidencePassage(chunk=chunk, relevance_score=score))
        candidates.sort(key=lambda item: (-item.relevance_score, item.chunk.chunk_id))
        selected = tuple(candidates[:top_k])
        if not selected:
            return EvidenceBundle.abstain(
                query,
                "no_relevant_approved_evidence",
                required_capability=required_capability,
            )
        if _has_conflict(selected):
            return EvidenceBundle(
                query=query,
                status="conflicting",
                passages=selected,
                abstention_reason="approved_sources_conflict",
                required_capability=required_capability,
            )
        return EvidenceBundle(
            query=query,
            status="sufficient",
            passages=selected,
            required_capability=required_capability,
        )

    def rollback_release(self, provenance: ReleaseProvenance) -> int:
        """Remove only chunks carrying one exact release identity.

        Citations and evidence references are nested inside the removed chunks, so
        removing by structured identity cannot leave a separate citation record behind.
        The operation is deterministic and safe to repeat.
        """

        matching_ids = [
            chunk_id
            for chunk_id, chunk in self._chunks.items()
            if chunk.release_provenance is not None
            and chunk.release_provenance.identity == provenance.identity
        ]
        for chunk_id in matching_ids:
            del self._chunks[chunk_id]
        return len(matching_ids)

    def release_chunk_ids(self, provenance: ReleaseProvenance) -> tuple[str, ...]:
        """Return indexed chunk IDs for one exact release identity."""

        return tuple(
            chunk_id
            for chunk_id, chunk in self._chunks.items()
            if chunk.release_provenance is not None
            and chunk.release_provenance.identity == provenance.identity
        )

    def _source_can_index(self, source_id: str | None) -> bool:
        if source_id is None:
            return True
        if self.registry.source_registry is None:
            return False
        try:
            return self.registry.source_registry.can_index(source_id)
        except SourceRegistryError:
            return False

    def _source(self, source_id: str | None):
        if source_id is None or self.registry.source_registry is None:
            return None
        try:
            return self.registry.source_registry.get(source_id)
        except SourceRegistryError:
            return None

    def _capability_matches(
        self,
        chunk: KnowledgeChunk,
        required_capability: SourceCapability | None,
    ) -> bool:
        if required_capability is None:
            return True
        if chunk.source_id is None or self.registry.source_registry is None:
            return False
        if chunk.source_capability not in (None, required_capability):
            return False
        try:
            return self.registry.source_registry.supports_capability(
                chunk.source_id,
                required_capability,
            )
        except SourceRegistryError:
            return False

    def _jurisdiction_matches(self, source_id: str | None, jurisdiction: str | None) -> bool:
        if jurisdiction is None or source_id is None:
            return True
        source = self._source(source_id)
        if source is None:
            return False
        requested = jurisdiction.strip().lower()
        return requested in {
            source.jurisdiction.strip().lower(),
            source.applicable_market.strip().lower(),
            "international",
            "global",
        }

    def _assert_source_indexing_allowed(self, source_id: str | None) -> None:
        if source_id is None:
            return
        if self.registry.source_registry is None:
            raise ValueError("A source registry is required for source-linked chunks")
        try:
            self.registry.source_registry.assert_indexing_allowed(source_id)
        except SourceRegistryError as exc:
            raise ValueError("Source is not approved for internal indexing") from exc

    @staticmethod
    def _assert_chunk_provenance_matches_document(chunk: KnowledgeChunk, metadata) -> None:
        if chunk.release_provenance != metadata.release_provenance:
            raise ValueError("Chunk release provenance does not match its registered document")
        if chunk.source_capability != metadata.source_capability:
            raise ValueError("Chunk source capability does not match its registered document")
        if chunk.source_id != metadata.source_id:
            raise ValueError("Chunk source identity does not match its registered document")
        if metadata.release_provenance is not None:
            if metadata.scope_approval is None or not chunk.source_file_id or not chunk.source_field_ids:
                raise ValueError("Release-scoped chunks require file and field provenance")
            if not metadata.scope_approval.allows(
                file_id=chunk.source_file_id,
                field_ids=chunk.source_field_ids,
                capability=chunk.source_capability,
            ):
                raise ValueError("Chunk is outside the approved release file/field scope")


def _terms(value: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]{3,}", value.lower()))


def _has_conflict(passages: tuple[EvidencePassage, ...]) -> bool:
    grouped: dict[str, set[str]] = defaultdict(set)
    for passage in passages:
        claim_key = passage.chunk.conflict_group or passage.chunk.claim_key
        if claim_key:
            grouped[claim_key].add(passage.chunk.content_hash)
    return any(len(hashes) > 1 for hashes in grouped.values())
