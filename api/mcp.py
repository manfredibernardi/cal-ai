import os
import json
import subprocess
from flask import Blueprint, request, jsonify

mcp_blueprint = Blueprint('mcp', __name__, url_prefix='/api')

@mcp_blueprint.route('/mcp', methods=['POST'])
def handle_mcp_request():
    """
    Handle MCP requests and forward them to the MCP script.
    """
    try:
        # Get the MCP script path from environment variables
        mcp_node_path = os.environ.get('MCP_NODE_PATH', '/usr/local/bin/node')
        mcp_script_path = os.environ.get('VERCEL_MCP_SCRIPT', 'vercel-mcp/dist/index.js')
        
        # Get the request data
        request_data = request.get_json()
        if not request_data:
            return jsonify({"error": "No request data provided"}), 400
        
        # Convert the request data to a JSON string
        request_json = json.dumps(request_data)
        
        # Execute the MCP script with the request data
        result = subprocess.run(
            [mcp_node_path, mcp_script_path],
            input=request_json.encode(),
            capture_output=True,
            text=True
        )
        
        # Check if the script executed successfully
        if result.returncode != 0:
            return jsonify({
                "error": "MCP script execution failed",
                "stderr": result.stderr
            }), 500
        
        # Parse the response
        try:
            response_data = json.loads(result.stdout)
            return jsonify(response_data)
        except json.JSONDecodeError:
            return jsonify({
                "error": "Failed to parse MCP response",
                "stdout": result.stdout
            }), 500
    
    except Exception as e:
        return jsonify({
            "error": f"MCP request failed: {str(e)}"
        }), 500 