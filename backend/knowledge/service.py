"""Application-facing knowledge service with a safe empty default."""

from dataclasses import dataclass

from backend.knowledge.models import EvidenceBundle
from backend.knowledge.registry import DocumentRegistry
from backend.knowledge.retrieval import InMemoryKnowledgeIndex


@dataclass(frozen=True)
class KnowledgeDecision:
    evidence: EvidenceBundle

    @property
    def can_answer(self) -> bool:
        return self.evidence.is_sufficient

    @property
    def message(self) -> str:
        if self.can_answer:
            return ""
        return (
            "I do not have enough approved, current evidence to answer that safely. "
            "Please consult a licensed pharmacist or another qualified healthcare professional."
        )


class KnowledgeService:
    """Coordinates the registry-backed retrieval boundary without persistence."""

    def __init__(self, index: InMemoryKnowledgeIndex, registry: DocumentRegistry) -> None:
        self.index = index
        self.registry = registry

    @classmethod
    def empty(cls) -> "KnowledgeService":
        registry = DocumentRegistry()
        return cls(index=InMemoryKnowledgeIndex(registry), registry=registry)

    def assess(self, question: str) -> KnowledgeDecision:
        return KnowledgeDecision(self.index.retrieve(question))
