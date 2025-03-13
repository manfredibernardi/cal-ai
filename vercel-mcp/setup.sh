#!/bin/bash

# Exit on error
set -e

echo "Setting up Vercel MCP for Cursor..."

# Install dependencies
echo "Installing dependencies..."
npm install

# Build TypeScript code
echo "Building TypeScript code..."
npm run build

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
  echo "Creating .env file..."
  cp .env.example .env
  echo "Please edit .env file and add your Vercel API token"
fi

# Make the script executable
chmod +x dist/index.js

echo "Setup complete!"
echo "To run the MCP server, use: npm start"
echo "To configure Cursor, add a new MCP server with:"
echo "  - Name: Vercel MCP"
echo "  - Type: stdio"
echo "  - Command: node $(pwd)/dist/index.js" 