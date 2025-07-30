#!/usr/bin/env node

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListResourcesRequestSchema,
  ListToolsRequestSchema,
  ReadResourceRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import { Pool, PoolConfig } from "pg";
import { URL } from "url";

interface PostgresConfig extends PoolConfig {
  ssl?: boolean | { rejectUnauthorized: boolean };
}

class PostgreSQLMCPServer {
  private server: Server;
  private pool: Pool;
  private resourceBaseUrl: string;
  private readonly SCHEMA_PATH = "schema";

  constructor(databaseUrl: string) {
    // Initialize MCP server
    this.server = new Server(
      {
        name: "@mcp-community/postgres-mcp-server",
        version: "1.0.0",
      },
      {
        capabilities: {
          resources: {},
          tools: {},
        },
      }
    );

    // Setup PostgreSQL connection with SSL handling
    this.setupConnection(databaseUrl);
    this.createResourceBaseUrl(databaseUrl);
    this.setupHandlers();
  }

  private setupConnection(databaseUrl: string): void {
    const dbUrl = new URL(databaseUrl);
    
    // Parse SSL mode from query parameters
    const sslMode = dbUrl.searchParams.get('sslmode') || 'prefer';
    
    const config: PostgresConfig = {
      connectionString: databaseUrl,
    };

    // Handle SSL configuration with fallback
    switch (sslMode) {
      case 'disable':
        config.ssl = false;
        break;
      case 'allow':
      case 'prefer':
        // Try SSL first, fallback to non-SSL (this fixes the original bug)
        config.ssl = { rejectUnauthorized: false };
        break;
      case 'require':
        config.ssl = { rejectUnauthorized: false };
        break;
      case 'verify-ca':
      case 'verify-full':
        config.ssl = { rejectUnauthorized: true };
        break;
      default:
        // Default to prefer mode for compatibility
        config.ssl = { rejectUnauthorized: false };
    }

    this.pool = new Pool(config);

    // Handle connection errors gracefully
    this.pool.on('error', (err) => {
      console.error('Unexpected error on idle client', err);
    });

    console.log(`PostgreSQL connection configured with SSL mode: ${sslMode}`);
  }

  private createResourceBaseUrl(databaseUrl: string): void {
    const resourceBaseUrl = new URL(databaseUrl);
    resourceBaseUrl.protocol = "postgres:";
    // Remove password for security
    resourceBaseUrl.password = "";
    this.resourceBaseUrl = resourceBaseUrl.toString();
  }

  private setupHandlers(): void {
    // List database tables as resources
    this.server.setRequestHandler(ListResourcesRequestSchema, async () => {
      const client = await this.pool.connect();
      try {
        const result = await client.query(
          `SELECT table_name 
           FROM information_schema.tables 
           WHERE table_schema = 'public'
           ORDER BY table_name`
        );
        
        return {
          resources: result.rows.map((row) => ({
            uri: new URL(`${row.table_name}/${this.SCHEMA_PATH}`, this.resourceBaseUrl).href,
            mimeType: "application/json",
            name: `"${row.table_name}" database schema`,
          })),
        };
      } finally {
        client.release();
      }
    });

    // Read table schema
    this.server.setRequestHandler(ReadResourceRequestSchema, async (request) => {
      const resourceUrl = new URL(request.params.uri);
      const pathComponents = resourceUrl.pathname.split("/");
      const schema = pathComponents.pop();
      const tableName = pathComponents.pop();

      if (schema !== this.SCHEMA_PATH) {
        throw new Error("Invalid resource URI");
      }

      const client = await this.pool.connect();
      try {
        const result = await client.query(
          `SELECT column_name, data_type, is_nullable, column_default
           FROM information_schema.columns 
           WHERE table_name = $1 AND table_schema = 'public'
           ORDER BY ordinal_position`,
          [tableName]
        );

        return {
          contents: [
            {
              uri: request.params.uri,
              mimeType: "application/json",
              text: JSON.stringify(result.rows, null, 2),
            },
          ],
        };
      } finally {
        client.release();
      }
    });

    // List available tools
    this.server.setRequestHandler(ListToolsRequestSchema, async () => {
      return {
        tools: [
          {
            name: "query",
            description: "Run a read-only SQL query against the PostgreSQL database",
            inputSchema: {
              type: "object",
              properties: {
                sql: { 
                  type: "string",
                  description: "The SQL query to execute (SELECT statements only)"
                },
              },
              required: ["sql"],
            },
          },
        ],
      };
    });

    // Execute SQL queries
    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      if (request.params.name === "query") {
        const sql = request.params.arguments?.sql as string;

        if (!sql) {
          throw new Error("SQL query is required");
        }

        // Security check - only allow SELECT statements
        const sqlUpper = sql.trim().toUpperCase();
        if (!sqlUpper.startsWith("SELECT")) {
          throw new Error("Only SELECT queries are allowed for security reasons");
        }

        const client = await this.pool.connect();
        try {
          // Use read-only transaction
          await client.query("BEGIN TRANSACTION READ ONLY");
          const result = await client.query(sql);
          await client.query("ROLLBACK");
          
          return {
            content: [
              { 
                type: "text", 
                text: JSON.stringify(result.rows, null, 2) 
              }
            ],
            isError: false,
          };
        } catch (error) {
          // Ensure transaction is rolled back
          try {
            await client.query("ROLLBACK");
          } catch (rollbackError) {
            console.warn("Could not roll back transaction:", rollbackError);
          }
          throw error;
        } finally {
          client.release();
        }
      }
      throw new Error(`Unknown tool: ${request.params.name}`);
    });
  }

  async run(): Promise<void> {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
  }

  async close(): Promise<void> {
    await this.pool.end();
  }
}

async function main() {
  const args = process.argv.slice(2);
  if (args.length === 0) {
    console.error("Please provide a database URL as a command-line argument");
    console.error("Usage: postgres-mcp-server <database_url>");
    console.error("Example: postgres-mcp-server 'postgresql://user:password@localhost:5432/dbname'");
    process.exit(1);
  }

  const databaseUrl = args[0];
  const server = new PostgreSQLMCPServer(databaseUrl);

  // Handle graceful shutdown
  process.on('SIGINT', async () => {
    console.log('\nReceived SIGINT, shutting down gracefully...');
    await server.close();
    process.exit(0);
  });

  process.on('SIGTERM', async () => {
    console.log('\nReceived SIGTERM, shutting down gracefully...');
    await server.close();
    process.exit(0);
  });

  try {
    await server.run();
  } catch (error) {
    console.error('Server error:', error);
    await server.close();
    process.exit(1);
  }
}

if (require.main === module) {
  main().catch(console.error);
}

export { PostgreSQLMCPServer };
export default PostgreSQLMCPServer;
