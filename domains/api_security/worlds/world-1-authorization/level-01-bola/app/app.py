#!/usr/bin/env python3
"""
Vulnerable REST API - BOLA (Broken Object Level Authorization) Challenge

INTENTIONALLY VULNERABLE FOR EDUCATIONAL PURPOSES
DO NOT USE IN PRODUCTION
"""

from flask import Flask, jsonify, request
import os

app = Flask(__name__)

# Get flag from environment variable
FLAG = os.environ.get('FLAG', 'ARENA{test_flag}')

# Simulated user database
USERS = {
    1: {
        "id": 1,
        "username": "alice",
        "email": "alice@example.com",
        "role": "user",
        "api_key": "alice_key_12345"
    },
    2: {
        "id": 2,
        "username": "admin",
        "email": "admin@example.com",
        "role": "admin",
        "api_key": "admin_key_secret",
        "secret_flag": FLAG  # Target data
    },
    3: {
        "id": 3,
        "username": "bob",
        "email": "bob@example.com",
        "role": "user",
        "api_key": "bob_key_67890"
    }
}

@app.route('/')
def index():
    """API documentation"""
    return jsonify({
        "name": "User Management API",
        "version": "1.0",
        "endpoints": {
            "/api/users/<user_id>": {
                "method": "GET",
                "description": "Get user profile by ID",
                "authentication": "API-Key header required",
                "example": "curl -H 'API-Key: alice_key_12345' http://localhost:4001/api/users/1"
            },
            "/api/login": {
                "method": "POST",
                "description": "Get your API key (for demo purposes)",
                "body": {"username": "alice or bob"},
                "example": "curl -X POST http://localhost:4001/api/login -H 'Content-Type: application/json' -d '{\"username\":\"alice\"}'"
            }
        },
        "hint": "You are logged in as a regular user. Can you access the admin's profile?"
    })

@app.route('/api/login', methods=['POST'])
def login():
    """
    Demo login endpoint - returns API key for a user
    (In a real app, this would validate credentials)
    """
    data = request.get_json()
    username = data.get('username', '').lower()

    # Find user by username
    for user_id, user in USERS.items():
        if user['username'] == username:
            return jsonify({
                "success": True,
                "message": f"Welcome {username}!",
                "api_key": user['api_key'],
                "user_id": user_id
            })

    return jsonify({
        "success": False,
        "message": "User not found. Try 'alice' or 'bob'"
    }), 404

@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """
    VULNERABLE ENDPOINT - BOLA/IDOR vulnerability

    This endpoint only checks if the user is authenticated (has valid API key)
    but does NOT check if the authenticated user has permission to access
    the requested user_id's data.
    """

    # Check if API-Key header is present
    api_key = request.headers.get('API-Key')

    if not api_key:
        return jsonify({
            "error": "Missing API-Key header",
            "hint": "Use the /api/login endpoint to get your API key"
        }), 401

    # VULNERABLE: Only checks if API key exists, not if it belongs to the right user
    valid_key = False
    authenticated_user = None
    for uid, user in USERS.items():
        if user['api_key'] == api_key:
            valid_key = True
            authenticated_user = user
            break

    if not valid_key:
        return jsonify({
            "error": "Invalid API key"
        }), 401

    # VULNERABLE: No authorization check!
    # The code checks authentication (is the user logged in?)
    # but NOT authorization (is the user allowed to access THIS resource?)

    # Return the requested user's data (even if it's not the authenticated user)
    if user_id in USERS:
        user_data = USERS[user_id].copy()

        # Show a hint to the attacker
        if authenticated_user and authenticated_user['id'] != user_id:
            user_data['_hint'] = f"You (user {authenticated_user['id']}) successfully accessed user {user_id}'s data!"

        return jsonify(user_data)
    else:
        return jsonify({
            "error": "User not found"
        }), 404

@app.route('/api/users', methods=['GET'])
def list_users():
    """List all users (IDs only) - helps with enumeration"""
    return jsonify({
        "users": [
            {"id": 1, "username": "alice"},
            {"id": 2, "username": "admin"},
            {"id": 3, "username": "bob"}
        ],
        "hint": "Try accessing /api/users/<id> for each user"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
