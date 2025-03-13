from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Set default response
        status_code = 200
        response_content = 'Hello, World!'
        content_type = 'text/plain'
        
        # Handle different routes
        if self.path == '/':
            # Root path - return welcome message
            response_content = 'Welcome to Cal AI!'
        elif self.path == '/api/health':
            # Health check endpoint
            content_type = 'application/json'
            response_content = json.dumps({
                'status': 'ok',
                'message': 'Service is healthy'
            })
        else:
            # Handle unknown paths
            status_code = 404
            response_content = 'Not Found'
        
        # Send response
        self.send_response(status_code)
        self.send_header('Content-type', content_type)
        self.end_headers()
        self.wfile.write(response_content.encode('utf-8'))
        return 