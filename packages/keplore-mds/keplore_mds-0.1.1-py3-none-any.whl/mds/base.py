from pathlib import Path
from typing import Any, Protocol, Type, Callable
import importlib


class AccessCheckResult:
    """Result of access check operation."""

    def __init__(
        self,
        accessible: bool,
        message: str = "",
        access_url: str | None = None,
        instructions: list[str] | None = None,
        requires_token: bool = False,
    ):
        self.accessible = accessible
        self.message = message
        self.access_url = access_url
        self.instructions = instructions or []
        self.requires_token = requires_token

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary format for MCP responses."""
        result = {
            "accessible": self.accessible,
            "message": self.message,
            "requires_token": self.requires_token,
        }

        if self.access_url:
            result["access_url"] = self.access_url

        if self.instructions:
            result["instructions"] = self.instructions

        return result


class Provider(Protocol):
    """Download provider interface for models, datasets, etc."""

    name: str

    def download(self, identifier: str, **kwargs: Any) -> Path | str:
        """Download artifact to dest directory and return cache path."""

    def needs_download(
        self, identifier: str, repo_type: str = "model", **kwargs: Any
    ) -> Path | None:
        """Check if download is needed for the given identifier.
        Args:
            identifier: Model/dataset identifier
            repo_type: Type of repository ("model" or "dataset")
            **kwargs: Additional arguments (e.g., revision, cache_dir, token)
        Returns:
            Path if already cached, None if download is needed
        """

    def check_access(
        self, identifier: str, repo_type: str = "model", **kwargs: Any
    ) -> AccessCheckResult:
        """Check if the artifact requires special access permissions.
        Args:
            identifier: Model/dataset identifier
            repo_type: Type of repository ("model" or "dataset")
            **kwargs: Additional arguments (e.g., token)
        Returns:
            AccessCheckResult: Information about access requirements
        """


# Provider registry for caching instances
_PROVIDER_REGISTRY: dict[str, Provider] = {}

# Factory functions for creating providers
PROVIDER_FACTORIES: dict[str, Callable[[], Provider]] = {
    'huggingface': lambda: _create_huggingface_provider(),
}


def _create_huggingface_provider() -> Provider:
    """Factory function to create HuggingFace provider."""
    try:
        module = importlib.import_module('.huggingface_provider', package=__package__)
        return module.HuggingFaceProvider()
    except ImportError as e:
        raise ValueError(f"Failed to import HuggingFace provider: {e}")


def register_provider_factory(name: str, factory: Callable[[], Provider]) -> None:
    """Register a provider factory function.
    
    Args:
        name: Provider name
        factory: Factory function that returns a Provider instance
    """
    PROVIDER_FACTORIES[name] = factory


def get_provider(name: str) -> Provider:
    """Get a provider by name using factory pattern.
    
    Args:
        name: Provider name
        
    Returns:
        Provider instance
        
    Raises:
        ValueError: If provider is not registered
    """
    # Return cached instance if available
    if name in _PROVIDER_REGISTRY:
        return _PROVIDER_REGISTRY[name]
    
    # Create new instance using factory
    if name in PROVIDER_FACTORIES:
        try:
            provider = PROVIDER_FACTORIES[name]()
            _PROVIDER_REGISTRY[name] = provider
            return provider
        except Exception as e:
            raise ValueError(f"Failed to create provider '{name}': {e}")
    
    # Provider not found
    available_providers = list(PROVIDER_FACTORIES.keys())
    raise ValueError(f"provider_not_registered: {name}. Available providers: {available_providers}")


def list_available_providers() -> list[str]:
    """List all available provider names."""
    return list(PROVIDER_FACTORIES.keys())


def clear_provider_cache() -> None:
    """Clear the provider instance cache. Useful for testing."""
    _PROVIDER_REGISTRY.clear()


# Legacy decorator for backwards compatibility (optional)
def register_provider(cls: Type[Provider]) -> Type[Provider]:
    """Legacy decorator for backwards compatibility.
    
    Note: This is kept for backwards compatibility but it's recommended
    to use register_provider_factory() for new providers.
    """
    def factory():
        return cls()
    
    register_provider_factory(cls.name, factory)
    return cls
