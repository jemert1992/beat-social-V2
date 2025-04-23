from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"status": "online", "message": "Social Media Automation API is running"})

@app.route('/api/status')
def status():
    return jsonify({"status": "online", "message": "API is operational"})

# This is the handler for Vercel serverless functions
def handler(request, response):
    return app(request, response)
