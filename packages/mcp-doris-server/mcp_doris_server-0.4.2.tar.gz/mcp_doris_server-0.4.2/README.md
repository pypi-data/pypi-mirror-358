<!--
Licensed to the Apache Software Foundation (ASF) under one
or more contributor license agreements.  See the NOTICE file
distributed with this work for additional information
regarding copyright ownership.  The ASF licenses this file
to you under the Apache License, Version 2.0 (the
"License"); you may not use this file except in compliance
with the License.  You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, either express or implied.  See the License for the
specific language governing permissions and limitations
under the License.
-->

# Doris MCP Server

Doris MCP (Model Context Protocol) Server is a backend service built with Python and FastAPI. It implements the MCP, allowing clients to interact with it through defined "Tools". It's primarily designed to connect to Apache Doris databases, potentially leveraging Large Language Models (LLMs) for tasks like converting natural language queries to SQL (NL2SQL), executing queries, and performing metadata management and analysis.

## 🚀 What's New in v0.4.1

- **🔒 Enhanced Security Framework**: Comprehensive SQL security validation with configurable blocked keywords, SQL injection protection, and unified security configuration management
- **🛠️ Connection Stability Improvements**: Fixed critical `at_eof` connection errors with advanced connection health monitoring, automatic retry mechanisms, and proactive connection cleanup
- **⚙️ Flexible Security Configuration**: Environment variable support for security policies (`BLOCKED_KEYWORDS`, `ENABLE_SECURITY_CHECK`) with unified configuration architecture eliminating code duplication
- **🎯 Centralized Configuration Management**: All security keywords now managed through single configuration source with consistent enforcement across all components
- **🚀 Production Reliability**: Enhanced error handling, connection diagnostics, and automatic recovery from database connection issues

> **🔧 Key Improvements**: Resolved connection stability issues, unified security keyword management, and added comprehensive environment variable configuration for security policies.

## Core Features

*   **MCP Protocol Implementation**: Provides standard MCP interfaces, supporting tool calls, resource management, and prompt interactions.
*   **Streamable HTTP Communication**: Unified HTTP endpoint supporting both request/response and streaming communication for optimal performance and reliability.
*   **Stdio Communication**: Standard input/output mode for direct integration with MCP clients like Cursor.
*   **Enterprise-Grade Architecture**: Modular design with comprehensive functionality:
    *   **Tools Manager**: Centralized tool registration and routing with unified interfaces (`doris_mcp_server/tools/tools_manager.py`)
    *   **Enhanced Monitoring Tools Module**: Advanced memory tracking, metrics collection, and flexible BE node discovery with modular, extensible design
    *   **Query Information Tools**: Enhanced SQL explain and profiling with configurable content truncation, file export for LLM attachments, and advanced query analytics
    *   **Resources Manager**: Resource management and metadata exposure (`doris_mcp_server/tools/resources_manager.py`)
    *   **Prompts Manager**: Intelligent prompt templates for data analysis (`doris_mcp_server/tools/prompts_manager.py`)
*   **Advanced Database Features**:
    *   **Query Execution**: High-performance SQL execution with advanced caching and optimization, enhanced connection stability and automatic retry mechanisms (`doris_mcp_server/utils/query_executor.py`)
    *   **Security Management**: Comprehensive SQL security validation with configurable blocked keywords, SQL injection protection, data masking, and unified security configuration management (`doris_mcp_server/utils/security.py`)
    *   **Metadata Extraction**: Comprehensive database metadata with catalog federation support (`doris_mcp_server/utils/schema_extractor.py`)
    *   **Performance Analysis**: Advanced column analysis, performance monitoring, and data analysis tools (`doris_mcp_server/utils/analysis_tools.py`)
*   **Catalog Federation Support**: Full support for multi-catalog environments (internal Doris tables and external data sources like Hive, MySQL, etc.)
*   **Enterprise Security**: Comprehensive security framework with authentication, authorization, SQL injection protection, and data masking capabilities with environment variable configuration support
*   **Unified Configuration Framework**: Centralized configuration management through `config.py` with comprehensive validation, standardized parameter naming, and smart default database handling with automatic fallback to `information_schema`

## System Requirements

*   Python 3.12+
*   Database connection details (e.g., Doris Host, Port, User, Password, Database)

## 🚀 Quick Start

### Installation from PyPI

```bash
# Install the latest version
pip install mcp-doris-server

# Install specific version
pip install mcp-doris-server==0.4.0
```

> **💡 Command Compatibility**: After installation, both `doris-mcp-server` and `mcp-doris-server` commands are available for backward compatibility. You can use either command interchangeably.

### Start Streamable HTTP Mode (Web Service)

