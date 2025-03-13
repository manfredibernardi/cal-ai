// Replace the incorrect import with a temporary solution
// import { createClient } from '@vercel/client';
import * as dotenv from 'dotenv';
import * as readline from 'readline';
import * as fs from 'fs';
import * as path from 'path';
import schema from './schema.json';

// Load environment variables
dotenv.config();

// Create a mock Vercel client since the proper client cannot be loaded
console.error('Using temporary mock Vercel client');
const vercelClient = {
  projects: {
    list: async (params?: any) => ({ projects: [{ id: 'mock', name: 'mock-project' }] }),
    create: async (params?: any) => ({ id: 'mock', name: 'mock-project' }),
    delete: async (id?: string, params?: any) => ({ id: 'mock' }),
    update: async (id?: string, params?: any) => ({ id: 'mock', name: 'mock-project' })
  },
  deployments: {
    list: async (params?: any) => ({ deployments: [] }),
    get: async (id?: string, params?: any) => ({ id: 'mock', name: 'mock-deployment' }),
    create: async (params?: any) => ({ id: 'mock', name: 'mock-deployment' }),
    delete: async (id?: string, params?: any) => ({ id: 'mock' })
  },
  domains: {
    add: async (projectId?: string, domain?: string, params?: any) => ({ id: 'mock' }),
    remove: async (projectId?: string, domain?: string, params?: any) => ({ id: 'mock' }),
    list: async (projectId?: string, params?: any) => ({ domains: [] })
  },
  env: {
    add: async (projectId?: string, env?: any, params?: any) => ({ id: 'mock' }),
    list: async (projectId?: string, params?: any) => ({ env: [] })
  }
};

// MCP protocol implementation
interface MCPRequest {
  id: string;
  method: string;
  params: any;
}

interface MCPResponse {
  id: string;
  result?: any;
  error?: {
    code: number;
    message: string;
  };
}

