from flask import Flask, jsonify
import os
import sys
import traceback
from pathlib import Path
import json
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

# Configure logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info(f"Starting serverless function. Working directory: {os.getcwd()}")

# Create a new Flask app just for the API
app = Flask(__name__)
app.static_folder = Path(__file__).parent.parent / 'static'
app.template_folder = Path(__file__).parent.parent / 'templates'

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

@app.route('/')
def index():
    """Return a simple welcome message."""
    logger.info("Index route called")
    return jsonify({
        "message": "Welcome to Cal AI!",
        "status": "API is running",
        "environment": os.environ.get('VERCEL_ENV', 'local')
    })

@app.route('/api/health')
def health_check():
    """Health check endpoint."""
    logger.info("Health check endpoint called")
    return jsonify({
        "status": "ok",
        "environment": {
            "PYTHONPATH": os.environ.get('PYTHONPATH'),
            "FLASK_ENV": os.environ.get('FLASK_ENV'),
            "VERCEL_ENV": os.environ.get('VERCEL_ENV')
        },
        "directories": {
            "current": os.getcwd(),
            "static_folder": str(app.static_folder),
            "template_folder": str(app.template_folder),
            "static_exists": os.path.exists(app.static_folder) if app.static_folder else False,
            "templates_exist": os.path.exists(app.template_folder) if app.template_folder else False,
        }
    })

@app.errorhandler(500)
def server_error(e):
    """Handle server errors."""
    error_msg = str(e)
    logger.error(f"Server error: {error_msg}")
    logger.error(traceback.format_exc())
    return jsonify(error=error_msg, traceback=traceback.format_exc()), 500

# Handler for Vercel
def handler(request, context):
    """
    This is the handler that Vercel calls when your serverless function is triggered.
    """
    logger.info(f"Received request: {request.get('path', '/')} [{request.get('method', 'GET')}]")
    
    try:
        # Create a test request context
        with app.test_request_context(
            path=request.get('path', '/'),
            method=request.get('method', 'GET'),
            headers=request.get('headers', {}),
            data=request.get('body', b'')
        ):
            try:
                # Process the request through the Flask app
                logger.info("Dispatching request")
                return app.full_dispatch_request()
            except Exception as e:
                logger.error(f"Error handling request: {str(e)}")
                logger.error(traceback.format_exc())
                response = app.make_response(jsonify({
                    "error": f"Server error: {str(e)}",
                    "traceback": traceback.format_exc()
                }))
                response.status_code = 500
                return response
    except Exception as e:
        logger.error(f"Error setting up request context: {str(e)}")
        logger.error(traceback.format_exc())
        return {
            "statusCode": 500,
            "body": f"Failed to process request: {str(e)}"
        } 