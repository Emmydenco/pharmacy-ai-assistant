"""In-memory source registry with explicit permission and review governance."""

from collections import defaultdict
from dataclasses import replace
from datetime import date

from backend.knowledge.models import SourceCapability, SourceRecord


class SourceRegistryError(ValueError):
    """Base error for source registry operations."""


class DuplicateSourceError(SourceRegistryError):
    """Raised when a source ID is registered twice."""


class SourceNotFoundError(SourceRegistryError):
    """Raised when a source ID is absent."""


class SourceValidationError(SourceRegistryError):
    """Raised when source metadata or permissions are incomplete."""


class SourceTransitionError(SourceRegistryError):
    """Raised when a source cannot make the requested governance transition."""


class SourceRegistry:
    """Small storage-independent registry for source metadata only."""

    def __init__(self) -> None:
        self._sources: dict[str, SourceRecord] = {}

    def register(self, source: SourceRecord) -> SourceRecord:
        if source.source_id in self._sources:
            raise DuplicateSourceError(f"Source ID already registered: {source.source_id}")
        if source.review_status != "draft":
            raise SourceValidationError("New source records must start in draft")
        self._sources[source.source_id] = source
        return source

    def get(self, source_id: str) -> SourceRecord:
        try:
            return self._sources[source_id]
        except KeyError as exc:
            raise SourceNotFoundError(f"Source not found: {source_id}") from exc

    def all_sources(self) -> tuple[SourceRecord, ...]:
        return tuple(self._sources.values())

    def submit_for_review(self, source_id: str) -> SourceRecord:
        source = self.get(source_id)
        if source.review_status != "draft":
            raise SourceTransitionError("Only draft sources may enter pending_review")
        updated = replace(source, review_status="pending_review")
        self._sources[source_id] = updated
        return updated

    def approve_for_linking(
        self,
        source_id: str,
        *,
        reviewer: str,
        approval_date: date | None = None,
    ) -> SourceRecord:
        source = self.get(source_id)
        self._require_review_ready(source, expected_status="pending_review", reviewer=reviewer)
        if source.permissions.linking != "confirmed_permitted":
            raise SourceTransitionError("Linking permission is not confirmed")
        updated = replace(
            source,
            review_status="approved_for_linking",
            reviewer=reviewer.strip(),
            approval_date=approval_date or date.today(),
        )
        self._sources[source_id] = updated
        return updated

    def approve_for_indexing(
        self,
        source_id: str,
        *,
        reviewer: str,
        approval_date: date | None = None,
    ) -> SourceRecord:
        source = self.get(source_id)
        self._require_review_ready(source, expected_status="approved_for_linking", reviewer=reviewer)
        if source.permissions.extraction != "confirmed_permitted":
            raise SourceTransitionError("Content-extraction permission is not confirmed")
        if source.permissions.internal_indexing != "confirmed_permitted":
            raise SourceTransitionError("Internal-indexing permission is not confirmed")
        updated = replace(
            source,
            review_status="approved_for_indexing",
            reviewer=reviewer.strip(),
            approval_date=approval_date or date.today(),
        )
        self._sources[source_id] = updated
        return updated

    def restrict(self, source_id: str, *, note: str) -> SourceRecord:
        source = self.get(source_id)
        if not note.strip():
            raise SourceTransitionError("A restriction note is required")
        updated = replace(source, review_status="restricted", review_notes=note.strip())
        self._sources[source_id] = updated
        return updated

    def reject(self, source_id: str, *, note: str) -> SourceRecord:
        source = self.get(source_id)
        if not note.strip():
            raise SourceTransitionError("A rejection note is required")
        updated = replace(source, review_status="rejected", review_notes=note.strip())
        self._sources[source_id] = updated
        return updated

    def expire(self, source_id: str, *, note: str = "Review is due") -> SourceRecord:
        source = self.get(source_id)
        updated = replace(source, review_status="expired", review_notes=note.strip() or "Review is due")
        self._sources[source_id] = updated
        return updated

    def withdraw(self, source_id: str, *, note: str) -> SourceRecord:
        source = self.get(source_id)
        if not note.strip():
            raise SourceTransitionError("A withdrawal note is required")
        updated = replace(source, withdrawn=True, review_notes=note.strip())
        self._sources[source_id] = updated
        return updated

    def governance_issues(self, source_id: str, *, as_of: date | None = None) -> tuple[str, ...]:
        source = self.get(source_id)
        check_date = as_of or date.today()
        issues: list[str] = []
        if source.review_status in {"restricted", "rejected", "expired"}:
            issues.append(f"review_status_{source.review_status}")
        if source.withdrawn:
            issues.append("source_withdrawn")
        if source.last_verification_date is None:
            issues.append("missing_last_verification_date")
        if source.next_review_date is None:
            issues.append("missing_next_review_date")
        elif source.next_review_date < check_date:
            issues.append("review_due")
        for action in (
            "public_accessibility",
            "linking",
            "downloading",
            "extraction",
            "internal_indexing",
            "reproduction",
        ):
            permission = source.permissions.status_for(action)
            if permission != "confirmed_permitted":
                issues.append(f"{action}_permission_{permission}")
        if any(source_id in pair for pair in self.metadata_conflicts()):
            issues.append("conflicting_source_metadata")
        return tuple(issues)

    def can_link(self, source_id: str, *, as_of: date | None = None) -> bool:
        return self.get(source_id).can_link(as_of=as_of)

    def can_index(self, source_id: str, *, as_of: date | None = None) -> bool:
        return self.get(source_id).can_index(as_of=as_of)

    def assert_indexing_allowed(self, source_id: str, *, as_of: date | None = None) -> None:
        source = self.get(source_id)
        if not source.can_index(as_of=as_of):
            issues = self.governance_issues(source_id, as_of=as_of)
            detail = ", ".join(issues) or f"status_{source.review_status}"
            raise SourceTransitionError(
                f"Source is not approved for internal indexing: {source_id} ({detail})"
            )

    def supports_capability(
        self,
        source_id: str,
        capability: SourceCapability,
        *,
        as_of: date | None = None,
    ) -> bool:
        """Return true only for an approved source that explicitly declares the capability."""

        source = self.get(source_id)
        return source.can_index(as_of=as_of) and source.supports_capability(capability)

    def assert_capability_allowed(
        self,
        source_id: str,
        capability: SourceCapability,
        *,
        as_of: date | None = None,
    ) -> None:
        if not self.supports_capability(source_id, capability, as_of=as_of):
            raise SourceTransitionError(
                f"Source is not approved for evidence capability: {capability}"
            )

    def metadata_conflicts(self) -> tuple[tuple[str, str], ...]:
        by_url: dict[str, list[SourceRecord]] = defaultdict(list)
        for source in self._sources.values():
            by_url[source.official_url].append(source)
        conflicts: list[tuple[str, str]] = []
        for records in by_url.values():
            for left_index, left in enumerate(records):
                for right in records[left_index + 1 :]:
                    left_identity = (
                        left.publisher,
                        left.jurisdiction,
                        left.applicable_market,
                        left.source_category,
                    )
                    right_identity = (
                        right.publisher,
                        right.jurisdiction,
                        right.applicable_market,
                        right.source_category,
                    )
                    if left_identity != right_identity:
                        conflicts.append((left.source_id, right.source_id))
        return tuple(conflicts)

    @staticmethod
    def _require_review_ready(
        source: SourceRecord,
        *,
        expected_status: str,
        reviewer: str,
    ) -> None:
        if source.review_status != expected_status:
            raise SourceTransitionError(
                f"Source must be {expected_status} before this approval transition"
            )
        if not reviewer.strip():
            raise SourceTransitionError("An identified reviewer is required")
        if source.last_verification_date is None:
            raise SourceTransitionError("A last verification date is required")
        if source.next_review_date is None:
            raise SourceTransitionError("A next review date is required")
        if source.is_due_for_review():
            raise SourceTransitionError("Source review is already due")
