#!/usr/bin/env python3
"""
Vulnerable Web Application - Reflected XSS Challenge

INTENTIONALLY VULNERABLE FOR EDUCATIONAL PURPOSES
DO NOT USE IN PRODUCTION
"""

from flask import Flask, request, make_response
import os

app = Flask(__name__)

# Get flag from environment variable
FLAG = os.environ.get('FLAG', 'ARENA{test_flag}')

@app.route('/')
def index():
    """Home page with search form"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Product Search</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
            }
            h1 { color: #333; }
            .search-box {
                margin: 20px 0;
            }
            input[type="text"] {
                padding: 10px;
                width: 300px;
                border: 1px solid #ddd;
            }
            button {
                padding: 10px 20px;
                background: #007bff;
                color: white;
                border: none;
                cursor: pointer;
            }
            button:hover {
                background: #0056b3;
            }
            .info {
                background: #f0f0f0;
                padding: 15px;
                margin: 20px 0;
                border-radius: 5px;
            }
        </style>
    </head>
    <body>
        <h1>Product Search</h1>
        <div class="info">
            <p>Welcome to our product search! Try searching for:</p>
            <ul>
                <li>laptop</li>
                <li>phone</li>
                <li>tablet</li>
            </ul>
        </div>
        <div class="search-box">
            <form action="/search" method="GET">
                <input type="text" name="q" placeholder="Search for products...">
                <button type="submit">Search</button>
            </form>
        </div>
    </body>
    </html>
    """

    # Set flag in cookie (intentionally visible for exploitation)
    response = make_response(html)
    response.set_cookie('flag', FLAG, httponly=False)  # VULNERABLE: httponly=False
    return response

@app.route('/search')
def search():
    """
    VULNERABLE SEARCH ENDPOINT
    Reflects user input without sanitization - XSS vulnerability
    """
    query = request.args.get('q', '')

    # VULNERABLE: Directly embedding user input in HTML
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Search Results</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
            }}
            h1 {{ color: #333; }}
            .results {{
                margin: 20px 0;
            }}
            .no-results {{
                color: #666;
                padding: 20px;
                background: #f9f9f9;
            }}
            a {{
                color: #007bff;
                text-decoration: none;
            }}
        </style>
    </head>
    <body>
        <h1>Search Results</h1>
        <div class="results">
            <p>You searched for: <strong>{query}</strong></p>
            <div class="no-results">
                <p>No products found matching your search.</p>
                <p><a href="/">← Back to search</a></p>
            </div>
        </div>
    </body>
    </html>
    """

    # Set flag in cookie again
    response = make_response(html)
    response.set_cookie('flag', FLAG, httponly=False)
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
