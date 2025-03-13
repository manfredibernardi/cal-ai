from flask import Flask, Response, request
import sys
import os
from pathlib import Path
import traceback
import json

# Add the parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

try:
    # Import the Flask app from the main app.py
    from app import app
    print("Successfully imported Flask app")
except Exception as e:
    print(f"Error importing app: {str(e)}")
    traceback.print_exc()

# This is the Vercel serverless function entry point
def handler(req):
    """Handle incoming requests from Vercel."""
    try:
        print(f"Request method: {req.method}, path: {req.path}")
        
        if req.method == "GET" and not req.path.startswith('/static/'):
            try:
                return app.send_static_file('index.html')
            except Exception as e:
                print(f"Error serving static file: {str(e)}")
                traceback.print_exc()
                return Response(f"Server error: {str(e)}", status=500)
        
        with app.test_client() as test_client:
            # Create appropriate WSGI environment
            response = test_client.request(
                method=req.method,
                path=req.path,
                headers={key: value for key, value in req.headers.items() if key != 'Host'},
                data=req.get_data(),
                environ_base={'REMOTE_ADDR': req.headers.get('X-Forwarded-For', '127.0.0.1')}
            )
            
            # Return Flask response to Vercel
            return Response(
                response.get_data(),
                status=response.status_code,
                headers=dict(response.headers)
            )
    except Exception as e:
        print(f"Handler error: {str(e)}")
        traceback.print_exc()
        return Response(f"Server error: {str(e)}", status=500)

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