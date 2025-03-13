// Vercel MCP Configuration Script
const { execSync } = require('child_process');
const path = require('path');
const fs = require('fs');

// Get the absolute path to the MCP implementation
const projectRoot = __dirname;
const MCP_PATH = '/usr/local/bin/node';
const VERCEL_MCP_PATH = path.join(projectRoot, 'vercel-mcp/dist/index.js');

console.log(`Configuring Vercel MCP with Node path: ${MCP_PATH}`);
console.log(`Vercel MCP script path: ${VERCEL_MCP_PATH}`);

// Check if the MCP implementation exists
if (!fs.existsSync(VERCEL_MCP_PATH)) {
  console.error(`Error: Vercel MCP script not found at ${VERCEL_MCP_PATH}`);
  console.error('Please run the setup script in the vercel-mcp directory first.');
  process.exit(1);
}

try {
  // Execute MCP configuration
  execSync(`vercel env add MCP_NODE_PATH ${MCP_PATH}`);
  console.log('Successfully configured Node.js path for Vercel MCP');
  
  // Set up Vercel MCP handler
  execSync(`vercel env add VERCEL_MCP_SCRIPT ${VERCEL_MCP_PATH}`);
  console.log('Successfully configured Vercel MCP script path');
  
  console.log('Vercel MCP configuration complete');
} catch (error) {
  console.error('Error configuring Vercel MCP:', error.message);
  process.exit(1);
} 