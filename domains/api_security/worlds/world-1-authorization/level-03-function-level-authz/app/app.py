#!/usr/bin/env python3
"""
Vulnerable REST API - Broken Function Level Authorization Challenge

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
    "user1": {
        "user_id": "user1",
        "username": "alice",
        "email": "alice@example.com",
        "role": "user",
        "api_key": "user_key_12345"
    },
    "user2": {
        "user_id": "user2",
        "username": "bob",
        "email": "bob@example.com",
        "role": "user",
        "api_key": "user_key_67890"
    },
    "target": {
        "user_id": "target",
        "username": "testuser",
        "email": "test@example.com",
        "role": "user",
        "api_key": "test_key_99999"
    }
}

def get_user_from_api_key(api_key):
    """Find user by API key"""
    for user_id, user in USERS.items():
        if user.get('api_key') == api_key:
            return user_id, user
    return None, None

@app.route('/')
def index():
    """API documentation - only shows 'safe' endpoints"""
    return jsonify({
        "name": "User Management API",
        "version": "2.0",
        "endpoints": {
            "/api/users": {
                "method": "GET",
                "description": "List all users",
                "authentication": "API-Key header required"
            },
            "/api/users/<user_id>": {
                "method": "GET",
                "description": "Get user details",
                "authentication": "API-Key header required"
            }
        },
        "hint": "Are there other HTTP methods or hidden endpoints? Admin functions must exist somewhere..."
    })

@app.route('/api/users', methods=['GET'])
def list_users():
    """List all users (public endpoint)"""
    api_key = request.headers.get('API-Key')
    if not api_key:
        return jsonify({"error": "Missing API-Key header"}), 401

    user_id, user = get_user_from_api_key(api_key)
    if not user:
        return jsonify({"error": "Invalid API key"}), 401

    # Return list of users
    users_list = []
    for uid, udata in USERS.items():
        users_list.append({
            "user_id": uid,
            "username": udata["username"],
            "email": udata["email"]
        })

    return jsonify({
        "users": users_list,
        "hint": "You can view users, but can you manage them? Try other HTTP methods..."
    })

@app.route('/api/users/<user_id>', methods=['GET'])
def get_user(user_id):
    """Get user details (public endpoint)"""
    api_key = request.headers.get('API-Key')
    if not api_key:
        return jsonify({"error": "Missing API-Key header"}), 401

    user_id_auth, user_auth = get_user_from_api_key(api_key)
    if not user_auth:
        return jsonify({"error": "Invalid API key"}), 401

    if user_id not in USERS:
        return jsonify({"error": "User not found"}), 404

    target_user = USERS[user_id]
    return jsonify({
        "user_id": target_user["user_id"],
        "username": target_user["username"],
        "email": target_user["email"]
    })

@app.route('/api/users/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    """
    VULNERABLE ENDPOINT - Broken Function Level Authorization

    This DELETE endpoint should only be accessible to admin users,
    but it only checks if the user is authenticated, not if they
    have admin privileges.

    The endpoint is 'hidden' (not in documentation) but still accessible.
    """
    api_key = request.headers.get('API-Key')
    if not api_key:
        return jsonify({"error": "Missing API-Key header"}), 401

    user_id_auth, user_auth = get_user_from_api_key(api_key)
    if not user_auth:
        return jsonify({"error": "Invalid API key"}), 401

    # VULNERABLE: No check for admin role!
    # Should verify: if user_auth['role'] != 'admin': return 403

    if user_id not in USERS:
        return jsonify({"error": "User not found"}), 404

    # Delete the user
    deleted_user = USERS.pop(user_id)

    return jsonify({
        "success": True,
        "message": f"User {user_id} deleted successfully",
        "deleted_user": deleted_user["username"],
        "flag": FLAG,
        "_vulnerability": "You exploited broken function-level authorization!",
        "_explanation": "This DELETE endpoint should only be accessible to admins, but it didn't check your role."
    })

@app.route('/api/admin/dashboard', methods=['GET'])
def admin_dashboard():
    """
    Another admin endpoint (decoy) - this one IS properly protected
    to show the difference
    """
    api_key = request.headers.get('API-Key')
    if not api_key:
        return jsonify({"error": "Missing API-Key header"}), 401

    user_id, user = get_user_from_api_key(api_key)
    if not user:
        return jsonify({"error": "Invalid API key"}), 401

    # This endpoint DOES check for admin role (proper implementation)
    if user.get('role') != 'admin':
        return jsonify({
            "error": "Forbidden: Admin access required",
            "hint": "This endpoint is properly protected. Try looking for other admin functions..."
        }), 403

    return jsonify({
        "message": "Admin dashboard",
        "stats": {"total_users": len(USERS)}
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
