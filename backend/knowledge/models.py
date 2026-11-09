"""Typed data models for the governed knowledge-base boundary.

The milestone 3G.1 models keep source identity, release identity, licence data,
and file/field approvals separate from free-form text. Legacy synthetic fixtures
remain supported by optional defaults, while release-scoped records are validated
strictly when they declare structured provenance.
"""

from dataclasses import dataclass
from datetime import date
import re
from typing import Literal


ReviewStatus = Literal["pending_review", "approved", "rejected", "retired"]
EvidenceStatus = Literal["sufficient", "insufficient", "conflicting"]
PermissionStatus = Literal[
    "confirmed_permitted",
    "restricted",
    "permission_required",
    "not_verified",
    "prohibited",
]
SourceReviewStatus = Literal[
    "draft",
    "pending_review",
    "approved_for_linking",
    "approved_for_indexing",
    "restricted",
    "rejected",
    "expired",
]
SourceAuthorityLevel = Literal["primary", "supplementary"]
SourceScope = Literal["national", "international"]
SourceCapability = Literal[
    "terminology_product_identity",
    "clinical_medication_evidence",
    "regulatory_product_status",
    "professional_practice_guidance",
    "public_health_policy",
]
ScopeStatus = Literal["approved", "rejected", "unresolved"]

_PERMISSION_STATUSES = frozenset(
    {
        "confirmed_permitted",
        "restricted",
        "permission_required",
        "not_verified",
        "prohibited",
    }
)
_SOURCE_REVIEW_STATUSES = frozenset(
    {
        "draft",
        "pending_review",
        "approved_for_linking",
        "approved_for_indexing",
        "restricted",
        "rejected",
        "expired",
    }
)
_SOURCE_CAPABILITIES = frozenset(
    {
        "terminology_product_identity",
        "clinical_medication_evidence",
        "regulatory_product_status",
        "professional_practice_guidance",
        "public_health_policy",
    }
)
_SCOPE_STATUSES = frozenset({"approved", "rejected", "unresolved"})
_SHA256_PATTERN = re.compile(r"^[0-9a-fA-F]{64}$")


@dataclass(frozen=True)
class SourcePermissions:
    """Separate permission decisions for each kind of source use."""

    public_accessibility: PermissionStatus = "not_verified"
    linking: PermissionStatus = "not_verified"
    downloading: PermissionStatus = "not_verified"
    extraction: PermissionStatus = "not_verified"
    internal_indexing: PermissionStatus = "not_verified"
    reproduction: PermissionStatus = "not_verified"

    def __post_init__(self) -> None:
        permissions = (
            self.public_accessibility,
            self.linking,
            self.downloading,
            self.extraction,
            self.internal_indexing,
            self.reproduction,
        )
        if any(permission not in _PERMISSION_STATUSES for permission in permissions):
            raise ValueError("All source permissions must use a supported permission status")

    def status_for(self, action: str) -> PermissionStatus:
        try:
            return getattr(self, action)
        except AttributeError as exc:
            raise ValueError(f"Unknown source permission action: {action}") from exc


@dataclass(frozen=True)
class SourceRecord:
    """Governed metadata for an information source, not the source contents."""

    source_id: str
    source_name: str
    publisher: str
    official_url: str
    source_category: str
    jurisdiction: str
    applicable_market: str
    scope_classification: SourceScope
    authoritative_for: tuple[str, ...]
    authority_limitations: tuple[str, ...]
    authority_level: SourceAuthorityLevel
    permissions: SourcePermissions
    publication_date: date | None = None
    last_verification_date: date | None = None
    next_review_date: date | None = None
    review_status: SourceReviewStatus = "draft"
    reviewer: str | None = None
    approval_date: date | None = None
    review_notes: str = ""
    withdrawn: bool = False
    evidence_capabilities: tuple[SourceCapability, ...] = ()

    def __post_init__(self) -> None:
        required = {
            "source_id": self.source_id,
            "source_name": self.source_name,
            "publisher": self.publisher,
            "official_url": self.official_url,
            "source_category": self.source_category,
            "jurisdiction": self.jurisdiction,
            "applicable_market": self.applicable_market,
        }
        if any(not value.strip() for value in required.values()):
            raise ValueError("Source identity, URL, category, and jurisdiction are required")
        if not self.official_url.startswith(("https://", "http://", "synthetic://")):
            raise ValueError("official_url must be an HTTP(S) or synthetic test URL")
        if not self.authoritative_for:
            raise ValueError("At least one authoritative information category is required")
        if self.scope_classification not in {"national", "international"}:
            raise ValueError("scope_classification must be national or international")
        if self.authority_level not in {"primary", "supplementary"}:
            raise ValueError("authority_level must be primary or supplementary")
        if self.review_status not in _SOURCE_REVIEW_STATUSES:
            raise ValueError("review_status is not a supported source workflow status")
        if any(capability not in _SOURCE_CAPABILITIES for capability in self.evidence_capabilities):
            raise ValueError("Source evidence capabilities must use supported values")
        if len(set(self.evidence_capabilities)) != len(self.evidence_capabilities):
            raise ValueError("Source evidence capabilities must be unique")
        if self.next_review_date and self.last_verification_date:
            if self.next_review_date < self.last_verification_date:
                raise ValueError("next_review_date cannot precede last_verification_date")
        if self.reviewer is not None and not self.reviewer.strip():
            raise ValueError("reviewer cannot be blank")

    def is_due_for_review(self, *, as_of: date | None = None) -> bool:
        check_date = as_of or date.today()
        return (
            self.last_verification_date is None
            or self.next_review_date is None
            or self.next_review_date < check_date
        )

    def can_link(self, *, as_of: date | None = None) -> bool:
        return (
            not self.withdrawn
            and self.review_status in {"approved_for_linking", "approved_for_indexing"}
            and self.permissions.linking == "confirmed_permitted"
            and not self.is_due_for_review(as_of=as_of)
        )

    def can_index(self, *, as_of: date | None = None) -> bool:
        return (
            not self.withdrawn
            and self.review_status == "approved_for_indexing"
            and self.permissions.extraction == "confirmed_permitted"
            and self.permissions.internal_indexing == "confirmed_permitted"
            and not self.is_due_for_review(as_of=as_of)
        )

    def supports_capability(self, capability: SourceCapability) -> bool:
        """Return whether this source explicitly declares a capability."""

        return capability in self.evidence_capabilities


