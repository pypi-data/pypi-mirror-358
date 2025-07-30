import { PostgreSQLMCPServer } from '../src/index';
import { Pool } from 'pg';

// Mock pg module
jest.mock('pg', () => ({
  Pool: jest.fn().mockImplementation(() => ({
    connect: jest.fn(),
    end: jest.fn(),
    on: jest.fn(),
  })),
}));

// Mock MCP SDK
jest.mock('@modelcontextprotocol/sdk/server/index.js', () => ({
  Server: jest.fn().mockImplementation(() => ({
    setRequestHandler: jest.fn(),
    connect: jest.fn(),
  })),
}));

jest.mock('@modelcontextprotocol/sdk/server/stdio.js', () => ({
  StdioServerTransport: jest.fn(),
}));

describe('PostgreSQLMCPServer', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('SSL Configuration', () => {
    it('should handle default SSL mode (prefer)', () => {
      const server = new PostgreSQLMCPServer('postgresql://user:pass@localhost:5432/db');
      expect(Pool).toHaveBeenCalledWith(
        expect.objectContaining({
          ssl: { rejectUnauthorized: false },
        })
      );
    });

    it('should handle disabled SSL', () => {
      const server = new PostgreSQLMCPServer('postgresql://user:pass@localhost:5432/db?sslmode=disable');
      expect(Pool).toHaveBeenCalledWith(
        expect.objectContaining({
          ssl: false,
        })
      );
    });

    it('should handle required SSL', () => {
      const server = new PostgreSQLMCPServer('postgresql://user:pass@localhost:5432/db?sslmode=require');
      expect(Pool).toHaveBeenCalledWith(
        expect.objectContaining({
          ssl: { rejectUnauthorized: false },
        })
      );
    });

    it('should handle verify-full SSL', () => {
      const server = new PostgreSQLMCPServer('postgresql://user:pass@localhost:5432/db?sslmode=verify-full');
      expect(Pool).toHaveBeenCalledWith(
        expect.objectContaining({
          ssl: { rejectUnauthorized: true },
        })
      );
    });
  });

  describe('Resource Base URL', () => {
    it('should remove password from resource URL', () => {
      const server = new PostgreSQLMCPServer('postgresql://user:password@localhost:5432/db');
      // Access private property for testing
      const resourceBaseUrl = (server as any).resourceBaseUrl;
      expect(resourceBaseUrl).not.toContain('password');
      expect(resourceBaseUrl).toContain('user');
    });
  });

  describe('Server initialization', () => {
    it('should create server with correct name and version', () => {
      const { Server } = require('@modelcontextprotocol/sdk/server/index.js');
      new PostgreSQLMCPServer('postgresql://user:pass@localhost:5432/db');
      
      expect(Server).toHaveBeenCalledWith(
        {
          name: '@mcp-community/postgres-mcp-server',
          version: '1.0.0',
        },
        {
          capabilities: {
            resources: {},
            tools: {},
          },
        }
      );
    });
  });
});