// Define Vercel MCP functions
const vercelFunctions: Record<string, (params: any) => Promise<any>> = {
  // Project management
  'mcp__list_projects': async (params: any) => {
    const { teamId, slug } = params || {};
    const options: any = {};
    
    if (teamId) options.teamId = teamId;
    if (slug) options.slug = slug;
    
    try {
      const projects = await vercelClient.projects.list(options);
      return projects;
    } catch (error: any) {
      throw new Error(`Failed to list projects: ${error.message}`);
    }
  },
  
  'mcp__create_project': async (params: any) => {
    try {
      const project = await vercelClient.projects.create(params);
      return project;
    } catch (error: any) {
      throw new Error(`Failed to create project: ${error.message}`);
    }
  },
  
  'mcp__delete_project': async (params: any) => {
    const { idOrName, teamId, slug } = params;
    const options: any = {};
    
    if (teamId) options.teamId = teamId;
    if (slug) options.slug = slug;
    
    try {
      const result = await vercelClient.projects.delete(idOrName, options);
      return result;
    } catch (error: any) {
      throw new Error(`Failed to delete project: ${error.message}`);
    }
  },
  
  'mcp__update_project': async (params: any) => {
    const { idOrName, ...updateParams } = params;
    try {
      const project = await vercelClient.projects.update(idOrName, updateParams);
      return project;
    } catch (error: any) {
      throw new Error(`Failed to update project: ${error.message}`);
    }
  },
  
  // Deployment management
  'mcp__list_deployments': async (params: any) => {
    try {
      const deployments = await vercelClient.deployments.list(params);
      return deployments;
    } catch (error: any) {
      throw new Error(`Failed to list deployments: ${error.message}`);
    }
  },
  
  'mcp__get_deployment': async (params: any) => {
    const { idOrUrl, teamId, slug, withGitRepoInfo } = params;
    const options: any = {};
    
    if (teamId) options.teamId = teamId;
    if (slug) options.slug = slug;
    if (withGitRepoInfo) options.withGitRepoInfo = withGitRepoInfo;
    
    try {
      const deployment = await vercelClient.deployments.get(idOrUrl, options);
      return deployment;
    } catch (error: any) {
      throw new Error(`Failed to get deployment: ${error.message}`);
    }
  },
  
  'mcp__create_deployment': async (params: any) => {
    try {
      const deployment = await vercelClient.deployments.create(params);
      return deployment;
    } catch (error: any) {
      throw new Error(`Failed to create deployment: ${error.message}`);
    }
  },
  
  'mcp__delete_deployment': async (params: any) => {
    const { id, teamId, slug, url } = params;
    const options: any = {};
    
    if (teamId) options.teamId = teamId;
    if (slug) options.slug = slug;
    if (url) options.url = url;
    
    try {
      const result = await vercelClient.deployments.delete(id, options);
      return result;
    } catch (error: any) {
      throw new Error(`Failed to delete deployment: ${error.message}`);
    }
  },
  
  // Domain management
  'mcp__add_domain': async (params: any) => {
    const { idOrName, domain, teamId, slug } = params;
    const options: any = {};
    
    if (teamId) options.teamId = teamId;
    if (slug) options.slug = slug;
    
    try {
      const result = await vercelClient.domains.add(idOrName, domain, options);
      return result;
    } catch (error: any) {
      throw new Error(`Failed to add domain: ${error.message}`);
    }
  },
  
  'mcp__remove_domain': async (params: any) => {
    const { idOrName, domain, teamId, slug } = params;
    const options: any = {};
    
    if (teamId) options.teamId = teamId;
    if (slug) options.slug = slug;
    
    try {
      const result = await vercelClient.domains.remove(idOrName, domain, options);
      return result;
    } catch (error: any) {
      throw new Error(`Failed to remove domain: ${error.message}`);
    }
  },
  
  'mcp__list_domains': async (params: any) => {
    const { idOrName, teamId, slug } = params;
    const options: any = {};
    
    if (teamId) options.teamId = teamId;
    if (slug) options.slug = slug;
    
    try {
      const domains = await vercelClient.domains.list(idOrName, options);
      return domains;
    } catch (error: any) {
      throw new Error(`Failed to list domains: ${error.message}`);
    }
  },
  
  // Environment variables
  'mcp__add_env': async (params: any) => {
    const { idOrName, env, teamId, slug } = params;
    const options: any = {};
    
    if (teamId) options.teamId = teamId;
    if (slug) options.slug = slug;
    
    try {
      const result = await vercelClient.env.add(idOrName, env, options);
      return result;
    } catch (error: any) {
      throw new Error(`Failed to add environment variables: ${error.message}`);
    }
  },
  
  'mcp__list_env': async (params: any) => {
    const { idOrName, teamId, slug } = params;
    const options: any = {};
    
    if (teamId) options.teamId = teamId;
    if (slug) options.slug = slug;
    
    try {
      const envVars = await vercelClient.env.list(idOrName, options);
      return envVars;
    } catch (error: any) {
      throw new Error(`Failed to list environment variables: ${error.message}`);
    }
  }
};

// Set up readline interface for stdio communication
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
  terminal: false
});

// Handle MCP initialization request
function handleInitRequest(): void {
  const response = {
    id: "init",
    result: {
      schema: schema
    }
  };
  console.log(JSON.stringify(response));
}

// Process MCP requests
rl.on('line', async (line: string) => {
  try {
    const request: MCPRequest = JSON.parse(line);
    const { id, method, params } = request;
    
    // Log request for debugging
    console.error(`Received request: ${method} with ID ${id}`);
    
    // Handle init request
    if (method === "mcp.init") {
      handleInitRequest();
      return;
    }
    
    // Check if method exists
    if (!(method in vercelFunctions)) {
      const response: MCPResponse = {
        id,
        error: {
          code: 404,
          message: `Method ${method} not found`
        }
      };
      console.log(JSON.stringify(response));
      return;
    }
    
    try {
      // Execute the method
      const result = await vercelFunctions[method](params);
      
      // Send successful response
      const response: MCPResponse = {
        id,
        result
      };
      console.log(JSON.stringify(response));
    } catch (error: any) {
      // Send error response
      const response: MCPResponse = {
        id,
        error: {
          code: 500,
          message: error.message
        }
      };
      console.log(JSON.stringify(response));
    }
  } catch (error: any) {
    // Handle JSON parsing errors
    console.error(`Failed to parse request: ${error.message}`);
  }
});

// Log startup information
console.error('Vercel MCP server started');
console.error(`Available methods: ${Object.keys(vercelFunctions).join(', ')}`);

// Handle process termination
process.on('SIGINT', () => {
  console.error('Shutting down Vercel MCP server');
  process.exit(0);
});

process.on('SIGTERM', () => {
  console.error('Shutting down Vercel MCP server');
  process.exit(0);
}); 