@dataclass(frozen=True)
class SourceStatusSnapshot:
    """Immutable source-governance state captured with a release."""

    review_status: SourceReviewStatus
    withdrawn: bool
    last_verification_date: date
    next_review_date: date
    permissions: SourcePermissions

    def __post_init__(self) -> None:
        if self.review_status not in _SOURCE_REVIEW_STATUSES:
            raise ValueError("Source status snapshot has an unsupported review status")
        if self.next_review_date < self.last_verification_date:
            raise ValueError("Source status snapshot review dates are invalid")


@dataclass(frozen=True)
class FieldApproval:
    """Rights decision for one structured field in one source file."""

    field_id: str
    status: ScopeStatus

    def __post_init__(self) -> None:
        if not self.field_id.strip():
            raise ValueError("Field approval requires a field identifier")
        if self.status not in _SCOPE_STATUSES:
            raise ValueError("Field approval has an unsupported status")


@dataclass(frozen=True)
class FileApproval:
    """Rights decision and field decisions for one manifest file."""

    file_id: str
    status: ScopeStatus
    fields: tuple[FieldApproval, ...]

    def __post_init__(self) -> None:
        if not self.file_id.strip():
            raise ValueError("File approval requires a file identifier")
        if self.status not in _SCOPE_STATUSES:
            raise ValueError("File approval has an unsupported status")
        field_ids = [field.field_id for field in self.fields]
        if len(set(field_ids)) != len(field_ids):
            raise ValueError("File approval field identifiers must be unique")

    def field_status(self, field_id: str) -> ScopeStatus | None:
        for field in self.fields:
            if field.field_id == field_id:
                return field.status
        return None

    def allows(self, field_ids: tuple[str, ...]) -> bool:
        return (
            self.status == "approved"
            and bool(field_ids)
            and all(self.field_status(field_id) == "approved" for field_id in field_ids)
        )


