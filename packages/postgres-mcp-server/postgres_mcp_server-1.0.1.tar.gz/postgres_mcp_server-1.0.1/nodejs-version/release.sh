#!/bin/bash

set -e

echo "PostgreSQL MCP Server (Node.js) - NPM Release Script"
echo "==================================================="

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "Error: package.json not found. Run this script from the nodejs-version directory."
    exit 1
fi

# Check if required tools are installed
echo "Checking required tools..."

if ! command -v node &> /dev/null; then
    echo "Error: Node.js is required"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo "Error: npm is required"
    exit 1
fi

# Install dependencies
echo "Installing dependencies..."
npm install

# Run linting
echo "Running linter..."
npm run lint || echo "Warning: Linting issues found"

# Run tests
echo "Running tests..."
npm test

# Build the project
echo "Building project..."
npm run build

# Check if dist directory was created
if [ ! -d "dist" ]; then
    echo "Error: Build failed - dist directory not found"
    exit 1
fi

echo ""
echo "Package built successfully!"
echo "Files in dist/:"
ls -la dist/

echo ""
echo "To publish to NPM:"
echo "1. Test publish: npm publish --dry-run"
echo "2. Production publish: npm publish"
echo ""
echo "To test with npx:"
echo "npx @mcp-community/postgres-mcp-server --help"
