#!/usr/bin/env python3
"""
Vulnerable REST API - JWT None Algorithm Challenge

INTENTIONALLY VULNERABLE FOR EDUCATIONAL PURPOSES
DO NOT USE IN PRODUCTION
"""

from flask import Flask, jsonify, request
import jwt
import os
import base64
import json

app = Flask(__name__)

# Get flag from environment variable
FLAG = os.environ.get('FLAG', 'ARENA{test_flag}')
SECRET_KEY = "super_secret_key_12345"  # In real apps, this would be secret

@app.route('/')
def index():
    """API documentation"""
    return jsonify({
        "name": "JWT Authentication API",
        "version": "1.0",
        "endpoints": {
            "/api/login": {
                "method": "POST",
                "description": "Login to get JWT token",
                "body": {"username": "alice or bob"},
                "example": "curl -X POST http://localhost:4004/api/login -H 'Content-Type: application/json' -d '{\"username\":\"alice\"}'"
            },
            "/api/profile": {
                "method": "GET",
                "description": "Get your profile (requires JWT)",
                "authentication": "Authorization: Bearer <token>",
                "example": "curl -H 'Authorization: Bearer <your_jwt>' http://localhost:4004/api/profile"
            },
            "/api/admin/flag": {
                "method": "GET",
                "description": "Get the flag (admin only)",
                "authentication": "Admin JWT required"
            }
        },
        "hint": "JWTs can be decoded to see their contents. What if you could modify them?"
    })

@app.route('/api/login', methods=['POST'])
def login():
    """Login endpoint - returns a JWT token"""
    data = request.get_json()
    username = data.get('username', '').lower()

    if username not in ['alice', 'bob']:
        return jsonify({"error": "Invalid username. Try 'alice' or 'bob'"}), 400

    # Create JWT for regular user
    token_payload = {
        "username": username,
        "role": "user",  # Regular users get 'user' role
        "user_id": username
    }

    # Sign token with SECRET_KEY using HS256
    token = jwt.encode(token_payload, SECRET_KEY, algorithm='HS256')

    return jsonify({
        "success": True,
        "message": f"Logged in as {username}",
        "token": token,
        "role": "user",
        "hint": "Decode this JWT to see its structure. Can you create an admin token?"
    })

@app.route('/api/profile', methods=['GET'])
def profile():
    """Get current user's profile"""
    auth_header = request.headers.get('Authorization')

    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Missing or invalid Authorization header"}), 401

    token = auth_header.replace('Bearer ', '')

    try:
        # VULNERABLE: Verify with options that allow 'none' algorithm
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=['HS256', 'none'],  # VULNERABLE: Accepts 'none' algorithm!
            options={"verify_signature": True}
        )

        return jsonify({
            "username": payload.get('username'),
            "role": payload.get('role'),
            "user_id": payload.get('user_id')
        })

    except jwt.InvalidTokenError as e:
        return jsonify({"error": f"Invalid token: {str(e)}"}), 401

@app.route('/api/admin/flag', methods=['GET'])
def admin_flag():
    """Admin-only endpoint"""
    auth_header = request.headers.get('Authorization')

    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Missing or invalid Authorization header"}), 401

    token = auth_header.replace('Bearer ', '')

    try:
        # VULNERABLE: Accepts 'none' algorithm
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=['HS256', 'none'],  # VULNERABLE!
            options={"verify_signature": True}
        )

        # Check if user is admin
        if payload.get('role') != 'admin':
            return jsonify({
                "error": "Forbidden: Admin access required",
                "your_role": payload.get('role'),
                "hint": "You need a JWT with role='admin'. Can you create one?"
            }), 403

        return jsonify({
            "success": True,
            "message": "Welcome, admin!",
            "flag": FLAG,
            "username": payload.get('username'),
            "_vulnerability": "You exploited the JWT 'none' algorithm vulnerability!"
        })

    except jwt.InvalidTokenError as e:
        return jsonify({"error": f"Invalid token: {str(e)}"}), 401

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
