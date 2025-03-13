from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return jsonify({'hello': 'world'})

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})
    
def handler(request, context):
    """
    This function is called by Vercel on each request.
    """
    # Create request context from Vercel's input
    path = request.get('path', '/')
    method = request.get('method', 'GET')
    headers = request.get('headers', {})
    body = request.get('body', b'')
    
    # Create request context
    with app.test_request_context(
        path=path,
        method=method,
        headers=headers,
        data=body
    ):
        # Full dispatch request
        return app.full_dispatch_request() 