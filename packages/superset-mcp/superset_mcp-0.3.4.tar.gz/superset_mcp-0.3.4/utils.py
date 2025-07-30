"""
Utility functions and decorators for Superset MCP

This module contains common helper functions, decorators, and utilities
used across the Superset MCP tools.
"""

import os
import httpx
import logging
from typing import Dict, Any, Optional, Callable, Awaitable
from functools import wraps
from mcp.server.fastmcp import Context

# Constants
ACCESS_TOKEN_STORE_PATH = os.path.join(os.path.dirname(__file__), ".superset_token")
logger = logging.getLogger(__name__)


def load_stored_token() -> Optional[str]:
    """Load stored access token if it exists"""
    try:
        if os.path.exists(ACCESS_TOKEN_STORE_PATH):
            with open(ACCESS_TOKEN_STORE_PATH, "r") as f:
                return f.read().strip()
    except Exception:
        return None
    return None


def save_access_token(token: str):
    """Save access token to file"""
    try:
        with open(ACCESS_TOKEN_STORE_PATH, "w") as f:
            f.write(token)
    except Exception as e:
        logger.warning(f"Could not save access token: {e}", exc_info=True)


async def check_token_validity(ctx: Context) -> Dict[str, Any]:
    """Check if the current access token is still valid"""
    from main import SupersetContext
    superset_ctx: SupersetContext = ctx.request_context.lifespan_context

    if not superset_ctx.access_token:
        return {"valid": False, "error": "No access token available"}

    try:
        response = await superset_ctx.client.get("/api/v1/me/")
        if response.status_code == 200:
            return {"valid": True}
        else:
            return {
                "valid": False,
                "status_code": response.status_code,
                "error": response.text,
            }
    except Exception as e:
        return {"valid": False, "error": str(e)}


async def refresh_token(ctx: Context) -> Dict[str, Any]:
    """Refresh the access token"""
    from main import SupersetContext
    superset_ctx: SupersetContext = ctx.request_context.lifespan_context

    if not superset_ctx.access_token:
        return {"error": "No access token to refresh. Please authenticate first."}

    try:
        response = await superset_ctx.client.post("/api/v1/security/refresh")
        if response.status_code != 200:
            return {
                "error": f"Failed to refresh token: {response.status_code} - {response.text}"
            }

        data = response.json()
        access_token = data.get("access_token")
        if not access_token:
            return {"error": "No access token returned from refresh"}

        save_access_token(access_token)
        superset_ctx.access_token = access_token
        superset_ctx.client.headers.update({"Authorization": f"Bearer {access_token}"})
        return {
            "message": "Successfully refreshed access token",
            "access_token": access_token,
        }
    except Exception as e:
        return {"error": f"Error refreshing token: {str(e)}"}


async def authenticate_user(
    ctx: Context,
    username: Optional[str] = None,
    password: Optional[str] = None,
    refresh: bool = True,
) -> Dict[str, Any]:
    """Authenticate with Superset and get access token"""
    from main import SupersetContext, SUPERSET_USERNAME, SUPERSET_PASSWORD
    superset_ctx: SupersetContext = ctx.request_context.lifespan_context

    if superset_ctx.access_token:
        validity = await check_token_validity(ctx)
        if validity.get("valid"):
            return {
                "message": "Already authenticated with valid token",
                "access_token": superset_ctx.access_token,
            }
        if refresh:
            refresh_result = await refresh_token(ctx)
            if not refresh_result.get("error"):
                return refresh_result

    username = username or SUPERSET_USERNAME
    password = password or SUPERSET_PASSWORD

    if not username or not password:
        return {
            "error": "Username and password must be provided either as arguments or set in environment variables"
        }

    try:
        response = await superset_ctx.client.post(
            "/api/v1/security/login",
            json={
                "username": username,
                "password": password,
                "provider": superset_ctx.auth_provider,
                "refresh": refresh,
            },
        )
        if response.status_code != 200:
            return {
                "error": f"Failed to get access token: {response.status_code} - {response.text}"
            }

        data = response.json()
        access_token = data.get("access_token")
        if not access_token:
            return {"error": "No access token returned"}

        save_access_token(access_token)
        superset_ctx.access_token = access_token
        superset_ctx.client.headers.update({"Authorization": f"Bearer {access_token}"})
        await get_csrf_token(ctx)
        return {
            "message": "Successfully authenticated with Superset",
            "access_token": access_token,
        }
    except Exception as e:
        return {"error": f"Authentication error: {str(e)}"}


def requires_auth(
    func: Callable[..., Awaitable[Dict[str, Any]]],
) -> Callable[..., Awaitable[Dict[str, Any]]]:
    """
    Decorator to automatically handle authentication before executing a function.
    If not authenticated, it will try to authenticate using credentials from env vars.
    """

    @wraps(func)
    async def wrapper(ctx: Context, *args, **kwargs) -> Dict[str, Any]:
        from main import SupersetContext
        superset_ctx: SupersetContext = ctx.request_context.lifespan_context

        if not superset_ctx.access_token:
            logger.info("Not authenticated. Attempting to authenticate automatically...")
            auth_result = await authenticate_user(ctx)

            if auth_result.get("error"):
                return {
                    "error": f"Automatic authentication failed: {auth_result.get('error')}"
                }
            logger.info("Authentication successful.")

        # If we reach here, we should be authenticated.
        return await func(ctx, *args, **kwargs)

    return wrapper


