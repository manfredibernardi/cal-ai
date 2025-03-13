from flask import Flask, Response
import sys
import os
from pathlib import Path
import traceback
import json

# Add the parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

# Import the Flask app from the main app.py
from app import app

# This is required for Vercel
def handler(request):
    """Handle incoming requests."""
    try:
        with app.request_context(request):
            return app.handle_request()
    except Exception as e:
        print(f"Handler error: {str(e)}")
        traceback.print_exc()
        return Response(json.dumps({"error": str(e)}), status=500, mimetype='application/json')

# For Vercel Python runtime
from http.server import BaseHTTPRequestHandler

class VercelHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self._handle_request()
    
    def do_POST(self):
        self._handle_request()
    
    def _handle_request(self):
        try:
            # Create a request-like object for handler
            class RequestWrapper:
                def __init__(self, handler):
                    self.method = handler.command
                    self.path = handler.path
                    self.headers = {k: v for k, v in handler.headers.items()}
                
                def get_data(self):
                    content_length = int(self.headers.get('Content-Length', 0))
                    return handler.rfile.read(content_length) if content_length > 0 else b''
            
            # Process request through Flask
            req = RequestWrapper(self)
            response = handler(req)
            
            # Send response back
            self.send_response(response.status_code)
            for header, value in response.headers.items():
                self.send_header(header, value)
            self.end_headers()
            self.wfile.write(response.get_data())
        except Exception as e:
            print(f"Server error: {str(e)}")
            traceback.print_exc()
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8')) 