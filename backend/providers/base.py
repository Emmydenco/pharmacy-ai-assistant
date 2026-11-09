"""Provider interface and non-bypassable application boundary."""

from dataclasses import dataclass
from typing import Literal, Protocol

from backend.answers import StructuredAnswer
from backend.knowledge.models import EvidenceBundle
from backend.knowledge.registry import DocumentRegistry
from backend.knowledge.validation import (
    AnswerValidationError,
    EvidenceValidationError,
    validate_evidence_bundle,
    validate_structured_answer,
)
from backend.schemas import HistoryMessage, SourceReference


DiagnosticCategory = Literal[
    "auth",
    "endpoint_or_model",
    "rate_limit",
    "timeout",
    "network",
    "server",
    "response",
    "unknown",
]


@dataclass(frozen=True)
class ProviderDiagnostic:
    """Safe metadata suitable for structured logs; never contains request content."""

    provider: str
    category: DiagnosticCategory
    http_status: int | None = None
    cloudflare_error_code: int | str | None = None


class ProviderError(Exception):
    """Base class for safe, user-facing provider failures."""

    def __init__(
        self, message: str, *, diagnostic: ProviderDiagnostic | None = None
    ) -> None:
        super().__init__(message)
        self.diagnostic = diagnostic


class ProviderConfigurationError(ProviderError):
    """Raised when the selected provider is not configured."""


class ProviderResultValidationError(ProviderError):
    """Raised when a provider returns a malformed or unsafe result."""


@dataclass(frozen=True)
class ProviderResult:
    text: str
    simulated: bool
    source: SourceReference | None = None
    answer: StructuredAnswer | None = None


class Provider(Protocol):
    async def generate(
        self,
        message: str,
        history: list[HistoryMessage],
        evidence: EvidenceBundle,
    ) -> ProviderResult:
        """Generate one result for the central boundary to validate."""


class GovernedProvider:
    """Non-bypassable application boundary around a provider implementation."""

    def __init__(self, provider: Provider, registry: DocumentRegistry) -> None:
        self.provider = provider
        self.registry = registry

    async def generate(
        self,
        message: str,
        history: list[HistoryMessage],
        evidence: EvidenceBundle,
    ) -> ProviderResult:
        evidence_validator = _evidence_validator(self.registry)
        validated_evidence = evidence_validator.validate(evidence)
        result = await self.provider.generate(message, history, validated_evidence)
        return _validate_provider_result(
            result,
            validated_evidence,
            registry=self.registry,
            evidence_validator=evidence_validator,
        )


def ensure_governed_provider(
    provider: Provider,
    registry: DocumentRegistry,
) -> GovernedProvider:
    """Wrap a provider exactly once before it enters the application path."""

    if isinstance(provider, GovernedProvider):
        return provider
    return GovernedProvider(provider, registry)


def _evidence_validator(registry: DocumentRegistry):
    from backend.knowledge.validation import EvidenceValidator

    return EvidenceValidator(registry=registry)


def _validate_provider_result(
    result: ProviderResult,
    evidence: EvidenceBundle,
    *,
    registry: DocumentRegistry,
    evidence_validator,
) -> ProviderResult:
    if not isinstance(result, ProviderResult):
        raise ProviderResultValidationError("The provider returned an invalid result")
    if not isinstance(result.text, str) or not result.text.strip():
        raise ProviderResultValidationError("The provider returned empty answer text")
    if not isinstance(result.simulated, bool):
        raise ProviderResultValidationError("The provider returned invalid simulation metadata")

    answer = result.answer or StructuredAnswer(conversational_text=result.text.strip())
    if answer.conversational_text.strip() != result.text.strip():
        raise ProviderResultValidationError("Answer text and structured text do not match")
    try:
        validate_structured_answer(
            answer,
            evidence,
            evidence_validator=evidence_validator,
        )
        # Re-run governance after the underlying provider returns. A source may have
        # been withdrawn, restricted, expired, or become due while it was running.
        validate_evidence_bundle(evidence, registry=registry)
    except (AnswerValidationError, EvidenceValidationError) as exc:
        raise ProviderResultValidationError("Generated answer failed validation") from exc
    return ProviderResult(
        text=answer.conversational_text.strip(),
        simulated=result.simulated,
        source=result.source,
        answer=answer,
    )
