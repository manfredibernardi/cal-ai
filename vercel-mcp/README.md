# Vercel MCP for Cursor

This is a Model Context Protocol (MCP) implementation for Vercel integration with Cursor. It allows you to interact with Vercel's API directly from Cursor's Composer feature.

## Features

- Project management (list, create, update, delete)
- Deployment management (list, create, get, delete)
- Domain management (add, remove, list)
- Environment variable management (add, list)

## Installation

1. Clone this repository
2. Install dependencies:
   ```bash
   npm install
   ```
3. Build the TypeScript code:
   ```bash
   npm run build
   ```
4. Copy `.env.example` to `.env` and add your Vercel API token:
   ```bash
   cp .env.example .env
   ```
5. Edit `.env` and add your Vercel API token

## Usage

### Running the MCP Server

```bash
npm start
```

### Configuring Cursor

1. Open Cursor Settings
2. Navigate to Features > MCP
3. Click "+ Add New MCP Server"
4. Configure the server:
   - Name: Vercel MCP
   - Type: stdio
   - Command: node /path/to/vercel-mcp/dist/index.js
5. Click "Add"

## Available Commands

- `mcp__list_projects`: List all projects
- `mcp__create_project`: Create a new project
- `mcp__delete_project`: Delete a project
- `mcp__update_project`: Update a project
- `mcp__list_deployments`: List deployments
- `mcp__get_deployment`: Get deployment details
- `mcp__create_deployment`: Create a new deployment
- `mcp__delete_deployment`: Delete a deployment
- `mcp__add_domain`: Add a domain to a project
- `mcp__remove_domain`: Remove a domain from a project
- `mcp__list_domains`: List domains for a project
- `mcp__add_env`: Add environment variables
- `mcp__list_env`: List environment variables

## Development

To run in development mode with hot reloading:

```bash
npm run dev
```

## License

MIT 