@dataclass(frozen=True)
class ReleaseScopeApproval:
    """Exact release/file/field scope that an ingestion may use."""

    source_id: str
    dataset_name: str
    trud_item_number: int
    release_number: str
    release_week: int
    release_date: date
    archive_filename: str
    archive_sha256: str
    approved_capabilities: tuple[SourceCapability, ...]
    files: tuple[FileApproval, ...]

    def __post_init__(self) -> None:
        if not self.source_id.strip() or not self.dataset_name.strip():
            raise ValueError("Release scope requires source and dataset identity")
        if self.trud_item_number < 1 or self.release_week < 1:
            raise ValueError("TRUD item and release week must be positive")
        if not self.release_number.strip() or not self.archive_filename.strip():
            raise ValueError("Release scope requires release and archive identifiers")
        if not _SHA256_PATTERN.fullmatch(self.archive_sha256):
            raise ValueError("Release scope requires a 64-character SHA-256 checksum")
        if not self.approved_capabilities or any(
            capability not in _SOURCE_CAPABILITIES for capability in self.approved_capabilities
        ):
            raise ValueError("Release scope requires supported approved capabilities")
        if len(set(self.approved_capabilities)) != len(self.approved_capabilities):
            raise ValueError("Release scope capabilities must be unique")
        file_ids = [file.file_id for file in self.files]
        if not file_ids or len(set(file_ids)) != len(file_ids):
            raise ValueError("Release scope requires unique manifest files")

    def file(self, file_id: str) -> FileApproval:
        for file in self.files:
            if file.file_id == file_id:
                return file
        raise ValueError("File is not present in the release manifest")

    def matches(self, provenance: "ReleaseProvenance") -> bool:
        return (
            self.source_id == provenance.source_id
            and self.dataset_name == provenance.dataset_name
            and self.trud_item_number == provenance.trud_item_number
            and self.release_number == provenance.release_number
            and self.release_week == provenance.release_week
            and self.release_date == provenance.release_date
            and self.archive_filename == provenance.archive_filename
            and self.archive_sha256 == provenance.archive_sha256
            and provenance.source_capability in self.approved_capabilities
        )

    def allows(
        self,
        *,
        file_id: str,
        field_ids: tuple[str, ...],
        capability: SourceCapability,
    ) -> bool:
        if capability not in self.approved_capabilities:
            return False
        try:
            return self.file(file_id).allows(field_ids)
        except ValueError:
            return False


@dataclass(frozen=True)
class ReleaseProvenance:
    """Machine-readable identity and licence provenance for one exact release."""

    publisher: str
    dataset_name: str
    source_id: str
    source_capability: SourceCapability
    jurisdiction: str
    licence_name: str
    licence_url: str
    required_attribution: str
    trud_item_number: int
    release_number: str
    release_week: int
    release_date: date
    archive_filename: str
    archive_sha256: str
    acquisition_date: date
    verification_date: date
    source_status_snapshot: SourceStatusSnapshot
    manifest_file_ids: tuple[str, ...]
    approved_file_ids: tuple[str, ...]
    approved_field_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        required = {
            "publisher": self.publisher,
            "dataset_name": self.dataset_name,
            "source_id": self.source_id,
            "jurisdiction": self.jurisdiction,
            "licence_name": self.licence_name,
            "licence_url": self.licence_url,
            "required_attribution": self.required_attribution,
            "release_number": self.release_number,
            "archive_filename": self.archive_filename,
        }
        if any(not value.strip() for value in required.values()):
            raise ValueError("Release provenance identity and licence fields are required")
        if not self.licence_url.startswith(("https://", "http://", "synthetic://")):
            raise ValueError("Release licence URL must be an HTTP(S) or synthetic URL")
        if self.source_capability not in _SOURCE_CAPABILITIES:
            raise ValueError("Release provenance has an unsupported source capability")
        if self.trud_item_number < 1 or self.release_week < 1:
            raise ValueError("TRUD item and release week must be positive")
        if not _SHA256_PATTERN.fullmatch(self.archive_sha256):
            raise ValueError("Release provenance requires a 64-character SHA-256 checksum")
        if not self.manifest_file_ids:
            raise ValueError("Release provenance requires a manifest")
        if not set(self.approved_file_ids).issubset(self.manifest_file_ids):
            raise ValueError("Approved files must be present in the manifest")
        if not self.approved_file_ids or not self.approved_field_ids:
            raise ValueError("Release provenance requires approved files and fields")
        if len(set(self.manifest_file_ids)) != len(self.manifest_file_ids):
            raise ValueError("Manifest file identifiers must be unique")

    @property
    def identity(self) -> tuple[str, str, int, str, str]:
        """Stable identity used by release-scoped rollback."""

        return (
            self.source_id,
            self.release_number,
            self.trud_item_number,
            self.archive_filename,
            self.archive_sha256.lower(),
        )


@dataclass(frozen=True)
class DocumentMetadata:
    document_id: str
    title: str
    publisher: str
    publication_date: date | None
    version: str
    source_location: str
    acquired_at: date
    review_status: ReviewStatus = "pending_review"
    reviewer: str | None = None
    licensing_status: str = "pending_review"
    last_verification_date: date | None = None
    clinical_content: bool = False
    source_id: str | None = None
    source_capability: SourceCapability | None = None
    release_provenance: ReleaseProvenance | None = None
    scope_approval: ReleaseScopeApproval | None = None
    source_file_id: str | None = None
    source_field_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.review_status not in {"pending_review", "approved", "rejected", "retired"}:
            raise ValueError("Document review status is invalid")
        if self.release_provenance is None:
            if self.scope_approval is not None:
                raise ValueError("A scope approval requires release provenance")
            return
        provenance = self.release_provenance
        if self.source_id != provenance.source_id:
            raise ValueError("Document source_id must match release provenance")
        if self.source_capability != provenance.source_capability:
            raise ValueError("Document source capability must match release provenance")
        if self.scope_approval is None or not self.scope_approval.matches(provenance):
            raise ValueError("Document requires an exact matching release scope approval")
        if self.source_file_id is not None and not self.source_field_ids:
            raise ValueError("A document file identity requires approved field identities")
        if (
            self.source_file_id is not None
            and self.source_capability is not None
            and not self.scope_approval.allows(
            file_id=self.source_file_id,
            field_ids=self.source_field_ids,
            capability=self.source_capability,
            )
        ):
            raise ValueError("Document metadata is outside the approved release scope")