The primary communication mode offering optimal performance and reliability:

```bash
# Full configuration with database connection
doris-mcp-server \
    --transport http \
    --host 0.0.0.0 \
    --port 3000 \
    --db-host 127.0.0.1 \
    --db-port 9030 \
    --db-user root \
    --db-password your_password 
```

### Start Stdio Mode (for Cursor and other MCP clients)

Standard input/output mode for direct integration with MCP clients:

```bash
# For direct integration with MCP clients like Cursor
doris-mcp-server --transport stdio
```

### Verify Installation

```bash
# Check installation
doris-mcp-server --help

# Test HTTP mode (in another terminal)
curl http://localhost:3000/health
```

### Environment Variables (Optional)

Instead of command-line arguments, you can use environment variables:

```bash
export DORIS_HOST="127.0.0.1"
export DORIS_PORT="9030"
export DORIS_USER="root"
export DORIS_PASSWORD="your_password"

# Then start with simplified command
doris-mcp-server --transport http --host 0.0.0.0 --port 3000
```

### Command Line Arguments

The `doris-mcp-server` command supports the following arguments:

| Argument | Description | Default | Required |
|:---------|:------------|:--------|:---------|
| `--transport` | Transport mode: `http` or `stdio` | `http` | No |
| `--host` | HTTP server host (HTTP mode only) | `0.0.0.0` | No |
| `--port` | HTTP server port (HTTP mode only) | `3000` | No |
| `--db-host` | Doris database host | `localhost` | No |
| `--db-port` | Doris database port | `9030` | No |
| `--db-user` | Doris database username | `root` | No |
| `--db-password` | Doris database password | - | Yes (unless in env) |

## Development Setup

For developers who want to build from source:

### 1. Clone the Repository

