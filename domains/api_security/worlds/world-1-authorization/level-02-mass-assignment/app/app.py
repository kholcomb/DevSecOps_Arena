#!/usr/bin/env python3
"""
Vulnerable REST API - Mass Assignment Challenge

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
    "user123": {
        "user_id": "user123",
        "username": "alice",
        "email": "alice@example.com",
        "role": "user",  # Sensitive field - should not be modifiable
        "is_premium": False,  # Sensitive field
        "account_balance": 100.0,  # Sensitive field
        "bio": "I love security challenges!",
        "api_key": "alice_api_key_12345"
    }
}

@app.route('/')
def index():
    """API documentation"""
    return jsonify({
        "name": "User Profile API",
        "version": "1.0",
        "endpoints": {
            "/api/profile": {
                "method": "GET",
                "description": "Get your profile",
                "authentication": "API-Key header required"
            },
            "/api/profile": {
                "method": "PUT",
                "description": "Update your profile",
                "authentication": "API-Key header required",
                "allowed_fields": ["username", "email", "bio"],
                "example": "curl -X PUT http://localhost:4002/api/profile -H 'API-Key: alice_api_key_12345' -H 'Content-Type: application/json' -d '{\"bio\":\"New bio\"}'",
                "warning": "Only update allowed fields!"
            },
            "/api/admin/flag": {
                "method": "GET",
                "description": "Get the secret flag (admin only)",
                "authentication": "API-Key header + admin role required"
            }
        },
        "hint": "Can you modify fields that shouldn't be modifiable?"
    })

def get_user_from_api_key(api_key):
    """Find user by API key"""
    for user_id, user in USERS.items():
        if user.get('api_key') == api_key:
            return user_id, user
    return None, None

@app.route('/api/profile', methods=['GET'])
def get_profile():
    """Get current user's profile"""
    api_key = request.headers.get('API-Key')

    if not api_key:
        return jsonify({"error": "Missing API-Key header"}), 401

    user_id, user = get_user_from_api_key(api_key)
    if not user:
        return jsonify({"error": "Invalid API key"}), 401

    # Return user profile (excluding sensitive api_key)
    profile = {k: v for k, v in user.items() if k != 'api_key'}
    return jsonify(profile)

@app.route('/api/profile', methods=['PUT'])
def update_profile():
    """
    VULNERABLE ENDPOINT - Mass Assignment vulnerability

    This endpoint allows users to update their profile, but it doesn't
    validate WHICH fields are being updated. Users should only be able
    to update 'username', 'email', and 'bio', but the API blindly
    accepts all fields from the request.
    """
    api_key = request.headers.get('API-Key')

    if not api_key:
        return jsonify({"error": "Missing API-Key header"}), 401

    user_id, user = get_user_from_api_key(api_key)
    if not user:
        return jsonify({"error": "Invalid API key"}), 401

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    # VULNERABLE: Blindly updates all fields from request
    # No validation of which fields are allowed to be modified
    for key, value in data.items():
        if key != 'api_key':  # At least protect the api_key
            USERS[user_id][key] = value

    return jsonify({
        "success": True,
        "message": "Profile updated successfully",
        "updated_fields": list(data.keys()),
        "_hint": "Did you update more than you were supposed to? Check your profile!"
    })

@app.route('/api/admin/flag', methods=['GET'])
def admin_flag():
    """Admin-only endpoint that returns the flag"""
    api_key = request.headers.get('API-Key')

    if not api_key:
        return jsonify({"error": "Missing API-Key header"}), 401

    user_id, user = get_user_from_api_key(api_key)
    if not user:
        return jsonify({"error": "Invalid API key"}), 401

    # Check if user has admin role
    if user.get('role') != 'admin':
        return jsonify({
            "error": "Forbidden: Admin access required",
            "your_role": user.get('role'),
            "hint": "You need to be an admin to access this endpoint"
        }), 403

    # Return the flag for admin users
    return jsonify({
        "success": True,
        "message": "Welcome, admin!",
        "flag": FLAG,
        "admin_privileges": [
            "View all users",
            "Delete accounts",
            "Access sensitive data",
            "Modify system settings"
        ]
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
