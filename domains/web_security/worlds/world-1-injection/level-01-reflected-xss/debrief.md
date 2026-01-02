# Reflected XSS Challenge - Debrief

## Vulnerability Explained

**Cross-Site Scripting (XSS)** is a security vulnerability that allows attackers to inject malicious scripts into web pages viewed by other users. In this challenge, you exploited a **reflected XSS** vulnerability.

### What Happened

The vulnerable application took user input from the search parameter and directly embedded it into the HTML response without any sanitization or encoding:

```python
# VULNERABLE CODE
query = request.args.get('q', '')
html = f"""
    <p>You searched for: <strong>{query}</strong></p>
"""
```

When you injected `<script>alert(document.cookie)</script>` as the search query, the browser executed it as JavaScript code instead of displaying it as text.

### Attack Flow

1. **Payload crafted**: `http://localhost:3001/search?q=<script>alert(document.cookie)</script>`
2. **Server reflects**: The malicious script is embedded directly in the HTML
3. **Browser executes**: The JavaScript runs in the victim's browser context
4. **Cookie stolen**: `document.cookie` reveals the flag

### Why This Worked

Two critical mistakes made this attack possible:

1. **No Input Sanitization**: The server didn't encode HTML special characters
2. **Cookie Not Protected**: The `httponly` flag was set to `False`, allowing JavaScript access

## Real-World Impact

XSS is consistently in the OWASP Top 10 and can lead to:

- **Session Hijacking**: Stealing authentication cookies
- **Credential Theft**: Capturing login credentials via fake forms
- **Malware Distribution**: Redirecting users to malicious sites
- **Defacement**: Modifying page content
- **Keylogging**: Recording user keystrokes

## Mitigation Strategies

### 1. Output Encoding

Always encode user input before displaying it in HTML:

```python
from markupsafe import escape

# SECURE CODE
query = escape(request.args.get('q', ''))
html = f"""
    <p>You searched for: <strong>{query}</strong></p>
"""
```

### 2. Content Security Policy (CSP)

Add HTTP headers to restrict script execution:

```python
response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self'"
```

### 3. HttpOnly Cookies

Prevent JavaScript access to sensitive cookies:

```python
response.set_cookie('flag', FLAG, httponly=True, secure=True, samesite='Strict')
```

### 4. Input Validation

Validate and sanitize all user inputs:

```python
import re

def sanitize_search(query):
    # Only allow alphanumeric characters and spaces
    return re.sub(r'[^a-zA-Z0-9 ]', '', query)
```

### 5. Use Templates with Auto-Escaping

Modern frameworks provide automatic escaping:

```python
from flask import render_template_string

# Jinja2 auto-escapes by default
return render_template_string('<p>You searched for: <strong>{{ query }}</strong></p>', query=query)
```

## Testing for XSS

### Common Payloads

```javascript
<script>alert('XSS')</script>
<img src=x onerror=alert('XSS')>
<svg onload=alert('XSS')>
'"><script>alert('XSS')</script>
```

### Tools

- **Burp Suite**: Intercepting proxy with XSS scanner
- **OWASP ZAP**: Free security scanner
- **XSStrike**: Advanced XSS detection tool

## References

- [OWASP XSS Guide](https://owasp.org/www-community/attacks/xss/)
- [PortSwigger Web Security Academy](https://portswigger.net/web-security/cross-site-scripting)
- [CSP Reference](https://content-security-policy.com/)

## Key Takeaways

1. **Never trust user input** - Always sanitize and encode
2. **Defense in depth** - Use multiple layers (encoding, CSP, httpOnly)
3. **Context matters** - Different contexts (HTML, JavaScript, URL) require different encoding
4. **Test thoroughly** - Use automated tools and manual testing
5. **Secure by default** - Use frameworks that auto-escape output

Remember: XSS vulnerabilities are preventable with proper input handling and output encoding!
