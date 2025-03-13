from flask import Flask, redirect, jsonify
import sys
import os
import traceback
from pathlib import Path

# Add the parent directory to Python path
parent_dir = str(Path(__file__).parent.parent)
sys.path.append(parent_dir)
print(f"Added parent directory to path: {parent_dir}")
print(f"Python path: {sys.path}")

# Configure logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info(f"Starting serverless function. Working directory: {os.getcwd()}")

try:
    # Import the Flask app from app.py
    from app import app
    logger.info("Successfully imported app")
    
    # Set up WSGI app with correct paths for Vercel
    app.static_folder = Path(__file__).parent.parent / 'static'
    app.template_folder = Path(__file__).parent.parent / 'templates'
    logger.info(f"Set static folder to {app.static_folder}")
    logger.info(f"Set template folder to {app.template_folder}")
except Exception as e:
    logger.error(f"Error importing app: {str(e)}")
    logger.error(traceback.format_exc())
    # Create a minimal app for error reporting
    app = Flask(__name__)
    
    @app.route('/')
    def error_index():
        return jsonify({
            "error": f"Failed to initialize app: {str(e)}",
            "traceback": traceback.format_exc()
        }), 500

# Handler for Vercel - this is what Vercel calls
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

# For Vercel platform
def render_page(path):
    """
    This is called by Vercel platform to render a page.
    """
    logger.info(f"Render page called for path: {path}")
    return app

# Default route - this will be used if request is directly to index.py
@app.route('/api/health')
def health_check():
    """
    Simple health check endpoint to verify the function is working.
    """
    logger.info("Health check endpoint called")
    return jsonify({
        "status": "ok",
        "environment": {
            "PYTHONPATH": os.environ.get('PYTHONPATH'),
            "FLASK_ENV": os.environ.get('FLASK_ENV'),
            "VERCEL_ENV": os.environ.get('VERCEL_ENV')
        }
    })

# Handle invalid paths
@app.route('/api/<path:invalid_path>')
def handle_invalid_api_route(invalid_path):
    """
    Redirect API routes to the main app.
    """
    logger.info(f"Invalid API path: {invalid_path}")
    return redirect('/') 