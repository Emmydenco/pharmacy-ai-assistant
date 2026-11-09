import asyncio
from pathlib import Path

import httpx
import pytest
from fastapi.testclient import TestClient

import backend.main as main
import backend.providers.cloudflare as cloudflare
from backend.config import get_settings
from backend.knowledge.models import EvidenceBundle
from backend.main import app
from backend.providers.base import (
    ProviderConfigurationError,
    ProviderDiagnostic,
    ProviderError,
)
from backend.schemas import HistoryMessage
from tests.helpers import synthetic_evidence, synthetic_service


client = TestClient(app)
TEST_EVIDENCE = synthetic_evidence()


@pytest.fixture(autouse=True)
def clear_provider_environment(monkeypatch):
    for name in (
        "LLM_PROVIDER",
        "APP_MODE",
        "LLM_MODEL",
        "CLOUDFLARE_MODEL",
        "CLOUDFLARE_ACCOUNT_ID",
        "CLOUDFLARE_API_TOKEN",
        "LLM_TIMEOUT_SECONDS",
        "PROVIDER_TIMEOUT_SECONDS",
        "LLM_MAX_OUTPUT_TOKENS",
    ):
        monkeypatch.delenv(name, raising=False)


class StubResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


class CaptureClient:
    def __init__(self, response):
        self.response = response
        self.timeout = None
        self.endpoint = None
        self.headers = None
        self.payload = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        return False

    async def post(self, endpoint, headers, json):
        self.endpoint = endpoint
        self.headers = headers
        self.payload = json
        return self.response


def configure_cloudflare(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "cloudflare")
    monkeypatch.setenv("CLOUDFLARE_ACCOUNT_ID", "test-account")
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "test-token")


def test_provider_settings_use_requested_names_and_safe_defaults(monkeypatch):
    settings = get_settings()
    assert settings.provider_mode == "mock"
    assert settings.cloudflare_model == "@cf/meta/llama-3.2-3b-instruct"
    assert settings.provider_timeout_seconds == 20
    assert settings.max_output_tokens == 500

    monkeypatch.setenv("LLM_PROVIDER", "cloudflare")
    monkeypatch.setenv("LLM_MODEL", "custom-model")
    monkeypatch.setenv("LLM_TIMEOUT_SECONDS", "7.5")
    monkeypatch.setenv("LLM_MAX_OUTPUT_TOKENS", "321")
    settings = get_settings()
    assert settings.provider_mode == "cloudflare"
    assert settings.cloudflare_model == "custom-model"
    assert settings.provider_timeout_seconds == 7.5
    assert settings.max_output_tokens == 321


def test_cloudflare_request_construction_and_auth(monkeypatch):
    configure_cloudflare(monkeypatch)
    capture = CaptureClient(StubResponse({"success": True, "result": {"response": "General information."}}))
    monkeypatch.setattr(cloudflare.httpx, "AsyncClient", lambda timeout: capture)
    monkeypatch.setenv("LLM_TIMEOUT_SECONDS", "9")
    monkeypatch.setenv("LLM_MAX_OUTPUT_TOKENS", "123")

    result = asyncio.run(
        cloudflare.CloudflareProvider(get_settings()).generate(
            "What is a medicine?",
            [HistoryMessage(role="user", content="Hello")],
            TEST_EVIDENCE,
        )
    )

    assert result.text == "General information."
    assert result.simulated is False
    assert capture.endpoint == (
        "https://api.cloudflare.com/client/v4/accounts/"
        "test-account/ai/run/@cf/meta/llama-3.2-3b-instruct"
    )
    assert capture.headers == {
        "Authorization": "Bearer test-token",
        "Content-Type": "application/json",
    }
    assert capture.payload["max_tokens"] == 123
    assert capture.payload["messages"][0]["role"] == "system"
    assert "Approved evidence only" in capture.payload["messages"][1]["content"]
    assert "Synthetic Test Publisher" in capture.payload["messages"][1]["content"]
    assert capture.payload["messages"][-1] == {
        "role": "user",
        "content": "What is a medicine?",
    }


def test_cloudflare_success_response_is_parsed(monkeypatch):
    configure_cloudflare(monkeypatch)
    capture = CaptureClient(StubResponse({"success": True, "result": {"response": "  Answer  "}}))
    monkeypatch.setattr(cloudflare.httpx, "AsyncClient", lambda timeout: capture)

    result = asyncio.run(
        cloudflare.CloudflareProvider(get_settings()).generate("Question", [], TEST_EVIDENCE)
    )
    assert result.text == "Answer"
    assert result.simulated is False


