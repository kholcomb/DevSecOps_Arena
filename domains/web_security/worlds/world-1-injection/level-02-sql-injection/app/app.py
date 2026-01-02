#!/usr/bin/env python3
"""
Vulnerable Web Application - SQL Injection Challenge

INTENTIONALLY VULNERABLE FOR EDUCATIONAL PURPOSES
DO NOT USE IN PRODUCTION
"""

from flask import Flask, request, render_template_string
import sqlite3
import os

app = Flask(__name__)

# Get flag from environment
FLAG = os.environ.get('FLAG', 'ARENA{SQL_1nj3ct10n_m4st3r}')

def get_db():
    """Get database connection"""
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    """Login page"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>User Login</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 500px;
                margin: 50px auto;
                padding: 20px;
                background: #f5f5f5;
            }
            .login-box {
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 {
                color: #333;
                text-align: center;
            }
            input[type="text"], input[type="password"] {
                width: 100%;
                padding: 12px;
                margin: 10px 0;
                border: 1px solid #ddd;
                border-radius: 5px;
                box-sizing: border-box;
            }
            button {
                width: 100%;
                padding: 12px;
                background: #007bff;
                color: white;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-size: 16px;
            }
            button:hover {
                background: #0056b3;
            }
            .info {
                background: #e7f3ff;
                padding: 15px;
                margin: 20px 0;
                border-radius: 5px;
                font-size: 14px;
            }
        </style>
    </head>
    <body>
        <div class="login-box">
            <h1>🔐 User Login</h1>
            <div class="info">
                <strong>Demo Credentials:</strong><br>
                Username: john<br>
                Password: password123
            </div>
            <form action="/login" method="POST">
                <input type="text" name="username" placeholder="Username" required>
                <input type="password" name="password" placeholder="Password" required>
                <button type="submit">Login</button>
            </form>
        </div>
    </body>
    </html>
    """
    return html

@app.route('/login', methods=['POST'])
def login():
    """
    VULNERABLE LOGIN ENDPOINT
    Uses string concatenation for SQL query - SQL Injection vulnerability
    """
    username = request.form.get('username', '')
    password = request.form.get('password', '')

    # VULNERABLE: String concatenation in SQL query
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"

    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(query)  # VULNERABLE!
        user = cursor.fetchone()
        conn.close()

        if user:
            # Successful login
            user_dict = dict(user)
            secret = user_dict.get('secret', 'No secret for this user')

            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Login Successful</title>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        max-width: 600px;
                        margin: 50px auto;
                        padding: 20px;
                    }}
                    .success {{
                        background: #d4edda;
                        border: 1px solid #c3e6cb;
                        color: #155724;
                        padding: 20px;
                        border-radius: 5px;
                        margin: 20px 0;
                    }}
                    .user-info {{
                        background: #f8f9fa;
                        padding: 20px;
                        border-radius: 5px;
                        margin: 20px 0;
                    }}
                    a {{
                        color: #007bff;
                        text-decoration: none;
                    }}
                </style>
            </head>
            <body>
                <div class="success">
                    <h1>✅ Login Successful!</h1>
                </div>
                <div class="user-info">
                    <h2>User Information</h2>
                    <p><strong>Username:</strong> {user_dict['username']}</p>
                    <p><strong>Role:</strong> {user_dict['role']}</p>
                    <p><strong>Secret:</strong> {secret}</p>
                </div>
                <p><a href="/">← Back to login</a></p>
            </body>
            </html>
            """
            return html
        else:
            # Failed login
            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Login Failed</title>
                <style>
                    body {
                        font-family: Arial, sans-serif;
                        max-width: 500px;
                        margin: 50px auto;
                        padding: 20px;
                    }
                    .error {
                        background: #f8d7da;
                        border: 1px solid #f5c6cb;
                        color: #721c24;
                        padding: 20px;
                        border-radius: 5px;
                    }
                    a {
                        color: #007bff;
                        text-decoration: none;
                    }
                </style>
            </head>
            <body>
                <div class="error">
                    <h1>❌ Login Failed</h1>
                    <p>Invalid username or password.</p>
                </div>
                <p><a href="/">← Back to login</a></p>
            </body>
            </html>
            """
            return html

    except sqlite3.Error as e:
        # SQL error (useful for exploitation!)
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Database Error</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    max-width: 600px;
                    margin: 50px auto;
                    padding: 20px;
                }}
                .error {{
                    background: #fff3cd;
                    border: 1px solid #ffeaa7;
                    color: #856404;
                    padding: 20px;
                    border-radius: 5px;
                }}
                code {{
                    background: #f4f4f4;
                    padding: 2px 5px;
                    border-radius: 3px;
                }}
            </style>
        </head>
        <body>
            <div class="error">
                <h1>⚠️ Database Error</h1>
                <p>SQL Error: <code>{str(e)}</code></p>
                <p>Query: <code>{query}</code></p>
            </div>
            <p><a href="/">← Back to login</a></p>
        </body>
        </html>
        """
        return html

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
