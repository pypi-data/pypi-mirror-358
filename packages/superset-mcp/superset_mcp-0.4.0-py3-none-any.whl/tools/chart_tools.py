"""
Chart Tools for Superset MCP

This module contains all chart-related tools for the Superset MCP server.
"""

import json
import prison
from main import mcp
from typing import Dict, Any, Optional, List, Literal
from mcp.server.fastmcp import Context
from pydantic import BaseModel, Field
from utils import requires_auth, handle_api_errors, make_api_request


# Pydantic Models for Chart Operations

class ChartListFilter(BaseModel):
    """
    Represents a filter condition for chart list queries.
    """
    col: str = Field(description="Column name to filter on")
    opr: Literal[
        "eq", "neq", "gt", "gte", "lt", "lte", 
        "temporal_range","like", "ilike"
    ] = Field(description="Filter operator")
    value: Any = Field(description="Filter value (can be string, number, boolean, or array)")


class ChartUpdatePayload(BaseModel):
    """
    Defines the payload for updating an existing chart.
    """
    slice_name: Optional[str] = Field(None, description="Name/title of the chart", max_length=250)
    description: Optional[str] = Field(None, description="A description of the chart")
    viz_type: Optional[str] = Field(
        None,
        description="Visualization type. Common types include: 'bar', 'line', 'area', 'pie', 'table', 'scatter', 'big_number', 'gauge', 'treemap', 'funnel', 'radar', 'sankey', 'timeseries_line', 'timeseries_bar', 'timeseries_area', 'pivot_table', etc.",
        max_length=250
    )
    params: Optional[str] = Field(None, description="Visualization parameters as JSON string")
    cache_timeout: Optional[int] = Field(
        None,
        description="Duration (in seconds) of the caching timeout for this chart"
    )
    dashboards: Optional[List[int]] = Field(None, description="List of dashboard IDs to include this chart")
    owners: Optional[List[int]] = Field(None, description="List of user IDs who should own this chart")
    datasource_id: Optional[int] = Field(None, description="ID of the dataset or SQL table")
    datasource_type: Optional[Literal["table", "dataset", "query", "saved_query", "view"]] = Field(
        None, description="Type of datasource"
    )
    tags: Optional[List[int]] = Field(None, description="List of tag IDs to associate with the chart")


class ChartResult(BaseModel):
    """
    Represents the result of chart operations.
    """
    id: Optional[int] = Field(None, description="Chart ID")
    slice_name: Optional[str] = Field(None, description="Chart name")
    description: Optional[str] = Field(None, description="Chart description")
    viz_type: Optional[str] = Field(None, description="Visualization type")
    params: Optional[str] = Field(None, description="Chart parameters as JSON string")
    cache_timeout: Optional[int] = Field(None, description="Cache timeout in seconds")
    datasource_id: Optional[int] = Field(None, description="Datasource ID")
    datasource_type: Optional[str] = Field(None, description="Datasource type")
    is_managed_externally: Optional[bool] = Field(None, description="Whether chart is managed externally")
    query_context: Optional[str] = Field(None, description="Query context as JSON string")
    thumbnail_url: Optional[str] = Field(None, description="Thumbnail URL")
    url: Optional[str] = Field(None, description="Chart URL")


class ChartListResult(BaseModel):
    """
    Represents the result of chart list operations.
    """
    count: Optional[int] = Field(None, description="Total number of charts")
    result: List[ChartResult] = Field(default_factory=list, description="List of charts")


class ChartDeleteResult(BaseModel):
    """
    Represents the result of chart deletion.
    """
    message: str = Field(description="Deletion confirmation message")


@mcp.tool()
@requires_auth
@handle_api_errors
async def superset_chart_list(
    ctx: Context,
    columns: Optional[List[str]] = Field(None, description="Columns to include in response"),
    keys: Optional[List[Literal["list_columns", "order_columns", "label_columns", "description_columns", "list_title", "none"]]] = Field(
        None, description="Metadata keys to include in response"
    ),
    order_column: Optional[str] = Field(None, description="Column to sort by"),
    order_direction: Optional[Literal["asc", "desc"]] = Field(None, description="Sort direction"),
    page: Optional[int] = Field(None, description="Page number (0-based)"),
    select_columns: Optional[List[str]] = Field(None, description="Specific columns to select"),
    filters: Optional[List[ChartListFilter]] = Field(None, description="Filter conditions")
) -> ChartListResult:
    """
    Get a list of charts from Superset with support for filtering, sorting, and pagination
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
    
    response_data = await make_api_request(ctx, "get", "/api/v1/chart/", params=params)
    return ChartListResult(**response_data)


@mcp.tool()
@requires_auth
@handle_api_errors
async def superset_chart_get_by_id(ctx: Context, chart_id: int) -> ChartResult:
    """
    Get details for a specific chart
    """
    response_data = await make_api_request(ctx, "get", f"/api/v1/chart/{chart_id}")
    # Extract the result field if it exists, otherwise use the whole response
    chart_data = response_data.get("result", response_data)
    return ChartResult(**chart_data)

@mcp.tool()
@requires_auth
@handle_api_errors
async def superset_chart_update(ctx: Context, chart_id: int, payload: ChartUpdatePayload) -> ChartResult:
    """
    Update an existing chart. It's recommended to use `superset_chart_get_by_id` to understand the `params` format before updating.
    """
    api_payload = payload.model_dump(exclude_none=True)
    response_data = await make_api_request(ctx, "put", f"/api/v1/chart/{chart_id}", data=api_payload)
    # Extract the result field if it exists, otherwise use the whole response
    chart_data = response_data.get("result", response_data)
    return ChartResult(**chart_data)


@mcp.tool()
@requires_auth
@handle_api_errors
async def superset_chart_delete(ctx: Context, chart_id: int) -> ChartDeleteResult:
    """
    Delete a chart
    """
    response = await make_api_request(ctx, "delete", f"/api/v1/chart/{chart_id}")

    if not response.get("error"):
        return ChartDeleteResult(message=f"Chart {chart_id} deleted successfully")

    # If there's an error, the response should still be handled by the error decorator
    return ChartDeleteResult(message=response.get("message", "Unknown error occurred")) 