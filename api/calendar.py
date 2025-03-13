from http.server import BaseHTTPRequestHandler
import json

# In-memory storage for calendar events (in a real app, this would be a database)
events = []

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests to retrieve events"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(events).encode()) 