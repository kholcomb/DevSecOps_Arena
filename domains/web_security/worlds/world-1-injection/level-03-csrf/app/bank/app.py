#!/usr/bin/env python3
"""
Vulnerable Banking Application - CSRF Challenge

INTENTIONALLY VULNERABLE FOR EDUCATIONAL PURPOSES
DO NOT USE IN PRODUCTION
"""

from flask import Flask, request, make_response, redirect
import os

app = Flask(__name__)
app.secret_key = 'insecure_secret_key_123'

# Get flag from environment
FLAG = os.environ.get('FLAG', 'ARENA{CSRF_f0rc3d_tr4nsf3r}')

# Simple in-memory user database
users = {
    'alice': {'balance': 1000, 'password': 'password123'},
    'attacker': {'balance': 0, 'password': 'evil'}
}

# Track transfers
transfers = []

@app.route('/')
def index():
    """Home page with login"""
    session_user = request.cookies.get('session_user')

    if session_user and session_user in users:
        # User is logged in
        user_data = users[session_user]
        balance = user_data['balance']

        # Show flag if money was transferred to attacker
        flag_message = ""
        if any(t['to'] == 'attacker' and t['amount'] > 0 for t in transfers):
            flag_message = f'<div class="flag">🚩 Flag: {FLAG}</div>'

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>SecureBank</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    max-width: 700px;
                    margin: 50px auto;
                    padding: 20px;
                }}
                .header {{
                    background: #007bff;
                    color: white;
                    padding: 20px;
                    border-radius: 5px;
                    margin-bottom: 20px;
                }}
                .balance {{
                    background: #f0f0f0;
                    padding: 20px;
                    border-radius: 5px;
                    margin: 20px 0;
                }}
                .transfer-form {{
                    background: white;
                    padding: 20px;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                }}
                input[type="text"], input[type="number"] {{
                    width: 100%;
                    padding: 10px;
                    margin: 10px 0;
                    border: 1px solid #ddd;
                    border-radius: 3px;
                    box-sizing: border-box;
                }}
                button {{
                    padding: 10px 20px;
                    background: #007bff;
                    color: white;
                    border: none;
                    border-radius: 3px;
                    cursor: pointer;
                }}
                button:hover {{
                    background: #0056b3;
                }}
                .flag {{
                    background: #d4edda;
                    border: 1px solid #c3e6cb;
                    color: #155724;
                    padding: 15px;
                    border-radius: 5px;
                    margin: 20px 0;
                    font-weight: bold;
                }}
                .history {{
                    margin-top: 30px;
                }}
                .transfer-item {{
                    background: #f9f9f9;
                    padding: 10px;
                    margin: 5px 0;
                    border-radius: 3px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🏦 SecureBank</h1>
                <p>Welcome, {session_user}! | <a href="/logout" style="color: white;">Logout</a></p>
            </div>

            {flag_message}

            <div class="balance">
                <h2>Current Balance: ${balance}</h2>
            </div>

            <div class="transfer-form">
                <h2>Transfer Funds</h2>
                <form action="/transfer" method="POST">
                    <input type="text" name="to" placeholder="Recipient username" required>
                    <input type="number" name="amount" placeholder="Amount" min="1" required>
                    <button type="submit">Transfer Money</button>
                </form>
            </div>

            <div class="history">
                <h2>Transfer History</h2>
                {"".join(f'<div class="transfer-item">Transferred ${t["amount"]} to {t["to"]}</div>' for t in transfers if t["from"] == session_user)}
            </div>
        </body>
        </html>
        """
        return html
    else:
        # Show login form
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>SecureBank - Login</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    max-width: 400px;
                    margin: 100px auto;
                    padding: 20px;
                }
                .login-box {
                    background: white;
                    padding: 30px;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }
                h1 {
                    text-align: center;
                    color: #007bff;
                }
                input {
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
                <h1>🏦 SecureBank</h1>
                <div class="info">
                    <strong>Demo Account:</strong><br>
                    Username: alice<br>
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
    """Login endpoint"""
    username = request.form.get('username', '')
    password = request.form.get('password', '')

    if username in users and users[username]['password'] == password:
        response = make_response(redirect('/'))
        response.set_cookie('session_user', username)
        return response
    else:
        return "Invalid credentials. <a href='/'>Try again</a>"

@app.route('/logout')
def logout():
    """Logout endpoint"""
    response = make_response(redirect('/'))
    response.set_cookie('session_user', '', expires=0)
    return response

@app.route('/transfer', methods=['POST'])
def transfer():
    """
    VULNERABLE TRANSFER ENDPOINT
    No CSRF token validation - accepts any POST request
    """
    session_user = request.cookies.get('session_user')

    if not session_user or session_user not in users:
        return "Not logged in. <a href='/'>Login</a>"

    to_user = request.form.get('to', '')
    amount = int(request.form.get('amount', 0))

    if to_user not in users:
        return f"User '{to_user}' not found. <a href='/'>Go back</a>"

    if amount <= 0:
        return "Invalid amount. <a href='/'>Go back</a>"

    if users[session_user]['balance'] < amount:
        return "Insufficient funds. <a href='/'>Go back</a>"

    # Perform transfer (VULNERABLE: No CSRF token check!)
    users[session_user]['balance'] -= amount
    users[to_user]['balance'] += amount

    # Record transfer
    transfers.append({
        'from': session_user,
        'to': to_user,
        'amount': amount
    })

    return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
