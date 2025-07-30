"""
Dashboard Tools for Superset MCP

This module contains all dashboard-related tools for the Superset MCP server.
"""

import prison
from main import mcp
from typing import Dict, Any, Optional, List, Literal
from mcp.server.fastmcp import Context
from pydantic import BaseModel, Field
from utils import requires_auth, handle_api_errors, make_api_request


# Pydantic Models for Dashboard Operations

class DashboardListFilter(BaseModel):
    """
    Represents a filter condition for dashboard list queries.
    """
    col: str = Field(description="Column name to filter on")
    opr: Literal[
        "eq", "neq", "gt", "gte", "lt", "lte", 
        "temporal_range","like", "ilike"
    ] = Field(description="Filter operator")
    value: Any = Field(description="Filter value (can be string, number, boolean, or array)")


class DashboardUser(BaseModel):
    """
    Represents a user associated with a dashboard.
    """
    id: Optional[int] = Field(None, description="User ID")
    first_name: Optional[str] = Field(None, description="User's first name", max_length=64)
    last_name: Optional[str] = Field(None, description="User's last name", max_length=64)


class DashboardRole(BaseModel):
    """
    Represents a role associated with a dashboard.
    """
    id: Optional[int] = Field(None, description="Role ID")
    name: Optional[str] = Field(None, description="Role name", max_length=64)


class DashboardTag(BaseModel):
    """
    Represents a tag associated with a dashboard.
    """
    id: Optional[int] = Field(None, description="Tag ID")
    name: Optional[str] = Field(None, description="Tag name", max_length=250)
    type: Optional[int] = Field(None, description="Tag type (1-4)")


class DashboardResult(BaseModel):
    """
    Represents the result of dashboard operations.
    """
    id: Optional[int] = Field(None, description="Dashboard ID")
    dashboard_title: Optional[str] = Field(None, description="Dashboard title", max_length=500)
    slug: Optional[str] = Field(None, description="Unique URL slug for the dashboard", max_length=255)
    css: Optional[str] = Field(None, description="Override CSS for the dashboard")
    json_metadata: Optional[str] = Field(None, description="JSON metadata for dashboard configuration")
    position_json: Optional[str] = Field(None, description="JSON describing widget positioning")
    # published: Optional[bool] = Field(None, description="Whether dashboard is visible in the list")
    # certification_details: Optional[str] = Field(None, description="Details of the certification")
    # certified_by: Optional[str] = Field(None, description="Person or group that certified this dashboard")
    # external_url: Optional[str] = Field(None, description="External URL")
    # is_managed_externally: Optional[bool] = Field(None, description="Whether dashboard is managed externally")
    # thumbnail_url: Optional[str] = Field(None, description="Thumbnail URL")
    # url: Optional[str] = Field(None, description="Dashboard URL")
    # status: Optional[str] = Field(None, description="Dashboard status")
    # changed_by: Optional[DashboardUser] = Field(None, description="User who last changed the dashboard")
    # changed_by_name: Optional[str] = Field(None, description="Name of user who last changed the dashboard")
    # changed_on_delta_humanized: Optional[str] = Field(None, description="Human-readable time since last change")
    # changed_on_utc: Optional[str] = Field(None, description="UTC timestamp of last change")
    # created_by: Optional[DashboardUser] = Field(None, description="User who created the dashboard")
    # created_on_delta_humanized: Optional[str] = Field(None, description="Human-readable time since creation")
    owners: Optional[List[DashboardUser]] = Field(None, description="Dashboard owners")
    # roles: Optional[List[DashboardRole]] = Field(None, description="Dashboard roles")
    tags: Optional[List[DashboardTag]] = Field(None, description="Dashboard tags")


class DashboardListResult(BaseModel):
    """
    Represents the result of dashboard list operations.
    """
    count: Optional[int] = Field(None, description="Total number of dashboards")
    result: List[DashboardResult] = Field(default_factory=list, description="List of dashboards")

