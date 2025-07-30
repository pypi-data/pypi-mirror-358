"""
Dataset Tools for Superset MCP

This module contains all dataset-related tools for the Superset MCP server.
"""

import prison
from main import mcp
from typing import Dict, Any, List, Optional, Literal
from mcp.server.fastmcp import Context
from utils import requires_auth, handle_api_errors, make_api_request
from pydantic import BaseModel, Field


class DatasetCreatePayload(BaseModel):
    """
    Defines the payload for creating a new dataset in Superset.
    """
    table_name: str = Field(description="Name of the physical table in the database")
    database_id: int = Field(alias="database", description="ID of the database where the table exists")
    db_schema: Optional[str] = Field(None, alias="schema", description="Optional database schema name where the table is located")
    owners: Optional[List[int]] = Field(None, description="Optional list of user IDs who should own this dataset")
    catalog: Optional[str] = Field(None, description="Optional database catalog name")
    sql: Optional[str] = Field(None, description="Optional SQL statement that defines the dataset (for virtual datasets)")
    external_url: Optional[str] = Field(None, description="Optional external URL for the dataset")
    normalize_columns: bool = Field(False, description="Whether to normalize column names")
    always_filter_main_dttm: bool = Field(False, description="Always filter main datetime column")


class DatasetUpdatePayload(BaseModel):
    """
    Defines the payload for updating an existing dataset.
    """
    table_name: Optional[str] = Field(None, description="Name of the table associated with the dataset")
    database_id: Optional[int] = Field(None, description="ID of the database")
    db_schema: Optional[str] = Field(None, alias="schema", description="Database schema name")
    description: Optional[str] = Field(None, description="Dataset description")
    sql: Optional[str] = Field(None, description="SQL statement that defines the dataset")
    cache_timeout: Optional[int] = Field(None, description="Duration (in seconds) of the caching timeout for this dataset")
    owners: Optional[List[int]] = Field(None, description="List of user IDs who should own this dataset")
    catalog: Optional[str] = Field(None, description="Database catalog name")
    external_url: Optional[str] = Field(None, description="External URL for the dataset")
    extra: Optional[str] = Field(None, description="Extra params for the dataset")
    fetch_values_predicate: Optional[str] = Field(None, description="Predicate used when fetching values from the dataset")
    filter_select_enabled: Optional[bool] = Field(None, description="Whether filter select is enabled")
    is_managed_externally: Optional[bool] = Field(None, description="Whether the dataset is managed externally")
    is_sqllab_view: Optional[bool] = Field(None, description="Whether the dataset is a SQL Lab view")
    main_dttm_col: Optional[str] = Field(None, description="Main datetime column")
    normalize_columns: Optional[bool] = Field(None, description="Whether to normalize column names")
    offset: Optional[int] = Field(None, description="Dataset offset")
    template_params: Optional[str] = Field(None, description="Template parameters")
    always_filter_main_dttm: Optional[bool] = Field(None, description="Always filter main datetime column")


class DatasetListFilter(BaseModel):
    """
    Represents a filter condition for dataset list queries.
    """
    col: str = Field(description="Column name to filter on")
    opr: Literal[
        "eq", "neq", "gt", "gte", "lt", "lte", 
        "temporal_range","like", "ilike"
    ] = Field(description="Filter operator")
    value: Any = Field(description="Filter value (can be string, number, boolean, or array)")


class DatasetListResult(BaseModel):
    """
    Result structure for dataset list operations.
    """
    count: Optional[int] = Field(None, description="The total record count on the backend")
    result: Optional[List[Dict[str, Any]]] = Field(None, description="List of datasets")
    ids: Optional[List[int]] = Field(None, description="A list of item ids")
    list_columns: Optional[List[str]] = Field(None, description="A list of columns")
    order_columns: Optional[List[str]] = Field(None, description="A list of allowed columns to sort")
    label_columns: Optional[Dict[str, str]] = Field(None, description="Column labels")
    description_columns: Optional[Dict[str, str]] = Field(None, description="Column descriptions")
    list_title: Optional[str] = Field(None, description="A title to render")
    error: Optional[str] = Field(None, description="Error message if request failed")


class DatasetDetailResult(BaseModel):
    """
    Result structure for dataset detail operations.
    """
    result: Optional[Dict[str, Any]] = Field(None, description="Dataset details")
    id: Optional[int] = Field(None, description="The item id")
    show_columns: Optional[List[str]] = Field(None, description="A list of columns to show")
    show_title: Optional[str] = Field(None, description="A title to render")
    label_columns: Optional[Dict[str, str]] = Field(None, description="Column labels")
    description_columns: Optional[Dict[str, str]] = Field(None, description="Column descriptions")
    error: Optional[str] = Field(None, description="Error message if request failed")


class DatasetCreateResult(BaseModel):
    """
    Result structure for dataset creation operations.
    """
    id: int = Field(description="ID of the created dataset")
    result: Dict[str, Any] = Field(description="Created dataset information")


class DatasetUpdateResult(BaseModel):
    """
    Result structure for dataset update operations.
    """
    id: int = Field(description="ID of the updated dataset")
    result: Dict[str, Any] = Field(description="Updated dataset information")


@mcp.tool()
@requires_auth
@handle_api_errors
async def superset_dataset_list(
    ctx: Context,
    columns: Optional[List[str]] = Field(None, description="Columns to include in response"),
    keys: Optional[List[Literal["list_columns", "order_columns", "label_columns", "description_columns", "list_title", "none"]]] = Field(
        None, description="Metadata keys to include in response"
    ),
    order_column: Optional[str] = Field(None, description="Column to sort by"),
    order_direction: Optional[Literal["asc", "desc"]] = Field(None, description="Sort direction"),
    page: Optional[int] = Field(None, description="Page number (0-based)"),
    select_columns: Optional[List[str]] = Field(None, description="Specific columns to select"),
    filters: Optional[List[DatasetListFilter]] = Field(None, description="Filter conditions")
) -> DatasetListResult:
    """
    Get a list of datasets from Superset with support for filtering, sorting, and pagination
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
    
    response_data = await make_api_request(ctx, "get", "/api/v1/dataset/", params=params)
    return DatasetListResult(**response_data)


@mcp.tool()
@requires_auth
@handle_api_errors
async def superset_dataset_get_by_id(ctx: Context, dataset_id: int) -> DatasetDetailResult:
    """
    Get details for a specific dataset
    """
    response_data = await make_api_request(ctx, "get", f"/api/v1/dataset/{dataset_id}")
    return DatasetDetailResult(**response_data)


@mcp.tool()
@requires_auth
@handle_api_errors
async def superset_dataset_create(ctx: Context, payload: DatasetCreatePayload) -> DatasetCreateResult:
    """
    Create a new dataset in Superset
    """
    api_payload = payload.model_dump(by_alias=True, exclude_none=True)
    response_data = await make_api_request(ctx, "post", "/api/v1/dataset/", data=api_payload)
    return DatasetCreateResult(**response_data)


@mcp.tool()
@requires_auth
@handle_api_errors
async def superset_dataset_update(ctx: Context, dataset_id: int, payload: DatasetUpdatePayload) -> DatasetUpdateResult:
    """
    Update an existing dataset
    """
    api_payload = payload.model_dump(by_alias=True, exclude_none=True)
    response_data = await make_api_request(ctx, "put", f"/api/v1/dataset/{dataset_id}", data=api_payload)
    return DatasetUpdateResult(**response_data) 