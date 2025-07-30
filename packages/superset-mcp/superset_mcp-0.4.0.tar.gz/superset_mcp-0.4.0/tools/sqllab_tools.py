"""
SQL Lab Tools for Superset MCP

This module contains all SQL Lab-related tools for the Superset MCP server.
"""

from main import mcp
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from mcp.server.fastmcp import Context
from utils import requires_auth, handle_api_errors, make_api_request, get_csrf_token


class SqlExecutePayload(BaseModel):
    """
    Defines the payload for executing a SQL query in SQL Lab.
    """
    database_id: int = Field(description="ID of the database to query.")
    sql: str = Field(description="The SQL query to execute.")
    db_schema: Optional[str] = Field(None, alias="schema", description="The schema to run the query against. If not provided, the database's default schema is used.")
    catalog: Optional[str] = Field(None, description="The catalog to run the query against.")
    query_limit: Optional[int] = Field(100, alias="queryLimit", description="The maximum number of rows to return.")


class SqlLabExecutionResult(BaseModel):
    """
    Represents the result of a SQL Lab query execution.
    """
    status: str = Field(description="The status of the query (e.g., 'success', 'running', 'failed').")
    query_id: int = Field(description="The ID of the executed query.")
    columns: Optional[List[Dict[str, Any]]] = Field(None, description="List of column metadata dictionaries.")
    data: Optional[List[Dict[str, Any]]] = Field(None, description="A list of dictionaries, each representing a row of data.")
    expanded_columns: Optional[List[Dict[str, Any]]] = Field(None, description="List of expanded column metadata for struct/map types.")
    query: Optional[Dict[str, Any]] = Field(None, description="Detailed information about the query that was run.")
    selected_columns: Optional[List[Dict[str, Any]]] = Field(None, description="List of selected column metadata.")


@mcp.tool()
@requires_auth
@handle_api_errors
async def superset_sqllab_execute_query(
    ctx: Context, payload: SqlExecutePayload
) -> SqlLabExecutionResult:
    """
    Execute a SQL query in SQL Lab
    """
    # Ensure we have a CSRF token before executing the query
    from main import SupersetContext
    superset_ctx: SupersetContext = ctx.request_context.lifespan_context
    if not superset_ctx.csrf_token:
        await get_csrf_token(ctx)

    api_payload = payload.model_dump(by_alias=True, exclude_none=True)
    api_payload["tab"] = "MCP Query"
    api_payload["runAsync"] = False
    api_payload["select_as_cta"] = False

    response_data = await make_api_request(ctx, "post", "/api/v1/sqllab/execute/", data=api_payload)
    return SqlLabExecutionResult(**response_data)