class DashboardUpdatePayload(BaseModel):
    """
    Defines the payload for updating an existing dashboard.
    """
    dashboard_title: Optional[str] = Field(None, description="Title of the dashboard", max_length=500)
    css: Optional[str] = Field(None, description="Override CSS for the dashboard")
    json_metadata: Optional[Dict[str, Any]] = Field(None, description="JSON metadata for dashboard configuration")
    position_json: Optional[str] = Field(None, description="JSON describing widget positioning")
    # published: Optional[bool] = Field(None, description="Whether dashboard is visible in the list")
    slug: Optional[str] = Field(None, description="Unique URL slug for the dashboard", max_length=255)
    owners: Optional[List[int]] = Field(None, description="List of user IDs who should own this dashboard")
    # roles: Optional[List[int]] = Field(None, description="List of role IDs for dashboard access")
    tags: Optional[List[int]] = Field(None, description="List of tag IDs to associate with the dashboard")
    # certification_details: Optional[str] = Field(None, description="Details of the certification")
    # certified_by: Optional[str] = Field(None, description="Person or group that certified this dashboard")
    # external_url: Optional[str] = Field(None, description="External URL")
    # is_managed_externally: Optional[bool] = Field(None, description="Whether dashboard is managed externally")


@mcp.tool()
@requires_auth
@handle_api_errors
async def superset_dashboard_list(
    ctx: Context,
    columns: Optional[List[str]] = Field(None, description="Columns to include in response"),
    keys: Optional[List[Literal["list_columns", "order_columns", "label_columns", "description_columns", "list_title", "none"]]] = Field(
        None, description="Metadata keys to include in response"
    ),
    order_column: Optional[str] = Field(None, description="Column to sort by"),
    order_direction: Optional[Literal["asc", "desc"]] = Field(None, description="Sort direction"),
    page: Optional[int] = Field(None, description="Page number (0-based)"),
    select_columns: Optional[List[str]] = Field(None, description="Specific columns to select"),
    filters: Optional[List[DashboardListFilter]] = Field(None, description="Filter conditions")
) -> DashboardListResult:
    """
    Get a list of dashboards from Superset with support for filtering, sorting, and pagination
    """
    params = {}
    
    # Build query dictionary
    query_dict = {}
    
    # Add query parameters if provided
    if columns is not None:
        query_dict["columns"] = columns
    if keys is not None:
        query_dict["keys"] = keys
    if order_column is not None:
        query_dict["order_column"] = order_column
    if order_direction is not None:
        query_dict["order_direction"] = order_direction
    if page is not None:
        query_dict["page"] = page
    if select_columns is not None:
        query_dict["select_columns"] = select_columns
        
    # Add filters if provided
    if filters:
        query_dict["filters"] = [
            {"col": f.col, "opr": f.opr, "value": f.value}
            for f in filters
        ]
    
    # Encode the query as Rison format
    if query_dict:
        params["q"] = prison.dumps(query_dict)
    
    response_data = await make_api_request(ctx, "get", "/api/v1/dashboard/", params=params)
    return DashboardListResult(**response_data)


@mcp.tool()
@requires_auth
@handle_api_errors
async def superset_dashboard_get_by_id(
    ctx: Context, dashboard_id: int
) -> DashboardResult:
    """
    Get details for a specific dashboard
    """
    response_data = await make_api_request(ctx, "get", f"/api/v1/dashboard/{dashboard_id}")
    # Extract the result field if it exists, otherwise use the whole response
    dashboard_data = response_data.get("result", response_data)
    return DashboardResult(**dashboard_data)


@mcp.tool()
@requires_auth
@handle_api_errors
async def superset_dashboard_update(
    ctx: Context, dashboard_id: int, payload: DashboardUpdatePayload
) -> DashboardResult:
    """
    Update an existing dashboard. It's recommended to use `superset_dashboard_get_by_id` to understand the `json_metadata` and `position_json` formats before updating.
    """
    api_payload = payload.model_dump(exclude_none=True)
    
    response_data = await make_api_request(
        ctx, "put", f"/api/v1/dashboard/{dashboard_id}", data=api_payload
    )
    # Extract the result field if it exists, otherwise use the whole response
    dashboard_data = response_data.get("result", response_data)
    return DashboardResult(**dashboard_data)