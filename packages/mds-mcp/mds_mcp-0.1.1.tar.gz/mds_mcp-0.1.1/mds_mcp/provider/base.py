from pathlib import Path
from typing import Any, Protocol, Type

from mds_mcp.logger import setup_logger

logger = setup_logger()


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

    def download(self, identifier: str, dest: Path | None, **kwargs: Any) -> Path | str:
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


_PROVIDER_REGISTRY: dict[str, Provider] = {}


def register_provider(cls: Type[Provider]) -> Type[Provider]:
    """Decorator to register a provider."""
    _PROVIDER_REGISTRY[cls.name] = cls()
    return cls


def get_provider(name: str) -> Provider:
    """Get a provider by name."""
    try:
        return _PROVIDER_REGISTRY[name]
    except KeyError as exc:
        logger.error(f"provider_not_registered: {name}")
        raise ValueError(f"provider_not_registered: {name}") from exc
