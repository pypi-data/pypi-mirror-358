from typing import TYPE_CHECKING

from .azure import AzureOpenAIProvider
from .base import AIProvider
from .google import GoogleProvider
from .openai import OpenAIProvider

if TYPE_CHECKING:
    from ..config import Config


class AIProviderFactory:
    """Factory to create AI providers."""

    @staticmethod
    def create_provider(provider_name: str, config: "Config") -> AIProvider:
        """Creaate an AI provider based on the provider name and configuration."""
        providers = {
            "openai": OpenAIProvider,
            "google": GoogleProvider,
            "azure": AzureOpenAIProvider,
        }

        if provider_name not in providers:
            available = ", ".join(providers.keys())
            raise ValueError(
                f"Provider '{provider_name}' not available. Available: {available}"
            )

        provider = providers[provider_name](config)

        if not provider.is_configured():
            raise ValueError(
                f"Provider '{provider_name}' is not configured correctly. "
                f"Check your configuration settings."
            )

        return provider

    @staticmethod
    def get_available_providers() -> list[str]:
        """Returns a list of available AI providers."""
        return ["openai", "google", "azure"]

    @staticmethod
    def is_provider_available(provider_name: str) -> bool:
        """Check if a provider is available."""
        return provider_name in AIProviderFactory.get_available_providers()
