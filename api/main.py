import json
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

# In-memory storage for calendar events (in a real app, this would be a database)
events = []

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests"""
        url_parts = urlparse(self.path)
        path = url_parts.path
        query_params = parse_qs(url_parts.query)
        
        # Root API endpoint
        if path == '/' or path == '':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'message': 'API is working!',
                'endpoints': [
                    '/api',
                    '/api/calendar'
                ]
            }).encode())
            return
            
        # Calendar endpoint
        if path == '/calendar':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            # Filter by event_id if provided
            if 'id' in query_params:
                event_id = query_params['id'][0]
                filtered_events = [event for event in events if event.get('id') == event_id]
                self.wfile.write(json.dumps(filtered_events).encode())
            else:
                self.wfile.write(json.dumps(events).encode())
            return
            
        # Default: Not found
        self.send_response(404)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({
            'error': 'Not Found',
            'path': path
        }).encode())
    
    def do_POST(self):
        """Handle POST requests"""
        url_parts = urlparse(self.path)
        path = url_parts.path
        
        # Calendar endpoint
        if path == '/calendar':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                event_data = json.loads(post_data.decode())
                
                # Validate required fields
                if not all(key in event_data for key in ['title', 'start_time']):
                    self.send_response(400)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        'error': 'Missing required fields. Required: title, start_time'
                    }).encode())
                    return
                
                # Generate a simple ID (in a real app, use UUID or database-generated ID)
                event_data['id'] = str(len(events) + 1)
                events.append(event_data)
                
                self.send_response(201)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(event_data).encode())
                return
            except json.JSONDecodeError:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Invalid JSON'}).encode())
                return
        
        # Default: Not found
        self.send_response(404)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({
            'error': 'Not Found',
            'path': path
        }).encode()) 