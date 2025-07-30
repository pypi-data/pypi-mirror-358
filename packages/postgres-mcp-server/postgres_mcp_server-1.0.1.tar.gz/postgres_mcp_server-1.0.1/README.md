# PostgreSQL MCP Server

A Model Context Protocol (MCP) server for PostgreSQL databases. This server provides read-only access to PostgreSQL databases through the MCP protocol, allowing AI assistants to query database schemas and execute SELECT queries safely.

## Features

- **Schema Exploration**: Browse database tables and their column information
- **Read-only Queries**: Execute SELECT queries safely with transaction isolation
- **SSL Support**: Handles SSL connections with proper fallback options
- **Connection Pooling**: Efficient database connection management
- **Security**: Only allows SELECT queries to prevent data modification

## Installation

Install with pip:
```bash
pip install postgres-mcp-server
```

Or run directly with uvx (recommended):
```bash
uvx postgres-mcp-server "postgresql://username:password@hostname:port/database"
```

## MCP Client Configuration

To use this server with MCP clients, configure it in your MCP settings:

### Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "postgres": {
      "command": "uvx",
      "args": [
        "postgres-mcp-server",
        "postgresql://username:password@localhost:5432/database"
      ]
    }
  }
}
```

**Configuration file locations:**
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

### Environment Variables

For security, avoid hardcoding credentials:

```json
{
  "mcpServers": {
    "postgres": {
      "command": "uvx",
      "args": [
        "postgres-mcp-server",
        "postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}"
      ],
      "env": {
        "POSTGRES_HOST": "localhost",
        "POSTGRES_PORT": "5432", 
        "POSTGRES_DB": "database",
        "POSTGRES_USER": "username",
        "POSTGRES_PASSWORD": "password"
      }
    }
  }
}
```

### SSL Configuration Examples

#### Development (SSL disabled):
```json
{
  "mcpServers": {
    "postgres-dev": {
      "command": "uvx",
      "args": [
        "postgres-mcp-server",
        "postgresql://postgres:password@localhost:5432/mydb?sslmode=disable"
      ]
    }
  }
}
```

#### Production (SSL required):
```json
{
  "mcpServers": {
    "postgres-prod": {
      "command": "uvx", 
      "args": [
        "postgres-mcp-server",
        "postgresql://user:pass@prod-db.example.com:5432/mydb?sslmode=require"
      ]
    }
  }
}
```

### Multiple Databases

Configure multiple PostgreSQL connections:

```json
{
  "mcpServers": {
    "postgres-main": {
      "command": "uvx",
      "args": [
        "postgres-mcp-server",
        "postgresql://user:pass@main-db:5432/main_database"
      ]
    },
    "postgres-analytics": {
      "command": "uvx",
      "args": [
        "postgres-mcp-server",
        "postgresql://user:pass@analytics-db:5432/analytics_database" 
      ]
    }
  }
}
```

## SSL Support

The server automatically handles SSL connections with these modes:
- `disable`: No SSL
- `allow`: Try non-SSL, then SSL  
- `prefer`: Try SSL, then non-SSL (default)
- `require`: SSL required
- `verify-ca`: SSL with CA verification
- `verify-full`: SSL with full verification

## Usage in MCP Clients

Once configured, interact with your PostgreSQL database through natural language:

**"What tables are available in the database?"** - Lists all tables with their schemas

**"Show me the first 10 users"** - Executes: `SELECT * FROM users LIMIT 10`

**"Find recent orders with customer info"** - Builds complex JOINs automatically

All queries are restricted to SELECT statements for security.

## License

MIT
