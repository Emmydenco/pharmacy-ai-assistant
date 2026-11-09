import asyncio

import httpx
from fastapi.testclient import TestClient
import pytest

import backend.main as main
import backend.providers.cloudflare as cloudflare
from backend.config import get_settings
from backend.main import app
from tests.helpers import synthetic_evidence, synthetic_service
from backend.providers.base import ProviderError


client = TestClient(app)
TEST_EVIDENCE = synthetic_evidence()


def test_health_check_does_not_expose_credentials():
    response = client.get('/health')
    assert response.status_code == 200
    payload = response.json()
    assert payload['status'] == 'ok'
    assert 'api_token' not in response.text.lower()
    assert 'account_id' not in response.text.lower()


def test_request_validation_rejects_empty_message():
    response = client.post('/api/chat', json={'message': ''})
    assert response.status_code == 422


def test_mock_provider_returns_structured_simulated_response(monkeypatch):
    monkeypatch.setenv('APP_MODE', 'mock')
    monkeypatch.setattr(main, 'knowledge_service', synthetic_service())
    response = client.post('/api/chat', json={'message': 'What information is listed on a label?'})
    assert response.status_code == 200
    payload = response.json()
    assert payload['status'] == 'ok'
    assert payload['simulated'] is True
    assert payload['source'] is None
    assert 'SIMULATED' in payload['message']


def test_emergency_is_routed_before_provider(monkeypatch):
    monkeypatch.setenv('APP_MODE', 'cloudflare')
    monkeypatch.setenv('CLOUDFLARE_ACCOUNT_ID', '')
    monkeypatch.setenv('CLOUDFLARE_API_TOKEN', '')
    response = client.post('/api/chat', json={'message': "I can't breathe"})
    assert response.status_code == 200
    payload = response.json()
    assert payload['status'] == 'blocked'
    assert payload['category'] == 'emergency'
    assert 'emergency' in payload['message'].lower()


def test_patient_specific_request_is_routed_to_pharmacist():
    response = client.post('/api/chat', json={'message': 'Should I change my dose?'})
    assert response.status_code == 200
    assert response.json()['category'] == 'pharmacist'


def test_missing_cloudflare_credentials_never_falls_back_to_mock(monkeypatch):
    monkeypatch.setenv('APP_MODE', 'cloudflare')
    monkeypatch.setenv('CLOUDFLARE_ACCOUNT_ID', '')
    monkeypatch.setenv('CLOUDFLARE_API_TOKEN', '')
    monkeypatch.setattr(main, 'knowledge_service', synthetic_service())
    response = client.post('/api/chat', json={'message': 'What information is listed on a label?'})
    assert response.status_code == 200
    payload = response.json()
    assert payload['status'] == 'error'
    assert payload['simulated'] is False
    assert payload['category'] == 'provider_configuration'


async def _failing_provider(message, history):
    raise ProviderError('simulated timeout')


class FailingProvider:
    async def generate(self, message, history, evidence):
        raise ProviderError('simulated timeout')


def test_provider_errors_return_safe_error_without_fabrication(monkeypatch):
    monkeypatch.setenv('APP_MODE', 'mock')
    monkeypatch.setattr(main, 'knowledge_service', synthetic_service())
    monkeypatch.setattr(main, 'build_provider', lambda settings: FailingProvider())
    response = client.post('/api/chat', json={'message': 'What information is listed on a label?'})
    assert response.status_code == 200
    payload = response.json()
    assert payload['status'] == 'error'
    assert payload['category'] == 'provider_error'
    assert payload['simulated'] is False
    assert 'invented' in payload['message'].lower()


def test_cloudflare_timeout_is_converted_to_provider_error(monkeypatch):
    monkeypatch.setenv('APP_MODE', 'cloudflare')
    monkeypatch.setenv('CLOUDFLARE_ACCOUNT_ID', 'test-account')
    monkeypatch.setenv('CLOUDFLARE_API_TOKEN', 'test-token')

    class TimeoutClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc_value, traceback):
            return False

        async def post(self, *args, **kwargs):
            raise httpx.TimeoutException('simulated timeout')

    monkeypatch.setattr(
        cloudflare.httpx, 'AsyncClient', lambda timeout: TimeoutClient()
    )
    provider = cloudflare.CloudflareProvider(get_settings())
    with pytest.raises(ProviderError, match='timed out'):
        asyncio.run(provider.generate('What is a medicine?', [], TEST_EVIDENCE))


def test_cloudflare_malformed_payload_is_converted_to_provider_error(monkeypatch):
    monkeypatch.setenv('APP_MODE', 'cloudflare')
    monkeypatch.setenv('CLOUDFLARE_ACCOUNT_ID', 'test-account')
    monkeypatch.setenv('CLOUDFLARE_API_TOKEN', 'test-token')

    class ResponseClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc_value, traceback):
            return False

        async def post(self, *args, **kwargs):
            class Response:
                def raise_for_status(self):
                    return None

                def json(self):
                    return ['unexpected', 'shape']

            return Response()

    monkeypatch.setattr(
        cloudflare.httpx, 'AsyncClient', lambda timeout: ResponseClient()
    )
    provider = cloudflare.CloudflareProvider(get_settings())
    with pytest.raises(ProviderError, match='reported an error'):
        asyncio.run(provider.generate('What is a medicine?', [], TEST_EVIDENCE))


def test_frontend_does_not_contain_provider_secrets():
    prototype_js = open('prototype.js', encoding='utf-8').read().lower()
    assert 'cloudflare_api_token' not in prototype_js
    assert 'api_token' not in prototype_js