```bash
# Replace with the actual repository URL if different
git clone https://github.com/apache/doris-mcp-server.git
cd doris-mcp-server
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Copy the `.env.example` file to `.env` and modify the settings according to your environment:

```bash
cp .env.example .env
```

**Key Environment Variables:**

*   **Database Connection**:
    *   `DORIS_HOST`: Database hostname (default: localhost)
    *   `DORIS_PORT`: Database port (default: 9030)
    *   `DORIS_USER`: Database username (default: root)
    *   `DORIS_PASSWORD`: Database password
    *   `DORIS_DATABASE`: Default database name (default: information_schema)
    *   `DORIS_MIN_CONNECTIONS`: Minimum connection pool size (default: 5)
    *   `DORIS_MAX_CONNECTIONS`: Maximum connection pool size (default: 20)
    *   `DORIS_BE_HOSTS`: BE nodes for monitoring (comma-separated, optional - auto-discovery via SHOW BACKENDS if empty)
    *   `DORIS_BE_WEBSERVER_PORT`: BE webserver port for monitoring tools (default: 8040)
*   **Security Configuration**:
    *   `AUTH_TYPE`: Authentication type (token/basic/oauth, default: token)
    *   `TOKEN_SECRET`: Token secret key
    *   `ENABLE_SECURITY_CHECK`: Enable/disable SQL security validation (default: true, New in v0.4.1)
    *   `BLOCKED_KEYWORDS`: Comma-separated list of blocked SQL keywords (New in v0.4.1)
    *   `ENABLE_MASKING`: Enable data masking (default: true)
    *   `MAX_RESULT_ROWS`: Maximum result rows (default: 10000)
*   **Performance Configuration**:
    *   `ENABLE_QUERY_CACHE`: Enable query caching (default: true)
    *   `CACHE_TTL`: Cache time-to-live in seconds (default: 300)
    *   `MAX_CONCURRENT_QUERIES`: Maximum concurrent queries (default: 50)
    *   `MAX_RESPONSE_CONTENT_SIZE`: Maximum response content size for LLM compatibility (default: 4096, New in v0.4.0)
*   **Logging Configuration**:
    *   `LOG_LEVEL`: Log level (DEBUG/INFO/WARNING/ERROR, default: INFO)
    *   `LOG_FILE_PATH`: Log file path
    *   `ENABLE_AUDIT`: Enable audit logging (default: true)

### Available MCP Tools

The following table lists the main tools currently available for invocation via an MCP client:

| Tool Name                   | Description                                                  | Parameters                                                   |
|-----------------------------|--------------------------------------------------------------|--------------------------------------------------------------|
| `exec_query`                | Execute SQL query and return results.                       | `sql` (string, Required), `db_name` (string, Optional), `catalog_name` (string, Optional), `max_rows` (integer, Optional), `timeout` (integer, Optional) |
| `get_table_schema`          | Get detailed table structure information.                   | `table_name` (string, Required), `db_name` (string, Optional), `catalog_name` (string, Optional) |
| `get_db_table_list`         | Get list of all table names in specified database.         | `db_name` (string, Optional), `catalog_name` (string, Optional) |
| `get_db_list`               | Get list of all database names.                             | `catalog_name` (string, Optional)                           |
| `get_table_comment`         | Get table comment information.                              | `table_name` (string, Required), `db_name` (string, Optional), `catalog_name` (string, Optional) |
| `get_table_column_comments` | Get comment information for all columns in table.          | `table_name` (string, Required), `db_name` (string, Optional), `catalog_name` (string, Optional) |
| `get_table_indexes`         | Get index information for specified table.                  | `table_name` (string, Required), `db_name` (string, Optional), `catalog_name` (string, Optional) |
| `get_recent_audit_logs`     | Get audit log records for recent period.                    | `days` (integer, Optional), `limit` (integer, Optional)     |
| `get_catalog_list`          | Get list of all catalog names.                              | `random_string` (string, Required)                          |
| `get_sql_explain`           | Get SQL execution plan with configurable content truncation and file export for LLM analysis.               | `sql` (string, Required), `verbose` (boolean, Optional), `db_name` (string, Optional), `catalog_name` (string, Optional) |
| `get_sql_profile`           | Get SQL execution profile with content management and file export for LLM optimization workflows.                  | `sql` (string, Required), `db_name` (string, Optional), `catalog_name` (string, Optional), `timeout` (integer, Optional) |
| `get_table_data_size`       | Get table data size information via FE HTTP API.           | `db_name` (string, Optional), `table_name` (string, Optional), `single_replica` (boolean, Optional) |
| `get_monitoring_metrics_info` | Get Doris monitoring metrics definitions and descriptions. | `role` (string, Optional), `monitor_type` (string, Optional), `priority` (string, Optional) |
| `get_monitoring_metrics_data` | Get actual Doris monitoring metrics data from nodes with flexible BE discovery.      | `role` (string, Optional), `monitor_type` (string, Optional), `priority` (string, Optional) |
| `get_realtime_memory_stats` | Get real-time memory statistics via BE Memory Tracker with auto/manual BE discovery.     | `tracker_type` (string, Optional), `include_details` (boolean, Optional) |
| `get_historical_memory_stats` | Get historical memory statistics via BE Bvar interface with flexible BE configuration.   | `tracker_names` (array, Optional), `time_range` (string, Optional) |

**Note:** All metadata tools support catalog federation for multi-catalog environments. The `get_catalog_list` tool requires a `random_string` parameter for compatibility reasons. Enhanced monitoring tools in v0.4.0 provide comprehensive memory tracking and metrics collection capabilities with flexible BE node discovery.

### 4. Run the Service

Execute the following command to start the server:

```bash
./start_server.sh
```

This command starts the FastAPI application with Streamable HTTP MCP service.

**Service Endpoints:**

*   **Streamable HTTP**: `http://<host>:<port>/mcp` (Primary MCP endpoint - supports GET, POST, DELETE, OPTIONS)
*   **Health Check**: `http://<host>:<port>/health`

> **Note**: The server uses Streamable HTTP for web-based communication, providing unified request/response and streaming capabilities.

## Usage

Interaction with the Doris MCP Server requires an **MCP Client**. The client connects to the server's Streamable HTTP endpoint and sends requests according to the MCP specification to invoke the server's tools.

**Main Interaction Flow:**

1.  **Client Initialization**: Send an `initialize` method call to `/mcp` (Streamable HTTP).
2.  **(Optional) Discover Tools**: The client can call `tools/list` to get the list of supported tools, their descriptions, and parameter schemas.
3.  **Call Tool**: The client sends a `tools/call` request, specifying the `name` and `arguments`.
    *   **Example: Get Table Schema**
        *   `name`: `get_table_schema`
        *   `arguments`: Include `table_name`, `db_name`, `catalog_name`.
4.  **Handle Response**:
    *   **Non-streaming**: The client receives a response containing `content` or `isError`.
    *   **Streaming**: The client receives a series of progress notifications, followed by a final response.

### Catalog Federation Support

The Doris MCP Server supports **catalog federation**, enabling interaction with multiple data catalogs (internal Doris tables and external data sources like Hive, MySQL, etc.) within a unified interface.

#### Key Features:

*   **Multi-Catalog Metadata Access**: All metadata tools (`get_db_list`, `get_db_table_list`, `get_table_schema`, etc.) support an optional `catalog_name` parameter to query specific catalogs.
*   **Cross-Catalog SQL Queries**: Execute SQL queries that span multiple catalogs using three-part table naming.
*   **Catalog Discovery**: Use `mcp_doris_get_catalog_list` to discover available catalogs and their types.