@dataclass(frozen=True)
class ApprovalChecklist:
    authenticity_verified: bool = False
    publisher_verified: bool = False
    relevance_assessed: bool = False
    currency_assessed: bool = False
    licensing_reviewed: bool = False
    content_quality_reviewed: bool = False
    pharmacist_approved: bool = False

    def complete_for(self, *, clinical_content: bool) -> bool:
        base_checks = (
            self.authenticity_verified,
            self.publisher_verified,
            self.relevance_assessed,
            self.currency_assessed,
            self.licensing_reviewed,
            self.content_quality_reviewed,
        )
        return all(base_checks) and (not clinical_content or self.pharmacist_approved)


@dataclass(frozen=True)
class DocumentSection:
    heading: str
    content: str
    source_reference: str | None = None
    claim_key: str | None = None
    conflict_group: str | None = None
    source_file_id: str | None = None
    source_field_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class DocumentPage:
    page_number: int
    sections: tuple[DocumentSection, ...]


@dataclass(frozen=True)
class DocumentPackage:
    metadata: DocumentMetadata
    pages: tuple[DocumentPage, ...]


@dataclass(frozen=True)
class Citation:
    publisher: str
    title: str
    version: str | None
    publication_date: date | None
    page_number: int | None
    section_heading: str | None
    source_location: str | None
    source_id: str | None = None
    document_id: str | None = None
    source_capability: SourceCapability | None = None
    source_file_id: str | None = None
    source_field_ids: tuple[str, ...] = ()
    release_provenance: ReleaseProvenance | None = None

    def render(self) -> str:
        edition = f", version {self.version}" if self.version else ""
        published = f", published {self.publication_date.isoformat()}" if self.publication_date else ""
        page = f", page {self.page_number}" if self.page_number is not None else ""
        section = f", section {self.section_heading}" if self.section_heading else ""
        source = f", source {self.source_id}" if self.source_id else ""
        location = f" — {self.source_location}" if self.source_location else ""
        release = (
            f", release {self.release_provenance.release_number}"
            f", file {self.source_file_id}"
            if self.release_provenance and self.source_file_id
            else ""
        )
        return f"{self.publisher}. {self.title}{edition}{published}{page}{section}{source}{release}{location}"


@dataclass(frozen=True)
class KnowledgeChunk:
    chunk_id: str
    document_id: str
    document_title: str
    publisher: str
    version: str
    section_heading: str
    page_number: int
    source_location: str
    source_reference: str | None
    content_hash: str
    text: str
    citation: Citation
    claim_key: str | None = None
    last_verification_date: date | None = None
    source_id: str | None = None
    conflict_group: str | None = None
    source_capability: SourceCapability | None = None
    source_file_id: str | None = None
    source_field_ids: tuple[str, ...] = ()
    release_provenance: ReleaseProvenance | None = None


@dataclass(frozen=True)
class EvidencePassage:
    chunk: KnowledgeChunk
    relevance_score: float

    @property
    def citation(self) -> Citation:
        return self.chunk.citation


@dataclass(frozen=True)
class EvidenceBundle:
    query: str
    status: EvidenceStatus
    passages: tuple[EvidencePassage, ...] = ()
    abstention_reason: str | None = None
    required_capability: SourceCapability | None = None

    @property
    def is_sufficient(self) -> bool:
        return self.status == "sufficient" and bool(self.passages)

    @classmethod
    def abstain(
        cls,
        query: str,
        reason: str,
        *,
        required_capability: SourceCapability | None = None,
    ) -> "EvidenceBundle":
        return cls(
            query=query,
            status="insufficient",
            abstention_reason=reason,
            required_capability=required_capability,
        )

    def prompt_context(self) -> str:
        if not self.is_sufficient:
            raise ValueError("A sufficient evidence bundle is required for model context")
        lines = [
            "Approved evidence only. Use the evidence below for factual claims.",
            "If the evidence does not answer the question, abstain instead of guessing.",
        ]
        if self.required_capability:
            lines.append(f"Required evidence capability: {self.required_capability}")
        for index, passage in enumerate(self.passages, start=1):
            lines.append(f"Evidence {index}: {passage.chunk.text}")
            lines.append(f"Source {index}: {passage.citation.render()}")
        return "\n".join(lines)
