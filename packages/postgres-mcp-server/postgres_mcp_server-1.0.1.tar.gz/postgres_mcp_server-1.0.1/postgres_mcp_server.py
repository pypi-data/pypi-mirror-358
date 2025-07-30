#!/usr/bin/env python3
"""
PostgreSQL MCP Server
A Model Context Protocol server that provides access to PostgreSQL databases.
"""

import sys
import json
import asyncio
import logging
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse, urlunparse
import psycopg2
from psycopg2 import sql
from psycopg2.extras import RealDictCursor
import psycopg2.pool

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PostgreSQLMCPServer:
    """PostgreSQL MCP Server implementation."""
    
    def __init__(self, database_url: str):
        """Initialize the PostgreSQL MCP server.
        
        Args:
            database_url: PostgreSQL connection URL
        """
        self.database_url = database_url
        self.connection_pool = None
        self.schema_path = "schema"
        
        # Parse the URL and handle SSL mode
        self.parsed_url = urlparse(database_url)
        self._setup_connection_pool()
        
        # Create resource base URL
        self.resource_base_url = self._create_resource_base_url()
        
        # Initialize MCP server
        self.server = Server("postgres-mcp")
        self._setup_handlers()
    
    def _setup_connection_pool(self):
        """Set up the PostgreSQL connection pool with SSL handling."""
        try:
            # Parse connection parameters
            conn_params = {
                'host': self.parsed_url.hostname,
                'port': self.parsed_url.port or 5432,
                'database': self.parsed_url.path.lstrip('/'),
                'user': self.parsed_url.username,
                'password': self.parsed_url.password,
                'cursor_factory': RealDictCursor
            }
            
            # Handle SSL mode - default to 'prefer' to avoid SSL issues
            if 'sslmode' not in self.database_url:
                conn_params['sslmode'] = 'prefer'
            
            # Create connection pool
            self.connection_pool = psycopg2.pool.ThreadedConnectionPool(
                minconn=1,
                maxconn=10,
                **conn_params
            )
            logger.info("PostgreSQL connection pool created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create connection pool: {e}")
            raise
    
    def _create_resource_base_url(self) -> str:
        """Create base URL for resources."""
        # Remove password from URL for security
        safe_url = urlunparse((
            'postgres',
            f"{self.parsed_url.username}@{self.parsed_url.hostname}:{self.parsed_url.port or 5432}",
            self.parsed_url.path,
            self.parsed_url.params,
            self.parsed_url.query,
            self.parsed_url.fragment
        ))
        return safe_url
    
    def _setup_handlers(self):
        """Set up MCP request handlers."""
        
        @self.server.list_resources()
        async def list_resources() -> list[types.Resource]:
            """List available database tables as resources."""
            conn = None
            try:
                conn = self.connection_pool.getconn()
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT table_name 
                        FROM information_schema.tables 
                        WHERE table_schema = 'public'
                        ORDER BY table_name
                    """)
                    tables = cursor.fetchall()
                
                resources = []
                for table in tables:
                    table_name = table['table_name']
                    uri = f"{self.resource_base_url}/{table_name}/{self.schema_path}"
                    resources.append(types.Resource(
                        uri=uri,
                        name=f'"{table_name}" database schema',
                        mimeType="application/json"
                    ))
                
                return resources
                
            except Exception as e:
                logger.error(f"Error listing resources: {e}")
                raise
            finally:
                if conn:
                    self.connection_pool.putconn(conn)
        
        @self.server.read_resource()
        async def read_resource(uri: str) -> str:
            """Read a specific table schema."""
            try:
                parsed_uri = urlparse(uri)
                path_components = parsed_uri.path.strip('/').split('/')
                
                if len(path_components) < 2:
                    raise ValueError("Invalid resource URI format")
                
                schema = path_components[-1]
                table_name = path_components[-2]
                
                if schema != self.schema_path:
                    raise ValueError("Invalid resource URI - schema path mismatch")
                
                conn = None
                try:
                    conn = self.connection_pool.getconn()
                    with conn.cursor() as cursor:
                        cursor.execute("""
                            SELECT column_name, data_type, is_nullable, column_default
                            FROM information_schema.columns 
                            WHERE table_name = %s AND table_schema = 'public'
                            ORDER BY ordinal_position
                        """, (table_name,))
                        columns = cursor.fetchall()
                    
                    return json.dumps([dict(row) for row in columns], indent=2)
                    
                finally:
                    if conn:
                        self.connection_pool.putconn(conn)
                        
            except Exception as e:
                logger.error(f"Error reading resource {uri}: {e}")
                raise
        
        @self.server.list_tools()
        async def list_tools() -> list[types.Tool]:
            """List available tools."""
            return [
                types.Tool(
                    name="query",
                    description="Run a read-only SQL query against the PostgreSQL database",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "sql": {
                                "type": "string",
                                "description": "The SQL query to execute (SELECT statements only)"
                            }
                        },
                        "required": ["sql"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict[str, Any]) -> list[types.TextContent]:
            """Execute tool calls."""
            if name != "query":
                raise ValueError(f"Unknown tool: {name}")
            
            sql_query = arguments.get("sql")
            if not sql_query:
                raise ValueError("SQL query is required")
            
            # Basic security check - only allow SELECT statements
            sql_query_upper = sql_query.strip().upper()
            if not sql_query_upper.startswith("SELECT"):
                raise ValueError("Only SELECT queries are allowed for security reasons")
            
            conn = None
            try:
                conn = self.connection_pool.getconn()
                conn.set_session(readonly=True)
                
                with conn.cursor() as cursor:
                    cursor.execute("BEGIN TRANSACTION READ ONLY")
                    cursor.execute(sql_query)
                    results = cursor.fetchall()
                    cursor.execute("ROLLBACK")
                
                # Convert results to JSON
                result_data = [dict(row) for row in results]
                return [types.TextContent(
                    type="text",
                    text=json.dumps(result_data, indent=2, default=str)
                )]
                
            except Exception as e:
                logger.error(f"Error executing query: {e}")
                if conn:
                    try:
                        with conn.cursor() as cursor:
                            cursor.execute("ROLLBACK")
                    except:
                        pass
                raise ValueError(f"Query execution failed: {e}")
            finally:
                if conn:
                    self.connection_pool.putconn(conn)
    
    async def run(self):
        """Run the MCP server."""
        try:
            async with stdio_server() as (read_stream, write_stream):
                await self.server.run(
                    read_stream,
                    write_stream,
                    self.server.create_initialization_options()
                )
        except Exception as e:
            logger.error(f"Server error: {e}")
            raise
        finally:
            if self.connection_pool:
                self.connection_pool.closeall()


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Please provide a database URL as a command-line argument", file=sys.stderr)
        print("Usage: python postgres_mcp_server.py <database_url>", file=sys.stderr)
        print("Example: python postgres_mcp_server.py postgresql://user:password@localhost:5432/dbname", file=sys.stderr)
        sys.exit(1)
    
    database_url = sys.argv[1]
    
    try:
        server = PostgreSQLMCPServer(database_url)
        asyncio.run(server.run())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