#### Three-Part Naming Requirement:

**All SQL queries MUST use three-part naming for table references:**

*   **Internal Tables**: `internal.database_name.table_name`
*   **External Tables**: `catalog_name.database_name.table_name`

#### Examples:

1.  **Get Available Catalogs:**
    ```json
    {
      "tool_name": "mcp_doris_get_catalog_list",
      "arguments": {"random_string": "unique_id"}
    }
    ```

2.  **Get Databases in Specific Catalog:**
    ```json
    {
      "tool_name": "mcp_doris_get_db_list", 
      "arguments": {"random_string": "unique_id", "catalog_name": "mysql"}
    }
    ```

3.  **Query Internal Catalog:**
    ```json
    {
      "tool_name": "mcp_doris_exec_query",
      "arguments": {
        "random_string": "unique_id",
        "sql": "SELECT COUNT(*) FROM internal.ssb.customer"
      }
    }
    ```

4.  **Query External Catalog:**
    ```json
    {
      "tool_name": "mcp_doris_exec_query", 
      "arguments": {
        "random_string": "unique_id",
        "sql": "SELECT COUNT(*) FROM mysql.ssb.customer"
      }
    }
    ```

5.  **Cross-Catalog Query:**
    ```json
    {
      "tool_name": "mcp_doris_exec_query",
      "arguments": {
        "random_string": "unique_id", 
        "sql": "SELECT i.c_name, m.external_data FROM internal.ssb.customer i JOIN mysql.test.user_info m ON i.c_custkey = m.customer_id"
      }
    }
    ```

## Security Configuration

The Doris MCP Server includes a comprehensive security framework that provides enterprise-level protection through authentication, authorization, SQL security validation, and data masking capabilities.

### Security Features

*   **🔐 Authentication**: Support for token-based and basic authentication
*   **🛡️ Authorization**: Role-based access control (RBAC) with security levels
*   **🚫 SQL Security**: SQL injection protection and blocked operations
*   **🎭 Data Masking**: Automatic sensitive data masking based on user permissions
*   **📊 Security Levels**: Four-tier security classification (Public, Internal, Confidential, Secret)

### Authentication Configuration

Configure authentication in your environment variables:

```bash
# Authentication Type (token/basic/oauth)
AUTH_TYPE=token

# Token Secret for JWT validation
TOKEN_SECRET=your_secret_key_here

# Session timeout (in seconds)
SESSION_TIMEOUT=3600
```

#### Token Authentication Example

```python
# Client authentication with token
auth_info = {
    "type": "token",
    "token": "your_jwt_token",
    "session_id": "unique_session_id"
}
```

#### Basic Authentication Example

```python
# Client authentication with username/password
auth_info = {
    "type": "basic",
    "username": "analyst",
    "password": "secure_password",
    "session_id": "unique_session_id"
}
```

### Authorization & Security Levels

The system supports four security levels with hierarchical access control:

| Security Level | Access Scope | Typical Use Cases |
|:---------------|:-------------|:------------------|
| **Public** | Unrestricted access | Public reports, general statistics |
| **Internal** | Company employees | Internal dashboards, business metrics |
| **Confidential** | Authorized personnel | Customer data, financial reports |
| **Secret** | Senior management | Strategic data, sensitive analytics |

#### Role Configuration

Configure user roles and permissions:

```python
# Example role configuration
role_permissions = {
    "data_analyst": {
        "security_level": "internal",
        "permissions": ["read_data", "execute_query"],
        "allowed_tables": ["sales", "products", "orders"]
    },
    "data_admin": {
        "security_level": "confidential", 
        "permissions": ["read_data", "execute_query", "admin"],
        "allowed_tables": ["*"]
    },
    "executive": {
        "security_level": "secret",
        "permissions": ["read_data", "execute_query", "admin"],
        "allowed_tables": ["*"]
    }
}
```

### SQL Security Validation

The system automatically validates SQL queries for security risks:

#### Blocked Operations

Configure blocked SQL operations using environment variables (New in v0.4.1):

```bash
# Enable/disable SQL security check (New in v0.4.1)
ENABLE_SECURITY_CHECK=true

# Customize blocked keywords via environment variable (New in v0.4.1)
BLOCKED_KEYWORDS="DROP,DELETE,TRUNCATE,ALTER,CREATE,INSERT,UPDATE,GRANT,REVOKE,EXEC,EXECUTE,SHUTDOWN,KILL"

# Maximum query complexity score
MAX_QUERY_COMPLEXITY=100
```