@pytest.mark.parametrize(
    "payload, expected",
    [
        ({"success": True, "result": {"response": ""}}, "no text response"),
        ({"success": True, "result": {"response": "   "}}, "no text response"),
        ({"success": True, "result": {"response": 42}}, "no text response"),
        ({"success": True, "result": ["wrong"]}, "unexpected response"),
        (["wrong"], "reported an error"),
        ({"success": False, "errors": [{"message": "bad"}]}, "reported an error"),
    ],
)
def test_cloudflare_invalid_or_empty_payloads_are_safe(monkeypatch, payload, expected):
    configure_cloudflare(monkeypatch)
    capture = CaptureClient(StubResponse(payload))
    monkeypatch.setattr(cloudflare.httpx, "AsyncClient", lambda timeout: capture)

    with pytest.raises(ProviderError, match=expected):
        asyncio.run(cloudflare.CloudflareProvider(get_settings()).generate("Question", [], TEST_EVIDENCE))


def test_cloudflare_invalid_json_is_safe(monkeypatch):
    configure_cloudflare(monkeypatch)

    class InvalidJsonResponse(StubResponse):
        def json(self):
            raise ValueError("not json")

    capture = CaptureClient(InvalidJsonResponse(None))
    monkeypatch.setattr(cloudflare.httpx, "AsyncClient", lambda timeout: capture)
    with pytest.raises(ProviderError, match="invalid response"):
        asyncio.run(cloudflare.CloudflareProvider(get_settings()).generate("Question", [], TEST_EVIDENCE))


def test_missing_credentials_raise_configuration_error(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "cloudflare")
    with pytest.raises(ProviderConfigurationError, match="credentials are missing"):
        asyncio.run(cloudflare.CloudflareProvider(get_settings()).generate("Question", [], TEST_EVIDENCE))


@pytest.mark.parametrize(
    "status, expected, category",
    [
        (401, "rejected its credentials", "auth"),
        (403, "rejected its credentials", "auth"),
        (404, "not found or is unavailable", "endpoint_or_model"),
        (429, "rate limit", "rate_limit"),
        (500, "temporarily unavailable", "server"),
        (418, "rejected this request", "unknown"),
    ],
)
def test_cloudflare_http_failures_are_classified_without_details(
    monkeypatch, status, expected, category
):
    configure_cloudflare(monkeypatch)
    request = httpx.Request("POST", "https://example.test")
    response = httpx.Response(
        status,
        request=request,
        json={"success": False, "errors": [{"code": 1001, "message": "do not log this"}]},
    )
    capture = CaptureClient(response)
    monkeypatch.setattr(cloudflare.httpx, "AsyncClient", lambda timeout: capture)

    with pytest.raises(ProviderError, match=expected) as error:
        asyncio.run(cloudflare.CloudflareProvider(get_settings()).generate("Question", [], TEST_EVIDENCE))
    assert error.value.diagnostic == ProviderDiagnostic(
        provider="cloudflare",
        category=category,
        http_status=status,
        cloudflare_error_code=1001,
    )


def test_cloudflare_rejects_unsafe_error_codes(monkeypatch):
    configure_cloudflare(monkeypatch)
    request = httpx.Request("POST", "https://example.test")
    response = httpx.Response(
        400,
        request=request,
        json={
            "success": False,
            "errors": [
                {"code": "account-secret-value", "message": "do not log this"},
                {"code": "Bearer secret-token", "message": "do not log this"},
            ],
        },
    )
    capture = CaptureClient(response)
    monkeypatch.setattr(cloudflare.httpx, "AsyncClient", lambda timeout: capture)

    with pytest.raises(ProviderError) as error:
        asyncio.run(cloudflare.CloudflareProvider(get_settings()).generate("Question", [], TEST_EVIDENCE))
    assert error.value.diagnostic.cloudflare_error_code is None


def test_cloudflare_network_failure_is_classified(monkeypatch):
    configure_cloudflare(monkeypatch)

    class NetworkFailureClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc_value, traceback):
            return False

        async def post(self, *args, **kwargs):
            raise httpx.ConnectError("do not log this")

    monkeypatch.setattr(
        cloudflare.httpx, "AsyncClient", lambda timeout: NetworkFailureClient()
    )
    with pytest.raises(ProviderError) as error:
        asyncio.run(cloudflare.CloudflareProvider(get_settings()).generate("Question", [], TEST_EVIDENCE))
    assert error.value.diagnostic == ProviderDiagnostic(
        provider="cloudflare", category="network"
    )


