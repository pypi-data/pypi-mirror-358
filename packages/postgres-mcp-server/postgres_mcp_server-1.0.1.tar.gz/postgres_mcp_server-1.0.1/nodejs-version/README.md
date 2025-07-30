# PostgreSQL MCP Server (Node.js)

A TypeScript/Node.js implementation of a Model Context Protocol (MCP) server for PostgreSQL databases. This version fixes SSL connection issues and provides robust database connectivity.

## Features

- **Fixed SSL Handling**: Resolves SSL connection issues with automatic fallback
- **Read-only Queries**: Secure SELECT-only query execution
- **MCP Protocol**: Full Model Context Protocol compliance
- **TypeScript**: Type-safe implementation with comprehensive error handling
- **Connection Pooling**: Efficient database connection management

## Installation & Usage

### Via NPX (Recommended)
```bash
# Run directly without installation
npx @mcp-community/postgres-mcp-server "postgresql://user:password@host:5432/database"
```

### Via NPM Global Install
```bash
npm install -g @mcp-community/postgres-mcp-server
postgres-mcp-server "postgresql://user:password@host:5432/database"
```

### Via Local Install
```bash
npm install @mcp-community/postgres-mcp-server
npx postgres-mcp-server "postgresql://user:password@host:5432/database"
```

## SSL Configuration

The server automatically handles SSL connections with proper fallback:

```bash
# Auto SSL (tries SSL, falls back to non-SSL)
npx @mcp-community/postgres-mcp-server "postgresql://user:pass@host:5432/db"

# Disable SSL
npx @mcp-community/postgres-mcp-server "postgresql://user:pass@host:5432/db?sslmode=disable"

# Require SSL
npx @mcp-community/postgres-mcp-server "postgresql://user:pass@host:5432/db?sslmode=require"
```

## MCP Client Configuration

To use this server with MCP clients, you need to configure it in your MCP settings:

### Claude Desktop Configuration

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "postgres": {
      "command": "npx",
      "args": [
        "@mcp-community/postgres-mcp-server",
        "postgresql://username:password@localhost:5432/database"
      ]
    }
  }
}
```

#### Alternative with global installation:
```json
{
  "mcpServers": {
    "postgres": {
      "command": "postgres-mcp-server",
      "args": [
        "postgresql://username:password@localhost:5432/database"
      ]
    }
  }
}
```

### Cline (VS Code Extension)

```json
{
  "mcpServers": {
    "postgres": {
      "command": "npx",
      "args": [
        "@mcp-community/postgres-mcp-server",
        "postgresql://username:password@localhost:5432/database"
      ]
    }
  }
}
```

### SSL Configuration Examples

#### SSL Disabled:
```json
{
  "mcpServers": {
    "postgres-local": {
      "command": "npx",
      "args": [
        "@mcp-community/postgres-mcp-server",
        "postgresql://postgres:password@localhost:5432/mydb?sslmode=disable"
      ]
    }
  }
}
```

#### SSL Required:
```json
{
  "mcpServers": {
    "postgres-prod": {
      "command": "npx",
      "args": [
        "@mcp-community/postgres-mcp-server",
        "postgresql://user:pass@prod-db.example.com:5432/mydb?sslmode=require"
      ]
    }
  }
}
```

## Development

```bash
# Clone and setup
git clone <repository>
cd nodejs-version
npm install

# Development
npm run dev

# Build
npm run build

# Test
npm test

# Lint
npm run lint
```

## MCP Resources & Tools

### Resources
- Database tables exposed as schema resources
- JSON format with column information

### Tools
- `query`: Execute read-only SQL SELECT statements

## Security

- Only SELECT statements allowed
- Read-only transactions
- SQL injection protection
- Secure connection handling

## Requirements

- Node.js 18+
- PostgreSQL database
- Valid database connection string

## License

MIT