**Default Blocked Keywords (Unified in v0.4.1):**
- **DDL Operations**: DROP, CREATE, ALTER, TRUNCATE
- **DML Operations**: DELETE, INSERT, UPDATE  
- **DCL Operations**: GRANT, REVOKE
- **System Operations**: EXEC, EXECUTE, SHUTDOWN, KILL

#### SQL Injection Protection

The system automatically detects and blocks:

*   **Union-based injections**: `UNION SELECT` attacks
*   **Boolean-based injections**: `OR 1=1` patterns  
*   **Time-based injections**: `SLEEP()`, `WAITFOR` functions
*   **Comment injections**: `--`, `/**/` patterns
*   **Stacked queries**: Multiple statements separated by `;`

#### Example Security Validation

```python
# This query would be blocked
dangerous_sql = "SELECT * FROM users WHERE id = 1; DROP TABLE users;"

# This query would be allowed
safe_sql = "SELECT name, email FROM users WHERE department = 'sales'"
```

### Data Masking Configuration

Configure automatic data masking for sensitive information:

#### Built-in Masking Rules

```python
# Default masking rules
masking_rules = [
    {
        "column_pattern": r".*phone.*|.*mobile.*",
        "algorithm": "phone_mask",
        "parameters": {
            "mask_char": "*",
            "keep_prefix": 3,
            "keep_suffix": 4
        },
        "security_level": "internal"
    },
    {
        "column_pattern": r".*email.*", 
        "algorithm": "email_mask",
        "parameters": {"mask_char": "*"},
        "security_level": "internal"
    },
    {
        "column_pattern": r".*id_card.*|.*identity.*",
        "algorithm": "id_mask", 
        "parameters": {
            "mask_char": "*",
            "keep_prefix": 6,
            "keep_suffix": 4
        },
        "security_level": "confidential"
    }
]
```

#### Masking Algorithms

| Algorithm | Description | Example |
|:----------|:------------|:--------|
| `phone_mask` | Masks phone numbers | `138****5678` |
| `email_mask` | Masks email addresses | `j***n@example.com` |
| `id_mask` | Masks ID card numbers | `110101****1234` |
| `name_mask` | Masks personal names | `张*明` |
| `partial_mask` | Partial masking with ratio | `abc***xyz` |

#### Custom Masking Rules

Add custom masking rules in your configuration:

```python
# Custom masking rule
custom_rule = {
    "column_pattern": r".*salary.*|.*income.*",
    "algorithm": "partial_mask",
    "parameters": {
        "mask_char": "*",
        "mask_ratio": 0.6
    },
    "security_level": "confidential"
}
```

### Security Configuration Examples

#### Environment Variables

```bash
# .env file
AUTH_TYPE=token
TOKEN_SECRET=your_jwt_secret_key
ENABLE_MASKING=true
MAX_RESULT_ROWS=10000
BLOCKED_SQL_OPERATIONS=DROP,DELETE,TRUNCATE,ALTER
MAX_QUERY_COMPLEXITY=100
ENABLE_AUDIT=true
```

#### Sensitive Tables Configuration

```python
# Configure sensitive tables with security levels
sensitive_tables = {
    "user_profiles": "confidential",
    "payment_records": "secret", 
    "employee_salaries": "secret",
    "customer_data": "confidential",
    "public_reports": "public"
}
```

### Security Best Practices

1. **🔑 Strong Authentication**: Use JWT tokens with proper expiration
2. **🎯 Principle of Least Privilege**: Grant minimum required permissions
3. **🔍 Regular Auditing**: Enable audit logging for security monitoring
4. **🛡️ Input Validation**: All SQL queries are automatically validated
5. **🎭 Data Classification**: Properly classify data with security levels
6. **🔄 Regular Updates**: Keep security rules and configurations updated

### Security Monitoring

The system provides comprehensive security monitoring:

```python
# Security audit log example
{
    "timestamp": "2024-01-15T10:30:00Z",
    "user_id": "analyst_user",
    "action": "query_execution", 
    "resource": "customer_data",
    "result": "blocked",
    "reason": "insufficient_permissions",
    "risk_level": "medium"
}
```

> **⚠️ Important**: Always test security configurations in a development environment before deploying to production. Regularly review and update security policies based on your organization's requirements.

## Connecting with Cursor

You can connect Cursor to this MCP server using Stdio mode (recommended) or Streamable HTTP mode.

### Stdio Mode

Stdio mode allows Cursor to manage the server process directly. Configuration is done within Cursor's MCP Server settings file (typically `~/.cursor/mcp.json` or similar).

### Method 1: Using PyPI Installation (Recommended)

Install the package from PyPI and configure Cursor to use it:

```bash
pip install mcp-doris-server
```

**Configure Cursor:** Add an entry like the following to your Cursor MCP configuration:

