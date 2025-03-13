#!/usr/bin/env node

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');
const readline = require('readline');

// Path to the MCP script
const mcpScriptPath = path.join(__dirname, 'dist/index.js');

// Check if the MCP script exists
if (!fs.existsSync(mcpScriptPath)) {
  console.error(`Error: MCP script not found at ${mcpScriptPath}`);
  console.error('Please run the build script first: npm run build');
  process.exit(1);
}

// Start the MCP script
const mcpProcess = spawn('node', [mcpScriptPath], {
  stdio: ['pipe', 'pipe', process.stderr]
});

// Create readline interface for reading MCP responses
const rl = readline.createInterface({
  input: mcpProcess.stdout,
  terminal: false
});

// Handle MCP responses
rl.on('line', (line) => {
  try {
    const response = JSON.parse(line);
    console.log('Received MCP response:');
    console.log(JSON.stringify(response, null, 2));
    
    // If this is the init response, send a test request
    if (response.id === 'init') {
      sendTestRequest();
    }
  } catch (error) {
    console.error('Error parsing MCP response:', error.message);
    console.error('Raw response:', line);
  }
});

// Send initialization request
function sendInitRequest() {
  const initRequest = {
    id: 'init',
    method: 'mcp.init',
    params: {}
  };
  
  mcpProcess.stdin.write(JSON.stringify(initRequest) + '\n');
  console.log('Sent initialization request');
}

// Send a test request to list projects
function sendTestRequest() {
  const testRequest = {
    id: 'test',
    method: 'mcp__list_projects',
    params: {}
  };
  
  mcpProcess.stdin.write(JSON.stringify(testRequest) + '\n');
  console.log('Sent test request to list projects');
}

// Handle process termination
mcpProcess.on('close', (code) => {
  console.log(`MCP process exited with code ${code}`);
  process.exit(code);
});

// Start the test
console.log('Starting MCP test...');
sendInitRequest();

// Handle CTRL+C
process.on('SIGINT', () => {
  console.log('Terminating MCP test...');
  mcpProcess.kill();
  process.exit(0);
}); 