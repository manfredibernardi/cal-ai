# Vercel MCP Integration for Cursor

This document explains how to use the Vercel MCP integration with Cursor.

## What is MCP?

Model Context Protocol (MCP) is an open protocol that allows you to provide custom tools to agentic LLMs (Large Language Models) in Cursor's Composer feature. This implementation provides Vercel API integration directly within Cursor.

## Setup

1. Follow the installation steps in the README.md file
2. Configure Cursor to use the MCP server:
   - Open Cursor Settings
   - Navigate to Features > MCP
   - Click "+ Add New MCP Server"
   - Configure the server:
     - Name: Vercel MCP
     - Type: stdio
     - Command: node /path/to/vercel-mcp/dist/index.js
   - Click "Add"

## Available Commands

The following commands are available in Cursor's Composer:

### Project Management

- `mcp__list_projects`: List all projects from Vercel
  - Example: "Show me my Vercel projects"

- `mcp__create_project`: Create a new project with the provided configuration
  - Example: "Create a new Vercel project named 'my-app'"

- `mcp__delete_project`: Delete a specific project
  - Example: "Delete my Vercel project 'my-app'"

- `mcp__update_project`: Update an existing project
  - Example: "Update my Vercel project 'my-app' to use Next.js framework"

### Deployment Management

- `mcp__list_deployments`: List deployments for a project
  - Example: "Show me the deployments for my Vercel project 'my-app'"

- `mcp__get_deployment`: Get deployment by ID or URL
  - Example: "Get details for deployment with ID 'dep_123'"

- `mcp__create_deployment`: Create a new deployment
  - Example: "Deploy my project 'my-app' to Vercel"

- `mcp__delete_deployment`: Delete a deployment by ID or URL
  - Example: "Delete deployment with ID 'dep_123'"

### Domain Management

- `mcp__add_domain`: Add a domain to a project
  - Example: "Add domain 'example.com' to my Vercel project 'my-app'"

- `mcp__remove_domain`: Remove a domain from a project
  - Example: "Remove domain 'example.com' from my Vercel project 'my-app'"

- `mcp__list_domains`: List all domains for a project
  - Example: "Show me the domains for my Vercel project 'my-app'"

### Environment Variables

- `mcp__add_env`: Add environment variables to a project
  - Example: "Add environment variable API_KEY with value 'secret' to my Vercel project 'my-app'"

- `mcp__list_env`: List all environment variables
  - Example: "Show me the environment variables for my Vercel project 'my-app'"

## Example Usage in Cursor

Here are some examples of how to use the Vercel MCP in Cursor's Composer:

1. **Listing Projects**:
   ```
   Show me all my Vercel projects
   ```

2. **Creating a Project**:
   ```
   Create a new Vercel project named 'my-nextjs-app' using Next.js framework
   ```

3. **Adding a Domain**:
   ```
   Add domain 'myapp.example.com' to my Vercel project 'my-nextjs-app'
   ```

4. **Deploying a Project**:
   ```
   Deploy my project 'my-nextjs-app' to Vercel
   ```

## Troubleshooting

If you encounter issues with the Vercel MCP integration:

1. Check that your Vercel API token is valid and has the necessary permissions
2. Verify that the MCP server is running correctly
3. Check the Cursor logs for any error messages
4. Try restarting Cursor and the MCP server

## Security Considerations

- Your Vercel API token is stored locally in the `.env` file
- The token is never sent to any third-party services
- All communication with Vercel's API is done directly from your machine 