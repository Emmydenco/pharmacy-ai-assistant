"""A clearly labelled, no-network provider for interface testing."""

from backend.knowledge.models import EvidenceBundle
from backend.knowledge.registry import DocumentRegistry
from backend.knowledge.validation import validate_evidence_bundle
from backend.providers.base import ProviderResult
from backend.schemas import HistoryMessage


class MockProvider:
    """Return predetermined demo text without pretending to use a knowledge base."""

    def __init__(self, registry: DocumentRegistry | None = None) -> None:
        self.registry = registry

    async def generate(
        self,
        message: str,
        history: list[HistoryMessage],
        evidence: EvidenceBundle,
    ) -> ProviderResult:
        del history
        validate_evidence_bundle(evidence, registry=self.registry)
        lowered = message.lower()
        if "side effect" in lowered:
            text = (
                "[SIMULATED MOCK RESPONSE] This demonstration does not look up a real "
                "medicine or knowledge base. In a later milestone, side-effect information "
                "would need to come from an approved, versioned source and would still be "
                "reviewed by a pharmacist."
            )
        elif any(word in lowered for word in ("take", "use", "medicine", "medication")):
            text = (
                "[SIMULATED MOCK RESPONSE] This is a predetermined demonstration answer. "
                "The prototype is not consulting a medication database, so please do not "
                "use this text to make a treatment decision. A later milestone will add "
                "retrieved, cited medication information."
            )
        else:
            text = (
                "[SIMULATED MOCK RESPONSE] Mock mode is active and no external service or "
                "real medication source was consulted. Try a general medication-use or "
                "side-effect question to exercise the demo interface."
            )
        return ProviderResult(text=text, simulated=True)
