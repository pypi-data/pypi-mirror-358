# PostgreSQL MCP Server

A Python implementation of a Model Context Protocol (MCP) server for PostgreSQL databases. This server provides read-only access to PostgreSQL databases through the MCP protocol, allowing AI assistants to query database schemas and execute SELECT queries safely.

## Features

- **Schema Exploration**: Browse database tables and their column information
- **Read-only Queries**: Execute SELECT queries safely with transaction isolation
- **SSL Support**: Handles SSL connections with proper fallback options
- **Connection Pooling**: Efficient database connection management
- **Security**: Only allows SELECT queries to prevent data modification

## Installation

### Via uvx (Recommended)
```bash
# Run directly without installation
uvx postgres-mcp-server "postgresql://username:password@hostname:port/database"
```

### Via pip
```bash
# Global installation
pip install postgres-mcp-server

# Run
postgres-mcp-server "postgresql://username:password@hostname:port/database"
```

### From Source
1. Clone this repository:
```bash
git clone <repository-url>
cd postgres-mcp
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Running the Server

#### With uvx (easiest)
```bash
uvx postgres-mcp-server "postgresql://username:password@hostname:port/database"
```

#### With pip install
```bash
postgres-mcp-server "postgresql://username:password@hostname:port/database"
```

#### From source
```bash
python postgres_mcp_server.py "postgresql://username:password@hostname:port/database"
```

### Example

#### uvx
```bash
uvx postgres-mcp-server "postgresql://myuser:mypass@localhost:5432/mydb"
```

#### pip
```bash
postgres-mcp-server "postgresql://myuser:mypass@localhost:5432/mydb"
```

#### Source
```bash
python postgres_mcp_server.py "postgresql://myuser:mypass@localhost:5432/mydb"
```

### SSL Configuration

The server automatically handles SSL connections. If no SSL mode is specified in the connection string, it defaults to `prefer` mode, which attempts SSL but falls back to non-SSL if needed.

To explicitly set SSL mode:
```bash
# uvx
uvx postgres-mcp-server "postgresql://user:pass@host:5432/db?sslmode=require"

# pip
postgres-mcp-server "postgresql://user:pass@host:5432/db?sslmode=require"

# source
python postgres_mcp_server.py "postgresql://user:pass@host:5432/db?sslmode=require"
```

Available SSL modes:
- `disable`: No SSL
- `allow`: Try non-SSL, then SSL
- `prefer`: Try SSL, then non-SSL (default)
- `require`: SSL required
- `verify-ca`: SSL required with CA verification
- `verify-full`: SSL required with full verification

## MCP Resources and Tools

### Resources

The server exposes database tables as resources with the following format:
- **URI**: `postgres://host:port/path/table_name/schema`
- **Name**: `"table_name" database schema`
- **Content**: JSON array of column information including name, data type, nullability, and defaults

### Tools

#### `query`
Executes read-only SQL SELECT queries against the database.

**Parameters:**
- `sql` (string): The SQL SELECT query to execute

**Example:**
```json
{
  "name": "query",
  "arguments": {
    "sql": "SELECT id, name FROM users WHERE active = true LIMIT 10"
  }
}
```

## Security Features

1. **Read-only Access**: Only SELECT statements are allowed
2. **Transaction Isolation**: Each query runs in a read-only transaction
3. **Connection Pooling**: Secure connection management with proper cleanup
4. **SQL Injection Protection**: Uses parameterized queries where applicable
5. **Password Sanitization**: Removes passwords from logged URLs

## Testing

Run the test suite:

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest test_postgres_mcp_server.py -v

# Run with coverage
pytest test_postgres_mcp_server.py --cov=postgres_mcp_server --cov-report=html
```

### Test Categories

- **Unit Tests**: Test individual components and functions
- **Integration Tests**: Test complete workflows with mocked database
- **Error Handling**: Test various error conditions and edge cases
- **Security Tests**: Verify SQL injection protection and access controls

## Configuration

### Environment Variables

You can also configure the database connection using environment variables:

```bash
export DATABASE_URL="postgresql://user:password@localhost:5432/dbname"
python postgres_mcp_server.py $DATABASE_URL
```

### Connection Pool Settings

The server uses a connection pool with the following default settings:
- Minimum connections: 1
- Maximum connections: 10
- Connection factory: RealDictCursor (returns dictionaries)

## Error Handling

The server handles various error conditions gracefully:

- **Connection Failures**: Proper error reporting for database connectivity issues
- **Invalid Queries**: Clear error messages for malformed SQL
- **Permission Errors**: Informative messages for access-related problems
- **Resource Not Found**: Appropriate responses for non-existent tables/schemas

## Development

### Project Structure

```
postgres-mcp/
├── postgres_mcp_server.py      # Main server implementation
├── test_postgres_mcp_server.py # Comprehensive test suite
├── requirements.txt            # Python dependencies
├── README.md                  # This file
└── setup.py                   # Package setup (optional)
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## Troubleshooting

### Common Issues

1. **SSL Connection Errors**
   - Solution: Add `?sslmode=disable` to your connection string or ensure SSL certificates are properly configured

2. **Connection Pool Exhaustion**
   - Solution: Ensure proper connection cleanup or adjust pool settings

3. **Permission Denied**
   - Solution: Verify database user has SELECT permissions on target tables

4. **Module Import Errors**
   - Solution: Ensure all dependencies are installed: `pip install -r requirements.txt`

### Logging

The server uses Python's logging module. To enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## License

[Specify your license here]

## Dependencies

- `mcp`: Model Context Protocol SDK
- `psycopg2-binary`: PostgreSQL adapter for Python
- `pytest`: Testing framework
- `pytest-asyncio`: Async testing support
