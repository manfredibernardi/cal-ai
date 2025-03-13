"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
// Replace the incorrect import with a temporary solution
// import { createClient } from '@vercel/client';
const dotenv = __importStar(require("dotenv"));
const readline = __importStar(require("readline"));
const schema_json_1 = __importDefault(require("./schema.json"));
// Load environment variables
dotenv.config();
// Create a mock Vercel client since the proper client cannot be loaded
console.error('Using temporary mock Vercel client');
const vercelClient = {
    projects: {
        list: async (params) => ({ projects: [{ id: 'mock', name: 'mock-project' }] }),
        create: async (params) => ({ id: 'mock', name: 'mock-project' }),
        delete: async (id, params) => ({ id: 'mock' }),
        update: async (id, params) => ({ id: 'mock', name: 'mock-project' })
    },
    deployments: {
        list: async (params) => ({ deployments: [] }),
        get: async (id, params) => ({ id: 'mock', name: 'mock-deployment' }),
        create: async (params) => ({ id: 'mock', name: 'mock-deployment' }),
        delete: async (id, params) => ({ id: 'mock' })
    },
    domains: {
        add: async (projectId, domain, params) => ({ id: 'mock' }),
        remove: async (projectId, domain, params) => ({ id: 'mock' }),
        list: async (projectId, params) => ({ domains: [] })
    },
    env: {
        add: async (projectId, env, params) => ({ id: 'mock' }),
        list: async (projectId, params) => ({ env: [] })
    }
};
// Define Vercel MCP functions
const vercelFunctions = {
    // Project management
    'mcp__list_projects': async (params) => {
        const { teamId, slug } = params || {};
        const options = {};
        if (teamId)
            options.teamId = teamId;
        if (slug)
            options.slug = slug;
        try {
            const projects = await vercelClient.projects.list(options);
            return projects;
        }
        catch (error) {
            throw new Error(`Failed to list projects: ${error.message}`);
        }
    },
    'mcp__create_project': async (params) => {
        try {
            const project = await vercelClient.projects.create(params);
            return project;
        }
        catch (error) {
            throw new Error(`Failed to create project: ${error.message}`);
        }
    },
    'mcp__delete_project': async (params) => {
        const { idOrName, teamId, slug } = params;
        const options = {};
        if (teamId)
            options.teamId = teamId;
        if (slug)
            options.slug = slug;
        try {
            const result = await vercelClient.projects.delete(idOrName, options);
            return result;
        }
        catch (error) {
            throw new Error(`Failed to delete project: ${error.message}`);
        }
    },
    'mcp__update_project': async (params) => {
        const { idOrName, ...updateParams } = params;
        try {
            const project = await vercelClient.projects.update(idOrName, updateParams);
            return project;
        }
        catch (error) {
            throw new Error(`Failed to update project: ${error.message}`);
        }
    },
    // Deployment management
    'mcp__list_deployments': async (params) => {
        try {
            const deployments = await vercelClient.deployments.list(params);
            return deployments;
        }
        catch (error) {
            throw new Error(`Failed to list deployments: ${error.message}`);
        }
    },
    'mcp__get_deployment': async (params) => {
        const { idOrUrl, teamId, slug, withGitRepoInfo } = params;
        const options = {};
        if (teamId)
            options.teamId = teamId;
        if (slug)
            options.slug = slug;
        if (withGitRepoInfo)
            options.withGitRepoInfo = withGitRepoInfo;
        try {
            const deployment = await vercelClient.deployments.get(idOrUrl, options);
            return deployment;
        }
        catch (error) {
            throw new Error(`Failed to get deployment: ${error.message}`);
        }
    },
    'mcp__create_deployment': async (params) => {
        try {
            const deployment = await vercelClient.deployments.create(params);
            return deployment;
        }
        catch (error) {
            throw new Error(`Failed to create deployment: ${error.message}`);
        }
    },
    'mcp__delete_deployment': async (params) => {
        const { id, teamId, slug, url } = params;
        const options = {};
        if (teamId)
            options.teamId = teamId;
        if (slug)
            options.slug = slug;
        if (url)
            options.url = url;
        try {
            const result = await vercelClient.deployments.delete(id, options);
            return result;
        }
        catch (error) {
            throw new Error(`Failed to delete deployment: ${error.message}`);
        }
    },
    // Domain management
    'mcp__add_domain': async (params) => {
        const { idOrName, domain, teamId, slug } = params;
        const options = {};
        if (teamId)
            options.teamId = teamId;
        if (slug)
            options.slug = slug;
        try {
            const result = await vercelClient.domains.add(idOrName, domain, options);
            return result;
        }
        catch (error) {
            throw new Error(`Failed to add domain: ${error.message}`);
        }
    },
    'mcp__remove_domain': async (params) => {
        const { idOrName, domain, teamId, slug } = params;
        const options = {};
        if (teamId)
            options.teamId = teamId;
        if (slug)
            options.slug = slug;
        try {
            const result = await vercelClient.domains.remove(idOrName, domain, options);
            return result;
        }
        catch (error) {
            throw new Error(`Failed to remove domain: ${error.message}`);
        }
    },
    'mcp__list_domains': async (params) => {
        const { idOrName, teamId, slug } = params;
        const options = {};
        if (teamId)
            options.teamId = teamId;
        if (slug)
            options.slug = slug;
        try {
            const domains = await vercelClient.domains.list(idOrName, options);
            return domains;
        }
        catch (error) {
            throw new Error(`Failed to list domains: ${error.message}`);
        }
    },
    // Environment variables
    'mcp__add_env': async (params) => {
        const { idOrName, env, teamId, slug } = params;
        const options = {};
        if (teamId)
            options.teamId = teamId;
        if (slug)
            options.slug = slug;
        try {
            const result = await vercelClient.env.add(idOrName, env, options);
            return result;
        }
        catch (error) {
            throw new Error(`Failed to add environment variables: ${error.message}`);
        }
    },
    'mcp__list_env': async (params) => {
        const { idOrName, teamId, slug } = params;
        const options = {};
        if (teamId)
            options.teamId = teamId;
        if (slug)
            options.slug = slug;
        try {
            const envVars = await vercelClient.env.list(idOrName, options);
            return envVars;
        }
        catch (error) {
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
function handleInitRequest() {
    const response = {
        id: "init",
        result: {
            schema: schema_json_1.default
        }
    };
    console.log(JSON.stringify(response));
}
// Process MCP requests
rl.on('line', async (line) => {
    try {
        const request = JSON.parse(line);
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
            const response = {
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
            const response = {
                id,
                result
            };
            console.log(JSON.stringify(response));
        }
        catch (error) {
            // Send error response
            const response = {
                id,
                error: {
                    code: 500,
                    message: error.message
                }
            };
            console.log(JSON.stringify(response));
        }
    }
    catch (error) {
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