```json
{
  "mcpServers": {
    "doris-stdio": {
      "command": "doris-mcp-server",
      "args": ["--transport", "stdio"],
      "env": {
        "DORIS_HOST": "127.0.0.1",
        "DORIS_PORT": "9030",
        "DORIS_USER": "root",
        "DORIS_PASSWORD": "your_db_password"
      }
    }
  }
}
```

### Method 2: Using uv (Development)

If you have `uv` installed and want to run from source:

```bash
uv run --project /path/to/doris-mcp-server doris-mcp-server
```

**Note:** Replace `/path/to/doris-mcp-server` with the actual absolute path to your project directory.

**Configure Cursor:** Add an entry like the following to your Cursor MCP configuration:

```json
{
  "mcpServers": {
    "doris-stdio": {
      "command": "uv",
      "args": ["run", "--project", "/path/to/your/doris-mcp-server", "doris-mcp-server"],
      "env": {
        "DORIS_HOST": "127.0.0.1",
        "DORIS_PORT": "9030",
        "DORIS_USER": "root",
        "DORIS_PASSWORD": "your_db_password"
      }
    }
  }
}
```

### Streamable HTTP Mode

Streamable HTTP mode requires you to run the MCP server independently first, and then configure Cursor to connect to it.

1.  **Configure `.env`:** Ensure your database credentials and any other necessary settings are correctly configured in the `.env` file within the project directory.
2.  **Start the Server:** Run the server from your terminal in the project's root directory:
    ```bash
    ./start_server.sh
    ```
    This script reads the `.env` file and starts the FastAPI server with Streamable HTTP support. Note the host and port the server is listening on (default is `0.0.0.0:3000`).
3.  **Configure Cursor:** Add an entry like the following to your Cursor MCP configuration, pointing to the running server's Streamable HTTP endpoint:

    ```json
    {
      "mcpServers": {
        "doris-http": {
           "url": "http://127.0.0.1:3000/mcp"
        }
      }
    }
    ```
    
    > **Note**: Adjust the host/port if your server runs on a different address. The `/mcp` endpoint is the unified Streamable HTTP interface.

After configuring either mode in Cursor, you should be able to select the server (e.g., `doris-stdio` or `doris-http`) and use its tools.

## Directory Structure

```
doris-mcp-server/
├── doris_mcp_server/           # Main server package
│   ├── main.py                 # Main entry point and FastAPI app
│   ├── tools/                  # MCP tools implementation
│   │   ├── tools_manager.py    # Centralized tools management and registration
│   │   ├── resources_manager.py # Resource management and metadata exposure
│   │   ├── prompts_manager.py  # Intelligent prompt templates for data analysis
│   │   └── __init__.py
│   ├── utils/                  # Core utility modules
│   │   ├── config.py           # Configuration management with validation
│   │   ├── db.py               # Database connection management with pooling
│   │   ├── query_executor.py   # High-performance SQL execution with caching
│   │   ├── security.py         # Security management and data masking
│   │   ├── schema_extractor.py # Metadata extraction with catalog federation
│   │   ├── analysis_tools.py   # Data analysis and performance monitoring
│   │   ├── logger.py           # Logging configuration
│   │   └── __init__.py
│   └── __init__.py
├── doris_mcp_client/           # MCP client implementation
│   ├── client.py               # Unified MCP client for testing and integration
│   ├── README.md               # Client documentation
│   └── __init__.py
├── logs/                       # Log files directory
├── README.md                   # This documentation
├── .env.example                # Environment variables template
├── requirements.txt            # Python dependencies
├── pyproject.toml              # Project configuration and entry points
├── uv.lock                     # UV package manager lock file
├── generate_requirements.py    # Requirements generation script
├── start_server.sh             # Server startup script
└── restart_server.sh           # Server restart script
```

## Developing New Tools

This section outlines the process for adding new MCP tools to the Doris MCP Server, based on the unified modular architecture with centralized tool management.

### 1. Leverage Existing Utility Modules

The server provides comprehensive utility modules for common database operations:

*   **`doris_mcp_server/utils/db.py`**: Database connection management with connection pooling and health monitoring.
*   **`doris_mcp_server/utils/query_executor.py`**: High-performance SQL execution with advanced caching, optimization, and performance monitoring.
*   **`doris_mcp_server/utils/schema_extractor.py`**: Metadata extraction with full catalog federation support.
*   **`doris_mcp_server/utils/security.py`**: Comprehensive security management, SQL validation, and data masking.
*   **`doris_mcp_server/utils/analysis_tools.py`**: Advanced data analysis and statistical tools.
*   **`doris_mcp_server/utils/config.py`**: Configuration management with validation.

