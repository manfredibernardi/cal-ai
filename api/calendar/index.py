import json
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

# In-memory storage for calendar events (in a real app, this would be a database)
events = []

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests to retrieve events"""
        url_parts = urlparse(self.path)
        path = url_parts.path
        query_params = parse_qs(url_parts.query)
        
        # Get all events - Vercel routes to /api/calendar, so we check for / or empty path
        if path == '/' or path == '':
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
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write('Not Found'.encode())
    
    def do_POST(self):
        """Handle POST requests to create new events"""
        if self.path == '/' or self.path == '':
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
            except json.JSONDecodeError:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Invalid JSON'}).encode())
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write('Not Found'.encode())
    
    def do_PUT(self):
        """Handle PUT requests to update existing events"""
        url_parts = urlparse(self.path)
        path = url_parts.path
        query_params = parse_qs(url_parts.query)
        
        if path == '/' or path == '':
            if 'id' not in query_params:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Event ID is required'}).encode())
                return
                
            event_id = query_params['id'][0]
            content_length = int(self.headers['Content-Length'])
            put_data = self.rfile.read(content_length)
            
            try:
                updated_data = json.loads(put_data.decode())
                
                # Find the event to update
                for i, event in enumerate(events):
                    if event.get('id') == event_id:
                        # Update the event with new data while preserving the ID
                        updated_data['id'] = event_id
                        events[i] = updated_data
                        
                        self.send_response(200)
                        self.send_header('Content-type', 'application/json')
                        self.end_headers()
                        self.wfile.write(json.dumps(updated_data).encode())
                        return
                
                # If we get here, the event wasn't found
                self.send_response(404)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Event not found'}).encode())
            except json.JSONDecodeError:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Invalid JSON'}).encode())
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write('Not Found'.encode())
    
    def do_DELETE(self):
        """Handle DELETE requests to remove events"""
        url_parts = urlparse(self.path)
        path = url_parts.path
        query_params = parse_qs(url_parts.query)
        
        if path == '/' or path == '':
            if 'id' not in query_params:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Event ID is required'}).encode())
                return
                
            event_id = query_params['id'][0]
            
            # Find and remove the event
            for i, event in enumerate(events):
                if event.get('id') == event_id:
                    removed_event = events.pop(i)
                    
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        'message': 'Event deleted successfully',
                        'event': removed_event
                    }).encode())
                    return
            
            # If we get here, the event wasn't found
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Event not found'}).encode())
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write('Not Found'.encode()) 