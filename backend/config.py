"""Small environment-backed settings object for the hosted-provider boundary."""

from dataclasses import dataclass, field
import os


def _env_value(*names: str, default: str = "") -> str:
    """Return the first non-empty environment value from the supplied aliases."""

    for name in names:
        value = os.getenv(name, "").strip()
        if value:
            return value
    return default


def _positive_float(*names: str, default: float) -> float:
    try:
        value = float(_env_value(*names, default=str(default)))
    except ValueError:
        return default
    return value if value > 0 else default


def _positive_int(*names: str, default: int) -> int:
    try:
        value = int(_env_value(*names, default=str(default)))
    except ValueError:
        return default
    return value if value > 0 else default


@dataclass(frozen=True)
class Settings:
    """Runtime configuration; no secret values are printed or returned to clients."""

    provider_mode: str = field(
        default_factory=lambda: _env_value("LLM_PROVIDER", "APP_MODE", default="mock").lower()
    )
    cloudflare_account_id: str = field(
        default_factory=lambda: _env_value("CLOUDFLARE_ACCOUNT_ID")
    )
    cloudflare_api_token: str = field(
        default_factory=lambda: _env_value("CLOUDFLARE_API_TOKEN")
    )
    cloudflare_model: str = field(
        default_factory=lambda: _env_value(
            "LLM_MODEL", "CLOUDFLARE_MODEL", default="@cf/meta/llama-3.2-3b-instruct"
        )
    )
    provider_timeout_seconds: float = field(
        default_factory=lambda: _positive_float(
            "LLM_TIMEOUT_SECONDS", "PROVIDER_TIMEOUT_SECONDS", default=20.0
        )
    )
    max_output_tokens: int = field(
        default_factory=lambda: _positive_int("LLM_MAX_OUTPUT_TOKENS", default=500)
    )

    @property
    def cloudflare_configured(self) -> bool:
        return bool(self.cloudflare_account_id and self.cloudflare_api_token)


def get_settings() -> Settings:
    """Create settings per request so local environment changes are easy to test."""

    return Settings()
