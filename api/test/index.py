import json
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests and log path information"""
        url_parts = urlparse(self.path)
        path = url_parts.path
        query_params = parse_qs(url_parts.query)
        
        # Create a response with debug information
        response = {
            "message": "Test endpoint",
            "debug": {
                "path": path,
                "full_path": self.path,
                "query_params": query_params
            }
        }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response, indent=2).encode()) 