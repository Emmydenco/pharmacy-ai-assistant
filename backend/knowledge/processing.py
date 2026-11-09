"""Structured document ingestion and processing without web scraping."""

from dataclasses import dataclass
import hashlib

from backend.knowledge.models import Citation, DocumentPackage, KnowledgeChunk, ReleaseProvenance
from backend.knowledge.registry import DocumentRegistry
from backend.knowledge.validation import IngestionMode, IngestionPolicy, IngestionPolicyError


class IngestionRejectedError(ValueError):
    """Raised when a package fails approval or structural validation."""


@dataclass(frozen=True)
class ProcessedDocument:
    document_id: str
    version: str
    chunks: tuple[KnowledgeChunk, ...]
    release_provenance: ReleaseProvenance | None = None


class DocumentProcessor:
    """Turn structured pages into chunks while retaining all source coordinates."""

    def __init__(
        self,
        registry: DocumentRegistry,
        *,
        max_chunk_characters: int = 1_200,
        mode: IngestionMode = "clinical",
    ) -> None:
        self.registry = registry
        self.policy = IngestionPolicy(mode=mode)
        if max_chunk_characters < 100:
            raise ValueError("max_chunk_characters must be at least 100")
        self.max_chunk_characters = max_chunk_characters

    def process(self, package: DocumentPackage) -> ProcessedDocument:
        registered = self.registry.get(
            package.metadata.document_id, package.metadata.version
        )
        if registered != package.metadata or registered.review_status != "approved":
            raise IngestionRejectedError("Only approved documents may be processed")
        if registered.last_verification_date is None:
            raise IngestionRejectedError("Approved documents require a verification date")
        try:
            self.policy.validate_document(
                registered,
                source_registry=self.registry.source_registry,
            )
        except IngestionPolicyError as exc:
            raise IngestionRejectedError(str(exc)) from exc
        if not package.pages:
            raise IngestionRejectedError("Document has no pages")
        page_numbers = [page.page_number for page in package.pages]
        if any(number < 1 for number in page_numbers) or len(set(page_numbers)) != len(page_numbers):
            raise IngestionRejectedError("Document pages must have unique positive page numbers")

        chunks: list[KnowledgeChunk] = []
        seen_sections: set[tuple[int, str, str]] = set()
        for page in sorted(package.pages, key=lambda item: item.page_number):
            if not page.sections:
                raise IngestionRejectedError("Document contains a page without sections")
            for section_index, section in enumerate(page.sections):
                heading = " ".join(section.heading.split())
                content = " ".join(section.content.split())
                if not heading or not content:
                    raise IngestionRejectedError("Document sections require headings and content")
                section_key = (page.page_number, heading, content)
                if section_key in seen_sections:
                    raise IngestionRejectedError("Document contains duplicate sections")
                seen_sections.add(section_key)
                if package.metadata.release_provenance is not None:
                    if package.metadata.scope_approval is None:
                        raise IngestionRejectedError(
                            "Release-scoped documents require an exact scope approval"
                        )
                    if not section.source_file_id or not section.source_field_ids:
                        raise IngestionRejectedError(
                            "Release-scoped sections require file and field provenance"
                        )
                    if package.metadata.source_capability is None or not package.metadata.scope_approval.allows(
                        file_id=section.source_file_id,
                        field_ids=section.source_field_ids,
                        capability=package.metadata.source_capability,
                    ):
                        raise IngestionRejectedError(
                            "Section is outside the approved release file/field scope"
                        )
                citation = Citation(
                    publisher=package.metadata.publisher,
                    title=package.metadata.title,
                    version=package.metadata.version,
                    publication_date=package.metadata.publication_date,
                    page_number=page.page_number,
                    section_heading=heading,
                    source_location=section.source_reference or package.metadata.source_location,
                    source_id=package.metadata.source_id,
                    document_id=package.metadata.document_id,
                    source_capability=package.metadata.source_capability,
                    source_file_id=section.source_file_id,
                    source_field_ids=section.source_field_ids,
                    release_provenance=package.metadata.release_provenance,
                )
                for part_index, text in enumerate(self._split(content), start=1):
                    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
                    chunk_id = (
                        f"{package.metadata.document_id}:{package.metadata.version}:"
                        f"{page.page_number}:{section_index}:{part_index}"
                    )
                    chunks.append(
                        KnowledgeChunk(
                            chunk_id=chunk_id,
                            document_id=package.metadata.document_id,
                            document_title=package.metadata.title,
                            publisher=package.metadata.publisher,
                            version=package.metadata.version,
                            section_heading=heading,
                            page_number=page.page_number,
                            source_location=package.metadata.source_location,
                            source_reference=section.source_reference,
                            content_hash=digest,
                            text=text,
                            citation=citation,
                            claim_key=section.claim_key,
                            last_verification_date=package.metadata.last_verification_date,
                            source_id=package.metadata.source_id,
                            conflict_group=section.conflict_group,
                            source_capability=package.metadata.source_capability,
                            source_file_id=section.source_file_id,
                            source_field_ids=section.source_field_ids,
                            release_provenance=package.metadata.release_provenance,
                        )
                    )
        return ProcessedDocument(
            document_id=package.metadata.document_id,
            version=package.metadata.version,
            chunks=tuple(chunks),
            release_provenance=package.metadata.release_provenance,
        )

    def _split(self, content: str) -> tuple[str, ...]:
        if len(content) <= self.max_chunk_characters:
            return (content,)
        words = content.split()
        parts: list[str] = []
        current: list[str] = []
        current_length = 0
        for word in words:
            proposed = current_length + len(word) + (1 if current else 0)
            if current and proposed > self.max_chunk_characters:
                parts.append(" ".join(current))
                current = []
                current_length = 0
            current.append(word)
            current_length += len(word) + (1 if len(current) > 1 else 0)
        if current:
            parts.append(" ".join(current))
        return tuple(parts)


class ApprovedDocumentIngestor:
    """Accept only document packages whose exact version and source are approved."""

    def __init__(self, registry: DocumentRegistry) -> None:
        self.registry = registry
        self.processor = DocumentProcessor(registry, mode="clinical")

    @classmethod
    def clinical(cls, registry: DocumentRegistry) -> "ApprovedDocumentIngestor":
        """Create the explicit future-clinical ingestion boundary."""
        return cls(registry)

    def ingest(self, package: DocumentPackage) -> ProcessedDocument:
        registered = self.registry.get(package.metadata.document_id, package.metadata.version)
        if registered != package.metadata:
            raise IngestionRejectedError("Package metadata does not match the registered source")
        if registered.review_status != "approved":
            raise IngestionRejectedError("Only approved documents may be ingested")
        if registered.last_verification_date is None:
            raise IngestionRejectedError("Approved documents require a verification date")
        return self.processor.process(package)
