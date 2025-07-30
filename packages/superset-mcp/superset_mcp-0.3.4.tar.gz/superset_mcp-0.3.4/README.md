# Superset MCP Server

A Model Control Protocol (MCP) server for Apache Superset integration with AI assistants. This server enables AI assistants to interact with and control a Superset instance programmatically.

## Project Structure

```
superset-mcp-py/
├── main.py                 # Main MCP server entry point
├── utils.py               # Utility functions and decorators
├── pyproject.toml         # Project configuration and dependencies
├── superset.spec.json     # MCP server specification
├── rebuild.ps1           # PowerShell build script
├── uv.lock               # UV package manager lock file
└── tools/                # MCP tools organized by category
    ├── __init__.py       # Tools package initialization
    ├── auth_tools.py     # Authentication and token management
    ├── chart_tools.py    # Chart/slice operations
    ├── dashboard_tools.py # Dashboard management
    ├── database_tools.py # Database connection tools
    ├── dataset_tools.py  # Dataset/table operations
    └── sqllab_tools.py   # SQL Lab query execution
```

## Available Tools

### Authentication Tools
- **Token Validation**: Check if the current access token is still valid
- **Token Refresh**: Refresh the access token using the refresh endpoint
- **User Authentication**: Authenticate with Superset and get access token

### Dashboard Tools
- **superset_dashboard_list**: Get a list of all accessible dashboards
- **superset_dashboard_get_by_id**: Get detailed information for a specific dashboard
- **superset_dashboard_create**: Create a new dashboard with title and metadata
- **superset_dashboard_update**: Update existing dashboard properties

### Chart Tools
- **superset_chart_list**: Get a list of all accessible charts/slices
- **superset_chart_get_by_id**: Get detailed information for a specific chart
- **superset_chart_create**: Create a new chart with visualization configuration
- **superset_chart_update**: Update existing chart properties and settings
- **superset_chart_delete**: Delete a chart (permanent operation)

### Database Tools
- **superset_database_list**: Get a list of all database connections
- **superset_database_get_by_id**: Get detailed database connection information
- **superset_database_get_function_names**: Get SQL functions supported by a database
- **superset_database_validate_sql**: Validate SQL syntax against a specific database

### Dataset Tools
- **superset_dataset_list**: Get a list of all accessible datasets
- **superset_dataset_get_by_id**: Get detailed dataset information including columns and metrics
- **superset_dataset_create**: Create a new dataset from an existing database table
- **superset_dataset_update**: Update dataset properties and configuration

### SQL Lab Tools
- **superset_sqllab_execute_query**: Execute SQL queries against databases through SQL Lab

## Dependencies

- **fastapi**: Web framework for additional endpoints
- **httpx**: HTTP client for Superset API communication
- **mcp**: Model Control Protocol framework
- **uvicorn**: ASGI server
- **python-dotenv**: Environment variable management
- **pydantic**: Data validation and settings management

## Configuration

Set the following environment variables:
- `SUPERSET_BASE_URL`: Base URL of your Superset instance (default: http://localhost:8088)
- `SUPERSET_USERNAME`: Username for authentication (default: admin)
- `SUPERSET_PASSWORD`: Password for authentication (default: admin)
- `SUPERSET_AUTH_PROVIDER`: Authentication provider (default: db)
