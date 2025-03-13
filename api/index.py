from flask import Flask, redirect
import sys
import os
from pathlib import Path

# Add the parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

# Import the Flask app from app.py
from app import app

# Set up WSGI app with correct paths for Vercel
app.static_folder = Path(__file__).parent.parent / 'static'
app.template_folder = Path(__file__).parent.parent / 'templates'

# Handler for Vercel - this is what Vercel calls
def handler(request, context):
    """
    This is the handler that Vercel calls when your serverless function is triggered.
    """
    with app.test_request_context(
        path=request.get('path', '/'),
        method=request.get('method', 'GET'),
        headers=request.get('headers', {}),
        data=request.get('body', b'')
    ):
        try:
            # Process the request through the Flask app
            return app.full_dispatch_request()
        except Exception as e:
            app.logger.error(f"Error handling request: {str(e)}")
            response = app.make_response(f"Server error: {str(e)}")
            response.status_code = 500
            return response

# For Vercel platform
def render_page(path):
    """
    This is called by Vercel platform to render a page.
    """
    return app

# Default route - this will be used if request is directly to index.py
@app.route('/api/health')
def health_check():
    """
    Simple health check endpoint to verify the function is working.
    """
    return {"status": "ok"}

# Handle invalid paths
@app.route('/api/<path:invalid_path>')
def handle_invalid_api_route(invalid_path):
    """
    Redirect API routes to the main app.
    """
    return redirect('/') 