"""Tools module for mathematical operations."""

from typing import Any

from .mcp_service import check_local_cache, require_provider_auth, perform_download
from .base import get_provider
from typing import Annotated
from pydantic import Field

def add(a: Annotated[int, Field(description="The first number")],
        b: Annotated[int, Field(description="The second number")]) -> Annotated[int, Field(description="The sum of the two numbers")]:
    """Add two numbers."""
    return a + b

def _download_resource(
    provider: str,
    identifier: str, 
    resource_type: str,
    token: str | None = None,
    **kwargs
) -> dict[str, Any]:
    """Generic resource download with common 3-step pattern.
    
    Args:
        provider: Provider name
        identifier: Resource identifier
        resource_type: "model" or "dataset"
        token: Authentication token
        **kwargs: Additional parameters for specific resource types
    """
    # Step 1: Get provider implementation
    try:
        provider_impl = get_provider(provider)
    except ValueError as exc:
        return {
            "status": "error", 
            "code": "provider_not_registered",
            "message": str(exc),
        }

    # Step 2: Check if resource is already cached locally
    if cache_resp := check_local_cache(
        provider_impl, identifier, resource_type, token=token, **kwargs
    ):
        return cache_resp

    # Step 3: Pre-download auth check if not cached
    if auth_resp := require_provider_auth(
        provider_impl, identifier, resource_type, token, provider
    ):
        return auth_resp

    # Step 4: Perform download if auth passed
    download_kwargs = {"token": token, **kwargs}
    if resource_type == "dataset":
        download_kwargs["repo_type"] = "dataset"
    
    return perform_download(provider_impl, identifier, **download_kwargs)


def download_model(
    provider: Annotated[str, Field(description="The provider to use, choose from: huggingface")],
    identifier: Annotated[str, Field(description="The identifier of the model")],
    revision: Annotated[str | None, Field(description="The revision of the model, default is 'main'")] = None,
    token: Annotated[str | None, Field(description="The token to use for authentication")] = None,
) -> Annotated[dict[str, Any], Field(description="Returns: \n"
        "  • Success: {'status': 'downloaded', 'path': '<cache_dir>'}\n"
        "  • Cached: {'status': 'cached', 'path': '<cache_dir>'}\n"
        "  • Access Required: {'status': 'auth_required', 'access_url': '...', 'instructions': [...]}\n")]:  
    """Download (or reuse) a pretrained model and return final path."""
    return _download_resource(
        provider=provider,
        identifier=identifier,
        resource_type="model",
        token=token,
        revision=revision
    )


def download_dataset(
    provider: Annotated[str, Field(description="The provider to use, choose from: huggingface")],
    identifier: Annotated[str, Field(description="The identifier of the dataset")],
    name: Annotated[str | None, Field(description="The name of the dataset")] = None,
    token: Annotated[str | None, Field(description="The token to use for authentication")] = None,
) -> Annotated[dict[str, Any], Field(description="Returns: \n"
        "  • Success: {'status': 'downloaded', 'path': '<cache_dir>'}\n"
        "  • Cached: {'status': 'cached', 'path': '<cache_dir>'}\n"
        "  • Access Required: {'status': 'auth_required', 'access_url': '...', 'instructions': [...]}\n")]:
    """Download (or reuse) a dataset and return final path."""
    return _download_resource(
        provider=provider,
        identifier=identifier,
        resource_type="dataset", 
        token=token,
        name=name
    )