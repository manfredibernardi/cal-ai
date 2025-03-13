from flask import Flask, jsonify
import os
import sys
import traceback
from pathlib import Path

# Configure logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info(f"Starting serverless function. Working directory: {os.getcwd()}")

# Create a new Flask app just for the API
app = Flask(__name__)
app.static_folder = Path(__file__).parent.parent / 'static'
app.template_folder = Path(__file__).parent.parent / 'templates'

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