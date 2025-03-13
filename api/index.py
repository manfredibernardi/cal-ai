from flask import Flask, Response
import sys
import os
from pathlib import Path

# Add the parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

# Import the Flask app from the main app.py
from app import app

def handler(request):
    """Handle incoming requests."""
    if request.method == "GET":
        return app.send_static_file('index.html')
    
    with app.test_client() as test_client:
        response = test_client.request(
            method=request.method,
            path=request.url.split(request.host_url)[1],
            headers={key: value for key, value in request.headers if key != 'Host'},
            data=request.get_data(),
            environ_base={'REMOTE_ADDR': request.access_route[0]}
        )
        
        return Response(
            response.get_data(),
            status=response.status_code,
            headers=dict(response.headers)
        ) 