def test_cloudflare_timeout_is_safe(monkeypatch):
    configure_cloudflare(monkeypatch)

    class TimeoutClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc_value, traceback):
            return False

        async def post(self, *args, **kwargs):
            raise httpx.TimeoutException("simulated timeout")

    monkeypatch.setattr(cloudflare.httpx, "AsyncClient", lambda timeout: TimeoutClient())
    with pytest.raises(ProviderError, match="timed out"):
        asyncio.run(cloudflare.CloudflareProvider(get_settings()).generate("Question", [], TEST_EVIDENCE))


def test_safety_screening_happens_before_provider(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "cloudflare")

    def provider_must_not_be_built(settings):
        raise AssertionError("high-risk messages must not build a provider")

    monkeypatch.setattr(main, "build_provider", provider_must_not_be_built)
    response = client.post("/api/chat", json={"message": "I cannot breathe"})
    assert response.status_code == 200
    assert response.json()["category"] == "emergency"


def test_emergency_questions_never_reach_cloudflare(monkeypatch):
    configure_cloudflare(monkeypatch)
    monkeypatch.setattr(
        cloudflare.CloudflareProvider,
        "generate",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            AssertionError("emergency must be blocked before inference")
        ),
    )
    response = client.post("/api/chat", json={"message": "I was poisoned"})
    assert response.status_code == 200
    assert response.json()["status"] == "blocked"
    assert response.json()["provider"] == "policy"


def test_live_provider_failure_does_not_fall_back_to_mock(monkeypatch):
    configure_cloudflare(monkeypatch)
    monkeypatch.setattr(main, "knowledge_service", synthetic_service())
    async def failed_generate(self, message, history, evidence):
        raise ProviderError("simulated live failure")

    monkeypatch.setattr(cloudflare.CloudflareProvider, "generate", failed_generate)
    response = client.post("/api/chat", json={"message": "What information is listed on a label?"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "error"
    assert payload["simulated"] is False
    assert payload["provider"] == "cloudflare"
    assert "SIMULATED" not in payload["message"]


def test_api_logs_only_sanitized_diagnostic_metadata(monkeypatch, caplog):
    configure_cloudflare(monkeypatch)
    monkeypatch.setattr(main, "knowledge_service", synthetic_service())

    async def failed_generate(self, message, history, evidence):
        raise ProviderError(
            "internal details must not be logged",
            diagnostic=ProviderDiagnostic(
                provider="cloudflare",
                category="auth",
                http_status=401,
                cloudflare_error_code=1001,
            ),
        )

    monkeypatch.setattr(cloudflare.CloudflareProvider, "generate", failed_generate)
    response = client.post("/api/chat", json={"message": "What information is listed on a label?"})
    assert response.status_code == 200
    assert response.json()["category"] == "provider_error"
    assert "internal details" not in caplog.text
    assert "provider=cloudflare" in caplog.text
    assert "category=auth" in caplog.text
    assert "http_status=401" in caplog.text
    assert "cloudflare_error_code=1001" in caplog.text
    assert "Bearer" not in caplog.text
    assert "test-token" not in caplog.text


def test_existing_api_contract_remains_functional(monkeypatch):
    monkeypatch.setenv("APP_MODE", "mock")
    monkeypatch.setattr(main, "knowledge_service", synthetic_service())
    response = client.post(
        "/api/chat",
        json={"message": "What information is listed on a label?", "history": []},
    )
    assert response.status_code == 200
    payload = response.json()
    assert set(("status", "message", "category", "simulated", "provider", "disclaimer")) <= set(payload)
    assert payload["status"] == "ok"
    assert payload["simulated"] is True


def test_frontend_assets_and_responses_do_not_expose_provider_secrets():
    frontend = "\n".join(
        Path(name).read_text(encoding="utf-8")
        for name in ("prototype.html", "prototype.css", "prototype.js")
    ).lower()
    assert "cloudflare_api_token" not in frontend
    assert "bearer test-token" not in frontend

    health = client.get("/health")
    assert "test-token" not in health.text
    assert "api_token" not in health.text.lower()