### 2. Implement Tool Logic

Add your new tool to the `DorisToolsManager` class in `doris_mcp_server/tools/tools_manager.py`. The tools manager provides a centralized approach to tool registration and execution with unified interfaces.

**Example:** Adding a new analysis tool:

```python
# In doris_mcp_server/tools/tools_manager.py

async def your_new_analysis_tool(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Your new analysis tool implementation
    
    Args:
        arguments: Tool arguments from MCP client
        
    Returns:
        List of MCP response messages
    """
    try:
        # Use existing utilities
        result = await self.query_executor.execute_sql_for_mcp(
            sql="SELECT COUNT(*) FROM your_table",
            max_rows=arguments.get("max_rows", 100)
        )
        
        return [{
            "type": "text",
            "text": json.dumps(result, ensure_ascii=False, indent=2)
        }]
        
    except Exception as e:
        logger.error(f"Tool execution failed: {str(e)}", exc_info=True)
        return [{
            "type": "text", 
            "text": f"Error: {str(e)}"
        }]
```

### 3. Register the Tool

Add your tool to the `_register_tools` method in the same class:

```python
# In the _register_tools method of DorisToolsManager

@self.mcp.tool(
    name="your_new_analysis_tool",
    description="Description of your new analysis tool",
    inputSchema={
        "type": "object",
        "properties": {
            "parameter1": {
                "type": "string",
                "description": "Description of parameter1"
            },
            "parameter2": {
                "type": "integer", 
                "description": "Description of parameter2",
                "default": 100
            }
        },
        "required": ["parameter1"]
    }
)
async def your_new_analysis_tool_wrapper(arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
    return await self.your_new_analysis_tool(arguments)
```

### 4. Advanced Features

For more complex tools, you can leverage the comprehensive framework:

*   **Advanced Caching**: Use the query executor's built-in caching for enhanced performance
*   **Enterprise Security**: Apply comprehensive SQL validation and data masking through the security manager
*   **Intelligent Prompts**: Use the prompts manager for advanced query generation
*   **Resource Management**: Expose metadata through the resources manager
*   **Performance Monitoring**: Integrate with the analysis tools for monitoring capabilities

### 5. Testing

Test your new tool using the included MCP client:

```python
# Using doris_mcp_client/client.py
from doris_mcp_client.client import DorisUnifiedMCPClient

async def test_new_tool():
    client = DorisUnifiedMCPClient()
    result = await client.call_tool("your_new_analysis_tool", {
        "parameter1": "test_value",
        "parameter2": 50
    })
    print(result)
```

## MCP Client

The project includes a unified MCP client (`doris_mcp_client/`) for testing and integration purposes. The client supports multiple connection modes and provides a convenient interface for interacting with the MCP server.

For detailed client documentation, see [`doris_mcp_client/README.md`](doris_mcp_client/README.md).

## Contributing

Contributions are welcome via Issues or Pull Requests.

## License

This project is licensed under the Apache 2.0 License. See the LICENSE file for details. 

## FAQ

### Q: Why do Qwen3-32b and other small parameter models always fail when calling tools?

**A:** This is a common issue. The main reason is that these models need more explicit guidance to correctly use MCP tools. It's recommended to add the following instruction prompt for the model:

- Chinese version：

```xml
<instruction>
尽可能使用MCP工具完成任务，仔细阅读每个工具的注解、方法名、参数说明等内容。请按照以下步骤操作：

1. 仔细分析用户的问题，从已有的Tools列表中匹配最合适的工具。
2. 确保工具名称、方法名和参数完全按照工具注释中的定义使用，不要自行创造工具名称或参数。
3. 传入参数时，严格遵循工具注释中规定的参数格式和要求。
4. 调用工具时，根据需要直接调用工具，但参数请求参考以下请求格式：{"mcp_sse_call_tool": {"tool_name": "$tools_name", "arguments": "{}"}}
5. 输出结果时，不要包含任何XML标签，仅返回纯文本内容。

<input>
用户问题：user_query
</input>

<output>
返回工具调用结果或最终答案，以及对结果的分析。
</output>
</instruction>
```
- English version：

```xml
<instruction>
Use MCP tools to complete tasks as much as possible. Carefully read the annotations, method names, and parameter descriptions of each tool. Please follow these steps:

1. Carefully analyze the user's question and match the most appropriate tool from the existing Tools list.
2. Ensure tool names, method names, and parameters are used exactly as defined in the tool annotations. Do not create tool names or parameters on your own.
3. When passing parameters, strictly follow the parameter format and requirements specified in the tool annotations.
4. When calling tools, call them directly as needed, but refer to the following request format for parameters: {"mcp_sse_call_tool": {"tool_name": "$tools_name", "arguments": "{}"}}
5. When outputting results, do not include any XML tags, return plain text content only.

<input>
User question: user_query
</input>

<output>
Return tool call results or final answer, along with analysis of the results.
</output>
</instruction>
```

