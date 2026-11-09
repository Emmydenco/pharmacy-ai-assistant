"""Cloudflare Workers AI REST adapter for non-streaming text generation.

The selected model's current documentation shows the account-qualified REST
endpoint, Bearer authentication, a ``messages`` request, and a synchronous
``result.response`` output. Streaming and structured output are intentionally
not assumed here. See the official model page at
https://developers.cloudflare.com/workers-ai/models/llama-3.2-3b-instruct/.
"""

import re

import httpx

from backend.config import Settings
from backend.knowledge.models import EvidenceBundle
from backend.knowledge.registry import DocumentRegistry
from backend.knowledge.validation import validate_evidence_bundle
from backend.providers.base import (
    DiagnosticCategory,
    ProviderConfigurationError,
    ProviderDiagnostic,
    ProviderError,
    ProviderResult,
)
from backend.schemas import HistoryMessage


SYSTEM_INSTRUCTIONS = (
    "You are a limited pharmacy information prototype. Provide general, unverified "
    "educational medication information only. Provide general, non-diagnostic "
    "medication information only. Do not diagnose, prescribe, recommend starting or "
    "stopping a prescription, change a dose, or make a patient-specific treatment "
    "decision. If the question needs personal clinical judgement, tell the user to speak "
    "with a licensed pharmacist. Use only the approved evidence and source metadata supplied "
    "in the request. Do not invent citations or claim support beyond that evidence. Mention "
    "uncertainty when it matters."
)

SAFE_ERROR_CODE = re.compile(r"^[0-9]{1,12}$")


def _safe_error_code(payload: object) -> int | str | None:
    """Extract only a bounded numeric Cloudflare error code for diagnostics."""

    if not isinstance(payload, dict) or not isinstance(payload.get("errors"), list):
        return None
    for error in payload["errors"]:
        if not isinstance(error, dict):
            continue
        code = error.get("code")
        if isinstance(code, int) and not isinstance(code, bool) and 0 <= code <= 2**31 - 1:
            return code
        if isinstance(code, str) and SAFE_ERROR_CODE.fullmatch(code):
            return code
    return None


def _response_error_code(response: httpx.Response) -> int | str | None:
    try:
        return _safe_error_code(response.json())
    except ValueError:
        return None


def _provider_error(
    message: str,
    category: DiagnosticCategory,
    *,
    http_status: int | None = None,
    cloudflare_error_code: int | str | None = None,
) -> ProviderError:
    return ProviderError(
        message,
        diagnostic=ProviderDiagnostic(
            provider="cloudflare",
            category=category,
            http_status=http_status,
            cloudflare_error_code=cloudflare_error_code,
        ),
    )


class CloudflareProvider:
    def __init__(self, settings: Settings, registry: DocumentRegistry | None = None):
        self.settings = settings
        self.registry = registry

    def _messages(
        self,
        message: str,
        history: list[HistoryMessage],
        evidence: EvidenceBundle,
    ) -> list[dict[str, str]]:
        messages = [
            {"role": "system", "content": SYSTEM_INSTRUCTIONS},
            {"role": "system", "content": evidence.prompt_context()},
        ]
        messages.extend(
            {"role": item.role, "content": item.content} for item in history[-6:]
        )
        messages.append({"role": "user", "content": message})
        return messages

    async def generate(
        self,
        message: str,
        history: list[HistoryMessage],
        evidence: EvidenceBundle,
    ) -> ProviderResult:
        if not self.settings.cloudflare_configured:
            raise ProviderConfigurationError(
                "Cloudflare credentials are missing; configure them or use LLM_PROVIDER=mock."
            )
        validate_evidence_bundle(evidence, registry=self.registry)

        endpoint = (
            "https://api.cloudflare.com/client/v4/accounts/"
            f"{self.settings.cloudflare_account_id}/ai/run/{self.settings.cloudflare_model}"
        )
        headers = {
            "Authorization": f"Bearer {self.settings.cloudflare_api_token}",
            "Content-Type": "application/json",
        }
        try:
            async with httpx.AsyncClient(
                timeout=self.settings.provider_timeout_seconds
            ) as client:
                response = await client.post(
                    endpoint,
                    headers=headers,
                    json={
                        "messages": self._messages(message, history, evidence),
                        "max_tokens": self.settings.max_output_tokens,
                    },
                )
                response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            status_code = exc.response.status_code
            error_code = _response_error_code(exc.response)
            if status_code in (401, 403):
                raise _provider_error(
                    "The hosted provider rejected its credentials.",
                    "auth",
                    http_status=status_code,
                    cloudflare_error_code=error_code,
                ) from exc
            if status_code == 404:
                raise _provider_error(
                    "The hosted model was not found or is unavailable.",
                    "endpoint_or_model",
                    http_status=status_code,
                    cloudflare_error_code=error_code,
                ) from exc
            if status_code == 429:
                raise _provider_error(
                    "The hosted provider rate limit was reached.",
                    "rate_limit",
                    http_status=status_code,
                    cloudflare_error_code=error_code,
                ) from exc
            if status_code >= 500:
                raise _provider_error(
                    "The hosted provider is temporarily unavailable.",
                    "server",
                    http_status=status_code,
                    cloudflare_error_code=error_code,
                ) from exc
            raise _provider_error(
                "The hosted provider rejected this request.",
                "unknown",
                http_status=status_code,
                cloudflare_error_code=error_code,
            ) from exc
        except httpx.TimeoutException as exc:
            raise _provider_error("The hosted provider timed out.", "timeout") from exc
        except httpx.RequestError as exc:
            raise _provider_error(
                "The hosted provider could not be reached.", "network"
            ) from exc

        try:
            payload = response.json()
        except ValueError as exc:
            raise _provider_error(
                "The hosted provider returned an invalid response.", "response"
            ) from exc

        if not isinstance(payload, dict) or payload.get("success") is not True:
            raise _provider_error(
                "The hosted provider reported an error.",
                "response",
                cloudflare_error_code=_safe_error_code(payload),
            )
        result = payload.get("result")
        if not isinstance(result, dict):
            raise _provider_error(
                "The hosted provider returned an unexpected response.",
                "response",
                cloudflare_error_code=_safe_error_code(payload),
            )
        text = result.get("response")
        if not isinstance(text, str) or not text.strip():
            raise _provider_error(
                "The hosted provider returned no text response.",
                "response",
                cloudflare_error_code=_safe_error_code(payload),
            )
        return ProviderResult(text=text.strip(), simulated=False)
