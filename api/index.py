from flask import Flask, request, jsonify, render_template
import sys
import os
from pathlib import Path

# Add the parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

# Import the Flask app from the main app.py
from app import app

# This is the handler that Vercel will call
def handler(request):
    with app.request_context(request):
        return app.full_dispatch_request() 