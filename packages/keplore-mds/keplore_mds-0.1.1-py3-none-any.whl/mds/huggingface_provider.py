import os
from pathlib import Path
from typing import Any

from datasets import DatasetDict, load_dataset
from huggingface_hub import HfFolder, auth_check, snapshot_download
from huggingface_hub.utils import (
    GatedRepoError,
    LocalEntryNotFoundError,
    RepositoryNotFoundError,
)

from .base import AccessCheckResult, Provider


def get_cache_dir(model: Any, cache_dir: Path | str | None = None) -> Path:
    """Return the cache directory for a model."""
    arg_path = Path(model.name_or_path)
    if arg_path.is_dir():
        return arg_path.resolve()

    commit = getattr(model.config, "_commit_hash", None)
    return Path(
        snapshot_download(
            repo_id=model.name_or_path,
            revision=commit,
            cache_dir=cache_dir,
            local_files_only=True,
        )
    ).resolve()


class HuggingFaceProvider(Provider):
    """Download models or datasets via the official HF APIs."""

    name = "huggingface"

    def download(self, identifier: str, **kwargs: Any) -> Path:
        """Route the request based on repo_type (model or dataset)."""
        repo_type = kwargs.get("repo_type", "model").lower()
        if repo_type == "dataset":
            return self.download_dataset(identifier, **kwargs)
        else:
            return self.download_model(identifier, **kwargs)

    def download_model(self, identifier: str, **kwargs: Any) -> Path:
        """Download and cache a model with its tokenizer."""
        token = kwargs.get("token")
        cache_dir = kwargs.get("cache_dir")
        revision = kwargs.get("revision", None)
        cache_path = snapshot_download(
            repo_id=identifier,
            token=token,
            revision=revision,
            cache_dir=cache_dir,
        )
        return cache_path

    def download_dataset(self, identifier: str, **kwargs: Any) -> Path:
        """Download and cache all splits of a dataset."""
        # Correctly pass cache_dir to load_dataset
        dataset = load_dataset(
            path=identifier,
            split=None,
            revision=kwargs.get("revision", None),
            name=kwargs.get("name", None),
            token=kwargs.get("token", None),
            cache_dir=kwargs.get("cache_dir"),
        )

        # Get cache path from dataset
        if isinstance(dataset, DatasetDict):
            ds_one = dataset.get("train") or next(iter(dataset.values()))
        else:
            ds_one = dataset

        if ds_one and ds_one.cache_files:
            cache_dir_path = Path(
                ds_one.cache_files[0]["filename"]
            ).parent.parent.parent
        else:
            # Fallback for datasets without cache_files or empty datasets
            cache_dir_path = Path(
                kwargs.get("cache_dir")
                or snapshot_download(
                    identifier, repo_type="dataset", cache_dir=kwargs.get("cache_dir")
                )
            )

        return cache_dir_path

    def needs_download(
        self, identifier: str, repo_type: str = "model", **kwargs: Any
    ) -> Path | None:
        """Check if download is needed for the given identifier."""
        try:
            # Pass cache_dir to ensure we check the correct location
            local_dir = snapshot_download(
                repo_id=identifier,
                repo_type=repo_type,
                revision=kwargs.get("revision"),
                cache_dir=kwargs.get("cache_dir"),
                local_files_only=True,
            )
            return Path(local_dir)
        except (LocalEntryNotFoundError, FileNotFoundError):
            return None

    def check_access(
        self, identifier: str, repo_type: str = "model", **kwargs: Any
    ) -> AccessCheckResult:
        """Check if a HuggingFace repository requires special access permissions."""
        token = kwargs.get("token") or self._get_token()

        try:
            auth_check(repo_id=identifier, repo_type=repo_type, token=token)
            return AccessCheckResult(
                accessible=True,
                message=f"Repository '{identifier}' is accessible.",
                requires_token=False,
            )
        except GatedRepoError:
            return AccessCheckResult(
                accessible=False,
                message=f"Repository '{identifier}' requires access approval, please follow the instructions below to get access.",
                access_url=f"https://huggingface.co/{identifier}",
                instructions=self._generate_access_instructions(identifier),
                requires_token=True,
            )
        except RepositoryNotFoundError:
            return AccessCheckResult(
                accessible=False,
                message=f"Repository '{identifier}' not found. It may be private or doesn't exist.",
                access_url=f"https://huggingface.co/{identifier}",
                instructions=self._generate_access_instructions(
                    identifier, is_private=True
                ),
                requires_token=True,
            )
        except Exception as e:
            if any(
                keyword in str(e).lower()
                for keyword in ["401", "403", "unauthorized", "forbidden"]
            ):
                return AccessCheckResult(
                    accessible=False,
                    message=f"Authentication required to access '{identifier}'.",
                    access_url=f"https://huggingface.co/{identifier}",
                    instructions=self._generate_access_instructions(identifier),
                    requires_token=True,
                )
            return AccessCheckResult(
                accessible=False,
                message=f"Unable to check access for '{identifier}': {str(e)}",
                requires_token=False,
            )

    def _get_token(self) -> str | None:
        token = os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_HUB_TOKEN")
        if token:
            return token
        try:
            return HfFolder.get_token()
        except Exception:
            return None

    def _generate_access_instructions(
        self, identifier: str, is_private: bool = False
    ) -> list[str]:
        base_instructions = [
            f"1. Visit the repository page: https://huggingface.co/{identifier}",
        ]
        if is_private:
            base_instructions.extend(
                [
                    "2. Ensure you have permission to access this private repository",
                    "3. Contact the repository owner if you need access",
                ]
            )
        else:
            base_instructions.extend(
                [
                    "2. Click 'Request access' or 'Agree and access repository'",
                    "3. Wait for approval (may take time for gated models like Meta LLaMA)",
                ]
            )
        base_instructions.extend(
            [
                "4. Generate an access token at: https://huggingface.co/settings/tokens",
                "5. Create a token with 'Read' permissions",
                "6. Set the token: export HF_TOKEN=hf_your_token_here",
                "7. Retry the download operation",
            ]
        )
        return base_instructions
