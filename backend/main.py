"""FastAPI entry point for the governed Milestone 3B prototype."""

from pathlib import Path
import logging

from fastapi import FastAPI
from fastapi.responses import FileResponse

from backend.config import Settings, get_settings
from backend.knowledge.service import KnowledgeService
from backend.knowledge.validation import AnswerValidationError, EvidenceValidationError
from backend.policy import evaluate_message
from backend.providers.base import (
    GovernedProvider,
    Provider,
    ProviderConfigurationError,
    ProviderDiagnostic,
    ProviderError,
    ProviderResultValidationError,
    ensure_governed_provider,
)
from backend.providers.cloudflare import CloudflareProvider
from backend.providers.mock import MockProvider
from backend.schemas import ChatRequest, ChatResponse


ROOT = Path(__file__).resolve().parents[1]
logger = logging.getLogger("pharmacy_assistant")

DISCLAIMER = (
    "Prototype only: general information, not a substitute for a pharmacist. "
    "No real patient data should be entered."
)

app = FastAPI(
    title="Pharmacy Patient Assistant — Milestone 3B",
    version="0.3.0",
    description="A governed retrieval skeleton with explicit safety and abstention boundaries.",
)


# Runtime starts empty. Tests may inject synthetic approved content explicitly; no
# clinical or medication documents are seeded into the application.
knowledge_service = KnowledgeService.empty()


@app.get("/", include_in_schema=False)
async def landing_page() -> FileResponse:
    return FileResponse(ROOT / "index.html")


@app.get("/prototype", include_in_schema=False)
async def prototype_page() -> FileResponse:
    return FileResponse(ROOT / "prototype.html")


@app.get("/health")
async def health() -> dict[str, object]:
    settings = get_settings()
    return {
        "status": "ok",
        "provider_mode": settings.provider_mode,
        "provider_configured": (
            settings.cloudflare_configured
            if settings.provider_mode == "cloudflare"
            else settings.provider_mode == "mock"
        ),
    }


@app.get("/manus-routes.json", include_in_schema=False)
async def route_manifest() -> FileResponse:
    return FileResponse(ROOT / "manus-routes.json", media_type="application/json")


for _asset in ("styles.css", "script.js", "prototype.css", "prototype.js", "logo.svg"):
    _route = f"/{_asset}"

    async def _serve_asset(asset: str = _asset) -> FileResponse:
        return FileResponse(ROOT / asset)

    app.get(_route, include_in_schema=False)(_serve_asset)


def build_provider(settings: Settings) -> GovernedProvider:
    if settings.provider_mode == "mock":
        return ensure_governed_provider(
            MockProvider(knowledge_service.registry), knowledge_service.registry
        )
    if settings.provider_mode == "cloudflare":
        return ensure_governed_provider(
            CloudflareProvider(settings, knowledge_service.registry),
            knowledge_service.registry,
        )
    raise ProviderConfigurationError(
        "APP_MODE must be either 'mock' or 'cloudflare'."
    )


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    settings = get_settings()
    decision = evaluate_message(request.message)
    if decision.category != "allowed":
        return ChatResponse(
            status="blocked",
            message=decision.message,
            category=decision.category,
            simulated=True,
            provider="policy",
            disclaimer=DISCLAIMER,
        )

    evidence_decision = knowledge_service.assess(request.message)
    if not evidence_decision.can_answer:
        return ChatResponse(
            status="blocked",
            message=evidence_decision.message,
            category="knowledge_abstention",
            simulated=True,
            provider="knowledge_base",
            disclaimer=DISCLAIMER,
        )

    try:
        provider = ensure_governed_provider(
            build_provider(settings), knowledge_service.registry
        )
        result = await provider.generate(
            request.message, request.history, evidence_decision.evidence
        )
    except ProviderConfigurationError:
        logger.warning("provider_configuration_error mode=%s", settings.provider_mode)
        return ChatResponse(
            status="error",
            message=(
                "Hosted inference is not configured. Set the required server-side "
                    "credentials, or use LLM_PROVIDER=mock for local interface testing."
            ),
            category="provider_configuration",
            simulated=False,
            provider=settings.provider_mode,
            disclaimer=DISCLAIMER,
        )
    except (
        AnswerValidationError,
        EvidenceValidationError,
        ProviderResultValidationError,
    ):
        logger.warning("evidence_validation_failed provider=%s", settings.provider_mode)
        return ChatResponse(
            status="blocked",
            message=(
                "I could not verify the evidence needed to answer safely. "
                "Please consult a licensed pharmacist."
            ),
            category="knowledge_abstention",
            simulated=True,
            provider="knowledge_base",
            disclaimer=DISCLAIMER,
        )
    except ProviderError as exc:
        diagnostic = exc.diagnostic or ProviderDiagnostic(
            provider=settings.provider_mode,
            category="unknown",
        )
        logger.warning(
            "provider_error provider=%s category=%s http_status=%s cloudflare_error_code=%s",
            diagnostic.provider,
            diagnostic.category,
            diagnostic.http_status,
            diagnostic.cloudflare_error_code,
        )
        return ChatResponse(
            status="error",
            message=(
                "The hosted provider could not answer. No medication information was "
                "invented. Check the provider configuration or try again later."
            ),
            category="provider_error",
            simulated=False,
            provider=settings.provider_mode,
            disclaimer=DISCLAIMER,
        )

    return ChatResponse(
        status="ok",
        message=result.text,
        category="allowed",
        simulated=result.simulated,
        provider=settings.provider_mode,
        source=result.source,
        disclaimer=DISCLAIMER,
    )
