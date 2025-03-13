from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return {'message': 'Hello World'}

def handler(request, context):
    return {'statusCode': 200, 'body': 'Hello from Vercel!'} 