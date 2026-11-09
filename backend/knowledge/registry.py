"""In-memory document registry with explicit approval governance."""

from dataclasses import replace
from datetime import date

from backend.knowledge.models import ApprovalChecklist, DocumentMetadata
from backend.knowledge.source_registry import SourceRegistry, SourceRegistryError


class RegistryError(ValueError):
    """Base error for invalid registry operations."""


class DuplicateDocumentError(RegistryError):
    """Raised when the same document version is registered twice."""


class DocumentNotFoundError(RegistryError):
    """Raised when a requested document version is absent."""


class ApprovalRejectedError(RegistryError):
    """Raised when the governance checklist is incomplete."""


class DocumentRegistry:
    """Small in-memory registry suitable for tests and a future storage adapter."""

    def __init__(self, *, source_registry: SourceRegistry | None = None) -> None:
        self._documents: dict[tuple[str, str], DocumentMetadata] = {}
        self.source_registry = source_registry

    def register(self, metadata: DocumentMetadata) -> DocumentMetadata:
        required = {
            "document_id": metadata.document_id,
            "title": metadata.title,
            "publisher": metadata.publisher,
            "version": metadata.version,
            "source_location": metadata.source_location,
            "licensing_status": metadata.licensing_status,
        }
        if any(not value.strip() for value in required.values()):
            raise RegistryError("Document identity and licensing metadata are required")
        if metadata.review_status != "pending_review":
            raise RegistryError("New registry records must start in pending_review")
        if metadata.source_id is not None:
            if self.source_registry is None:
                raise RegistryError("A source registry is required for source-linked documents")
            try:
                self.source_registry.assert_indexing_allowed(metadata.source_id)
            except SourceRegistryError as exc:
                raise RegistryError(
                    "Source is not approved for internal indexing"
                ) from exc
            if metadata.source_capability is not None:
                try:
                    self.source_registry.assert_capability_allowed(
                        metadata.source_id,
                        metadata.source_capability,
                    )
                except SourceRegistryError as exc:
                    raise RegistryError(
                        "Source is not approved for the declared evidence capability"
                    ) from exc
        key = (metadata.document_id, metadata.version)
        if key in self._documents:
            raise DuplicateDocumentError(
                f"Document version already registered: {metadata.document_id}/{metadata.version}"
            )
        self._documents[key] = metadata
        return metadata

    def get(self, document_id: str, version: str) -> DocumentMetadata:
        try:
            return self._documents[(document_id, version)]
        except KeyError as exc:
            raise DocumentNotFoundError(f"Document version not found: {document_id}/{version}") from exc

    def approve(
        self,
        document_id: str,
        version: str,
        checklist: ApprovalChecklist,
        *,
        reviewer: str,
    ) -> DocumentMetadata:
        metadata = self.get(document_id, version)
        if metadata.review_status != "pending_review":
            raise ApprovalRejectedError("Only pending-review documents may be approved")
        if not reviewer.strip():
            raise ApprovalRejectedError("An identified reviewer is required")
        if not checklist.complete_for(clinical_content=metadata.clinical_content):
            raise ApprovalRejectedError("The source-governance checklist is incomplete")
        approved = replace(
            metadata,
            review_status="approved",
            reviewer=reviewer.strip(),
            last_verification_date=metadata.last_verification_date or date.today(),
        )
        self._documents[(document_id, version)] = approved
        return approved

    def all_documents(self) -> tuple[DocumentMetadata, ...]:
        return tuple(self._documents.values())

    def is_approved(self, document_id: str, version: str) -> bool:
        return self.get(document_id, version).review_status == "approved"
