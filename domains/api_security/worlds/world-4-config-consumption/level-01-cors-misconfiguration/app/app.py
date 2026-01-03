#!/usr/bin/env python3
"""Vulnerable API - CORS Misconfiguration"""
from flask import Flask, jsonify, request, make_response
import os

app = Flask(__name__)
FLAG = os.environ.get('FLAG', 'ARENA{test_flag}')

@app.after_request
def add_cors_headers(response):
    """VULNERABLE: Allows ANY origin with credentials"""
    origin = request.headers.get('Origin')
    if origin:
        response.headers['Access-Control-Allow-Origin'] = origin  # VULNERABLE!
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response

@app.route('/')
def index():
    return jsonify({"name": "API with CORS", "hint": "Check CORS headers"})

@app.route('/api/user/profile', methods=['GET'])
def get_profile():
    """Returns sensitive data - should be protected"""
    api_key = request.headers.get('Authorization')
    if not api_key:
        return jsonify({"error": "Unauthorized"}), 401

    return jsonify({
        "username": "admin",
        "email": "admin@company.com",
        "role": "admin",
        "secret_flag": FLAG,
        "_vulnerability": "CORS allows any origin to read this!"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
