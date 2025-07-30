from typing import (
    Optional,
    AsyncIterator,
)
import os
import httpx
import logging
from contextlib import asynccontextmanager
from dataclasses import dataclass
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.WARNING, format='%(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SUPERSET_BASE_URL = os.getenv("SUPERSET_BASE_URL", "http://localhost:8088")
SUPERSET_USERNAME = os.getenv("SUPERSET_USERNAME", "admin")
SUPERSET_PASSWORD = os.getenv("SUPERSET_PASSWORD", "admin")
SUPERSET_AUTH_PROVIDER = os.getenv("SUPERSET_AUTH_PROVIDER", "db")

@dataclass
class SupersetContext:
    """Typed context for the Superset MCP server"""

    client: httpx.AsyncClient
    base_url: str
    auth_provider: str
    access_token: Optional[str] = None
    csrf_token: Optional[str] = None


@asynccontextmanager
async def superset_lifespan(server: FastMCP) -> AsyncIterator[SupersetContext]:
    """Manage application lifecycle for Superset integration"""
    logger.info("Initializing Superset context...")

    # Create HTTP client
    client = httpx.AsyncClient(base_url=SUPERSET_BASE_URL, timeout=30.0)

    # Create context
    ctx = SupersetContext(
        client=client,
        base_url=SUPERSET_BASE_URL,
        auth_provider=SUPERSET_AUTH_PROVIDER,
    )

    # Try to load existing token
    from utils import load_stored_token

    stored_token = load_stored_token()
    if stored_token:
        ctx.access_token = stored_token
        # Set the token in the client headers
        client.headers.update({"Authorization": f"Bearer {stored_token}"})
        logger.info("Using stored access token")

        # Verify token validity
        try:
            response = await client.get("/api/v1/me/")
            if response.status_code != 200:
                logger.warning(
                    f"Stored token is invalid (status {response.status_code}). Will need to re-authenticate."
                )
                ctx.access_token = None
                client.headers.pop("Authorization", None)
        except Exception as e:
            logger.error(f"Error verifying stored token: {e}", exc_info=True)
            ctx.access_token = None
            client.headers.pop("Authorization", None)

    try:
        yield ctx
    finally:
        # Cleanup on shutdown
        logger.info("Shutting down Superset context...")
        await client.aclose()

mcp = FastMCP(
    "superset",
    "A Model Control Protocol (MCP) server for Apache Superset integration with AI assistants. This server enables AI assistants to interact with and control a Superset instance programmatically.",
    lifespan=superset_lifespan
)

def main():
    import tools
    mcp.run()
    
if __name__ == "__main__":
    main()


