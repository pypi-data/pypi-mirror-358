import logging
import os
from typing import Any, Literal

import sentry_sdk
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from mds_mcp.logger import setup_logger
from mds_mcp.provider.base import get_provider

# Import providers to ensure they are registered
from mds_mcp.provider.huggingface_provider import HuggingFaceProvider  # noqa: F401
from mds_mcp.services.mcp_service import (
    check_local_cache,
    perform_download,
    require_provider_auth,
)

load_dotenv()

# Initialize Sentry if DSN is provided
if dsn := os.getenv("SENTRY_DSN"):
    sentry_sdk.init(
        dsn=dsn,
        traces_sample_rate=float(os.getenv("SENTRY_SAMPLE_RATE", "0.1")),
        environment=os.getenv("SENTRY_ENVIRONMENT", "development"),
        attach_stacktrace=True,
    )

log_level_str = os.getenv("LOG_LEVEL", "INFO").upper()
logger = setup_logger(
    name="model-cache-server", level=getattr(logging, log_level_str, logging.INFO)
)

# Create MCP server
mcp = FastMCP(
    "ModelCacheServer",
    host=os.getenv("MCP_HOST", "0.0.0.0"),
    port=int(os.getenv("MCP_PORT", "9004")),
    log_level=os.getenv("LOG_LEVEL", "INFO"),
)


@mcp.tool(
    description=(
        "Download a pretrained model to the local cache.\n"
        "Arguments:\n"
        "  • provider   - Model source (e.g., 'huggingface').\n"
        "  • identifier - Model repo ID or local path.\n"
        "  • token      - Access token for private or gated models (optional).\n"
        "Returns:\n"
        "  • Success: {'status': 'downloaded', 'path': '<cache_dir>'}\n"
        "  • Cached: {'status': 'cached', 'path': '<cache_dir>'}\n"
        "  • Access Required: {'status': 'auth_required', 'access_url': '...', 'instructions': [...]}\n"
        "  • Error: {'status': 'error', 'message': '...'}"
    )
)
def download_model(
    provider: str,
    identifier: str,
    token: str | None = None,
) -> dict[str, Any]:
    """Download (or reuse) a pretrained model and return final path."""
    # Get provider implementation
    try:
        provider_impl = get_provider(provider)
    except ValueError as exc:
        return {
            "status": "error",
            "code": "provider_not_registered",
            "message": str(exc),
        }

    # Step 1: Check if model is already cached locally
    if cache_resp := check_local_cache(provider_impl, identifier, "model", token=token):
        return cache_resp

    # Step 2: Pre-download auth check if not cached
    if auth_resp := require_provider_auth(
        provider_impl, identifier, "model", token, provider
    ):
        return auth_resp

    # Step 3: Perform download if auth passed
    return perform_download(provider_impl, identifier, None, token=token)


@mcp.tool(
    description=(
        "Download all splits of a dataset and store them in the local cache.\n"
        "Arguments:\n"
        "  • provider   - Dataset source (e.g., 'huggingface').\n"
        "  • identifier - Dataset repo name; for multi-config datasets "
        "use 'repo/config'.\n"
        "  • name       - Dataset config or task name (optional).\n"
        "  • token      - Access token for private or gated datasets (optional).\n"
        "Returns:\n"
        "  • Success: {'status': 'downloaded', 'path': '<cache_dir>'}\n"
        "  • Cached: {'status': 'cached', 'path': '<cache_dir>'}\n"
        "  • Access Required: {'status': 'auth_required', 'access_url': '...', 'instructions': [...]}\n"
        "  • Error: {'status': 'error', 'message': '...'}"
    )
)
def download_dataset(
    provider: str,
    identifier: str,
    name: str | None = None,
    token: str | None = None,
) -> dict[str, Any]:
    """Download a dataset and return its cache path."""
    # Get provider implementation
    try:
        provider_impl = get_provider(provider)
    except ValueError as exc:
        return {
            "status": "error",
            "code": "provider_not_registered",
            "message": str(exc),
        }

    # Step 1: Check if dataset is already cached locally
    if cache_resp := check_local_cache(
        provider_impl, identifier, "dataset", name=name, token=token
    ):
        return cache_resp

    # Step 2: Pre-download auth check if not cached
    if auth_resp := require_provider_auth(
        provider_impl, identifier, "dataset", token, provider
    ):
        return auth_resp

    # Step 3: Perform download if auth passed
    return perform_download(
        provider_impl, identifier, None, name=name, token=token, repo_type="dataset"
    )


def main() -> None:
    """Main entry point for the MCP server."""
    # Get transport from environment variable
    transport_str = os.getenv("MCP_TRANSPORT", "stdio")

    # Ensure transport is valid
    valid_transports = {"stdio", "sse", "streamable-http"}
    if transport_str in valid_transports:
        transport: Literal["stdio", "sse", "streamable-http"] = transport_str  # type: ignore
    else:
        transport = "stdio"

    logger.info("MCP Server starting with transport: %s", transport)

    if transport == "streamable-http" or transport == "sse":
        logger.info("Host: %s", mcp.settings.host)
        logger.info("Port: %s", mcp.settings.port)

    mcp.run(transport=transport)


if __name__ == "__main__":
    main()
