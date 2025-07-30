import traceback
from typing import Any

from .base import Provider


def check_local_cache(
    provider_impl: Provider, identifier: str, repo_type: str = "model", **kwargs: Any
) -> dict[str, Any] | None:
    """
    Check if the model/dataset is already cached locally.
    Returns a cached response dict if found, else None.
    """
    try:
        # Check if download is needed using provider's method
        needs_download = provider_impl.needs_download(
            identifier=identifier, repo_type=repo_type, **kwargs
        )

        if needs_download is not None:
            print(
                "Found cached %s: %s at %s", repo_type, identifier, needs_download
            )   
            return {"status": "cached", "path": str(needs_download)}
    except Exception as e:
        print(f"Error checking cache for {repo_type} {identifier}: {e}")

    return None


def require_provider_auth(
    provider_impl: Provider,
    identifier: str,
    repo_type: str,
    token: str | None,
    provider_name: str,
) -> dict[str, Any] | None:
    """
    Check if authentication is required for the resource before download.
    Returns an auth_required response dict if needed, else None.
    """
    try:
        access_result = provider_impl.check_access(
            identifier, repo_type=repo_type, token=token
        )
        if not access_result.accessible:
            print(
                "Authentication required for %s %s, token: %s",
                repo_type,
                identifier,
                token,
            )
            return {
                "status": "auth_required",
                "provider": provider_name,
                "identifier": identifier,
                **access_result.to_dict(),
            }
    except Exception:
        # Ignore access check failures and proceed to download attempt
        pass
    return None


def perform_download(
    provider_impl: Provider, *args: Any, **kwargs: Any
) -> dict[str, Any]:
    """
    Perform the download call on provider_impl with error handling.
    Returns a dict with status and either path or error message.
    """
    try:
        dest = provider_impl.download(*args, **kwargs)
        return {"status": "downloaded", "path": str(dest)}
    except Exception as err:
        print(f"Download error: {err}")
        traceback.print_exc()
        return {"status": "error", "message": str(err)}