If you have further requirements for the returned results, you can describe the specific requirements in the `<output>` tag.

### Q: How to configure different database connections?

**A:** You can configure database connections in several ways:

1. **Environment Variables** (Recommended):
   ```bash
   export DORIS_HOST="your_doris_host"
   export DORIS_PORT="9030"
   export DORIS_USER="root"
   export DORIS_PASSWORD="your_password"
   ```

2. **Command Line Arguments**:
   ```bash
   doris-mcp-server --db-host your_host --db-port 9030 --db-user root --db-password your_password
   ```

3. **Configuration File**:
   Modify the corresponding configuration items in the `.env` file.

### Q: How to configure BE nodes for monitoring tools?

**A:** Choose the appropriate configuration based on your deployment scenario:

**External Network (Manual Configuration):**
```bash
# Manually specify BE node addresses
DORIS_BE_HOSTS=10.1.1.100,10.1.1.101,10.1.1.102
DORIS_BE_WEBSERVER_PORT=8040
```

**Internal Network (Automatic Discovery):**
```bash
# Leave BE_HOSTS empty for auto-discovery
# DORIS_BE_HOSTS=  # Not set or empty
# System will use 'SHOW BACKENDS' command to get internal IPs
```

### Q: How to use SQL Explain/Profile files with LLM for optimization?

**A:** The tools provide both truncated content and complete files for LLM analysis:

1. **Get Analysis Results:**
   ```json
   {
     "content": "Truncated plan for immediate review",
     "file_path": "/tmp/explain_12345.txt",
     "is_content_truncated": true
   }
   ```

2. **LLM Analysis Workflow:**
   - Review truncated content for quick insights
   - Upload the complete file to your LLM as an attachment
   - Request optimization suggestions or performance analysis
   - Implement recommended improvements

3. **Configure Content Size:**
   ```bash
   MAX_RESPONSE_CONTENT_SIZE=4096  # Adjust as needed
   ```

### Q: How to enable data security and masking features?

**A:** Set the following configurations in your `.env` file:

```bash
# Enable data masking
ENABLE_MASKING=true
# Set authentication type
AUTH_TYPE=token
# Configure token secret
TOKEN_SECRET=your_secret_key
# Set maximum result rows
MAX_RESULT_ROWS=10000
```

### Q: What's the difference between Stdio mode and HTTP mode?

**A:** 

- **Stdio Mode**: Suitable for direct integration with MCP clients (like Cursor), where the client manages the server process
- **HTTP Mode**: Independent web service that supports multiple client connections, suitable for production environments

Recommendations:
- Development and personal use: Stdio mode
- Production and multi-user environments: HTTP mode

### Q: How to resolve connection timeout issues?

**A:** Try the following solutions:

1. **Increase timeout settings**:
   ```bash
   # Set in .env file
   QUERY_TIMEOUT=60
   CONNECTION_TIMEOUT=30
   ```

2. **Check network connectivity**:
   ```bash
   # Test database connection
   curl http://localhost:3000/health
   ```

3. **Optimize connection pool configuration**:
   ```bash
   DORIS_MIN_CONNECTIONS=5
   DORIS_MAX_CONNECTIONS=20
   ```

### Q: How to resolve `at_eof` connection errors? (Fixed in v0.4.1)

**A:** Version 0.4.1 has resolved the critical `at_eof` connection errors. The improvements include:

1. **Enhanced Connection Health Monitoring**: Strict connection state validation before operations
2. **Automatic Retry Mechanism**: Failed queries are automatically retried up to 2 times
3. **Proactive Connection Cleanup**: Automatic detection and cleanup of problematic connections
4. **Connection Diagnostics**: Comprehensive connection health analysis and reporting

If you still encounter connection issues after upgrading to v0.4.1:
```bash
# Check connection diagnostics
# The system now automatically handles connection recovery
# Monitor logs for connection health reports
tail -f logs/doris_mcp_server.log | grep "connection"
```

### Q: How to view server logs?

**A:** Log files are located in the `logs/` directory. You can:

1. **View real-time logs**:
   ```bash
   tail -f logs/doris_mcp_server.log
   ```

2. **Adjust log level**:
   ```bash
   # Set in .env file
   LOG_LEVEL=DEBUG
   ```

3. **Enable audit logging**:
   ```bash
   ENABLE_AUDIT=true
   ```

For other issues, please check GitHub Issues or submit a new issue. 