def handle_api_errors(
    func: Callable[..., Awaitable[Dict[str, Any]]],
) -> Callable[..., Awaitable[Dict[str, Any]]]:
    """Decorator to handle API errors in a consistent way"""

    @wraps(func)
    async def wrapper(ctx: Context, *args, **kwargs) -> Dict[str, Any]:
        try:
            return await func(ctx, *args, **kwargs)
        except Exception as e:
            # Extract function name for better error context
            function_name = func.__name__
            return {"error": f"Error in {function_name}: {str(e)}"}

    return wrapper


async def with_auto_refresh(
    ctx: Context, api_call: Callable[[], Awaitable[httpx.Response]]
) -> Optional[httpx.Response]:
    """
    Helper function to handle automatic token refreshing for API calls

    This function will attempt to execute the provided API call. If the call
    fails with a 401 Unauthorized error, it will try to refresh the token
    and retry the API call once.

    Args:
        ctx: The MCP context
        api_call: The API call function to execute (should be a callable that returns a response)

    Returns:
        The response object on success, or None on authentication failure.
    """
    from main import SupersetContext
    superset_ctx: SupersetContext = ctx.request_context.lifespan_context

    if not superset_ctx.access_token:
        logger.error("Not authenticated. Please login first.")
        return None

    # First attempt
    try:
        response = await api_call()

        # If not an auth error, return the response
        if response.status_code != 401:
            return response

    except httpx.HTTPStatusError as e:
        if e.response.status_code != 401:
            raise e
        response = e.response
    except Exception as e:
        # For other errors, just raise
        raise e

    # If we got a 401, try to refresh the token
    logger.info("Received 401 Unauthorized. Attempting to refresh token...")
    refresh_result = await refresh_token(ctx)

    if refresh_result.get("error"):
        # If refresh failed, try to re-authenticate
        logger.warning(
            f"Token refresh failed: {refresh_result.get('error')}. Attempting re-authentication..."
        )
        auth_result = await authenticate_user(ctx)

        if auth_result.get("error"):
            # If re-authentication failed, return None
            logger.error(f"Authentication failed: {auth_result.get('error')}")
            return None

    # Retry the API call with the new token
    return await api_call()


async def get_csrf_token(ctx: Context) -> Optional[str]:
    """
    Get a CSRF token from Superset

    Makes a request to the /api/v1/security/csrf_token endpoint to get a token

    Args:
        ctx: MCP context
    """
    from main import SupersetContext
    superset_ctx: SupersetContext = ctx.request_context.lifespan_context
    client = superset_ctx.client

    try:
        response = await client.get("/api/v1/security/csrf_token/")
        if response.status_code == 200:
            data = response.json()
            csrf_token = data.get("result")
            superset_ctx.csrf_token = csrf_token
            return csrf_token
        else:
            logger.warning(f"Failed to get CSRF token: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        logger.error(f"Error getting CSRF token: {str(e)}", exc_info=True)
        return None


async def make_api_request(
    ctx: Context,
    method: str,
    endpoint: str,
    data: Dict[str, Any] = None,
    params: Dict[str, Any] = None,
    auto_refresh: bool = True,
) -> Dict[str, Any]:
    """
    Helper function to make API requests to Superset

    Args:
        ctx: MCP context
        method: HTTP method (get, post, put, delete)
        endpoint: API endpoint (without base URL)
        data: Optional JSON payload for POST/PUT requests
        params: Optional query parameters
        auto_refresh: Whether to auto-refresh token on 401
    """
    from main import SupersetContext
    superset_ctx: SupersetContext = ctx.request_context.lifespan_context
    client = superset_ctx.client

    # For non-GET requests, make sure we have a CSRF token
    if method.lower() != "get" and not superset_ctx.csrf_token:
        await get_csrf_token(ctx)

    async def make_request() -> httpx.Response:
        headers = {}

        # Add CSRF token for non-GET requests
        if method.lower() != "get" and superset_ctx.csrf_token:
            headers["X-CSRFToken"] = superset_ctx.csrf_token

        if method.lower() == "get":
            return await client.get(endpoint, params=params)
        elif method.lower() == "post":
            return await client.post(
                endpoint, json=data, params=params, headers=headers
            )
        elif method.lower() == "put":
            return await client.put(endpoint, json=data, headers=headers)
        elif method.lower() == "delete":
            return await client.delete(endpoint, headers=headers)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

    # Use auto_refresh if requested
    response = (
        await with_auto_refresh(ctx, make_request)
        if auto_refresh
        else await make_request()
    )

    if response is None:
        return {"error": "Authentication failed. Please login again."}

    if response.status_code not in [200, 201]:
        return {
            "error": f"API request failed: {response.status_code} - {response.text}"
        }

    return response.json() 