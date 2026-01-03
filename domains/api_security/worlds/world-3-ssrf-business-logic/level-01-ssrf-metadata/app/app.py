#!/usr/bin/env python3
"""
Vulnerable REST API - SSRF Challenge
INTENTIONALLY VULNERABLE FOR EDUCATIONAL PURPOSES
"""
from flask import Flask, jsonify, request
import requests
import os

app = Flask(__name__)
FLAG = os.environ.get('FLAG', 'ARENA{test_flag}')

@app.route('/')
def index():
    return jsonify({
        "name": "Webhook API",
        "endpoints": {
            "/api/fetch": {
                "method": "POST",
                "body": {"url": "https://example.com"},
                "description": "Fetch content from URL"
            }
        }
    })

@app.route('/api/fetch', methods=['POST'])
def fetch_url():
    """VULNERABLE: No URL validation - SSRF vulnerability"""
    data = request.get_json()
    url = data.get('url')

    if not url:
        return jsonify({"error": "URL required"}), 400

    try:
        # VULNERABLE: Fetches ANY URL without validation
        response = requests.get(url, timeout=5)
        return jsonify({
            "success": True,
            "url": url,
            "content": response.text,
            "status_code": response.status_code
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
