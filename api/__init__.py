# This file is intentionally empty to make the directory a Python package 

# This file ensures that the api directory is treated as a Python package
# It helps with imports in the Vercel serverless environment

import os
import sys
from pathlib import Path

# Add parent directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

# Print environment information for debugging
print(f"Python version: {sys.version}")
print(f"Python path: {sys.path}")
print(f"Working directory: {os.getcwd()}")
print(f"Environment variables: {', '.join(f'{k}={v}' for k, v in os.environ.items() if k.startswith(('PYTHON', 'VERCEL', 'FLASK')))}") 