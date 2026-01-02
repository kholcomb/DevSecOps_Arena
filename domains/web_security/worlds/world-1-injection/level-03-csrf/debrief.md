# CSRF Challenge - Debrief

## Vulnerability Explained

**Cross-Site Request Forgery (CSRF)** is an attack that forces an authenticated user to execute unwanted actions on a web application in which they're currently authenticated. Attackers trick victims into submitting malicious requests without their knowledge.

### What Happened

The vulnerable banking application accepted state-changing POST requests without verifying that the request originated from a legitimate source:

```python
# VULNERABLE CODE
@app.route('/transfer', methods=['POST'])
def transfer():
    session_user = request.cookies.get('session_user')
    to_user = request.form.get('to', '')
    amount = int(request.form.get('amount', 0))

    # No CSRF token validation!
    # Accepts any POST request with valid session cookie
    users[session_user]['balance'] -= amount
    users[to_user]['balance'] += amount
```

When you clicked the button on the attacker's site, it submitted a hidden form to the banking app. Because you were logged in, your browser automatically included your session cookie, making the bank think the request was legitimate.

### Attack Flow

1. **Victim logs in**: User authenticates to the banking app (alice)
2. **Session established**: Browser stores session cookie
3. **Attacker lures victim**: User visits malicious site (http://localhost:3004)
4. **Hidden form submits**: JavaScript/auto-submit triggers transfer request
5. **Browser sends cookie**: Browser automatically includes session cookie
6. **Bank processes request**: Server can't distinguish legitimate from forged request
7. **Money transferred**: $500 goes from alice to attacker
8. **Flag revealed**: Challenge complete

### Why This Worked

Three factors enabled this attack:

1. **No CSRF Token**: The transfer endpoint didn't validate request origin
2. **Automatic Cookie Submission**: Browsers include cookies with all requests to a domain
3. **Simple Form POST**: The attack only required a basic HTML form

## Real-World Impact

CSRF vulnerabilities can lead to:

- **Financial Fraud**: Unauthorized money transfers, purchases
- **Account Takeover**: Password changes, email updates
- **Data Modification**: Changing user settings, posting content
- **Privilege Escalation**: Adding admin users, changing permissions
- **State-Changing Actions**: Any action that modifies server-side data

### Famous CSRF Attacks

- **YouTube (2008)**: CSRF allowed posting comments as any user
- **Netflix (2006)**: CSRF enabled adding items to queues, changing account details
- **Gmail (2007)**: CSRF allowed email filters to forward emails to attackers
- **ING Direct (2008)**: CSRF enabled money transfers from victims' accounts

## Mitigation Strategies

### 1. Synchronizer Token Pattern (Primary Defense)

Generate unique, unpredictable tokens for each session or request:

```python
# SECURE CODE
import secrets

# In session initialization
session['csrf_token'] = secrets.token_hex(32)

# In template
<form action="/transfer" method="POST">
    <input type="hidden" name="csrf_token" value="{{ session.csrf_token }}">
    ...
</form>

# In endpoint
@app.route('/transfer', methods=['POST'])
def transfer():
    # Validate CSRF token
    user_token = request.form.get('csrf_token')
    session_token = session.get('csrf_token')

    if not user_token or user_token != session_token:
        return "CSRF token validation failed", 403

    # Process transfer...
```

### 2. SameSite Cookie Attribute

Prevent cookies from being sent with cross-site requests:

```python
response.set_cookie(
    'session_user',
    username,
    samesite='Strict',  # or 'Lax'
    secure=True,        # HTTPS only
    httponly=True       # No JavaScript access
)
```

**SameSite values:**
- `Strict`: Cookie never sent on cross-site requests
- `Lax`: Cookie sent on top-level navigation (GET requests)
- `None`: Cookie sent on all requests (requires Secure flag)

### 3. Double Submit Cookie Pattern

Send token both as cookie and request parameter:

```python
# Set CSRF token cookie
csrf_token = secrets.token_hex(32)
response.set_cookie('csrf_token', csrf_token, samesite='Strict')

# In form
<input type="hidden" name="csrf_token" value="{{ csrf_token }}">

# Validation
cookie_token = request.cookies.get('csrf_token')
form_token = request.form.get('csrf_token')

if not cookie_token or cookie_token != form_token:
    return "CSRF validation failed", 403
```

### 4. Custom Request Headers

Use AJAX with custom headers (cannot be set cross-origin):

```javascript
// Frontend
fetch('/transfer', {
    method: 'POST',
    headers: {
        'X-CSRF-Token': csrfToken,
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({to: 'bob', amount: 100})
});
```

```python
# Backend
@app.route('/transfer', methods=['POST'])
def transfer():
    csrf_token = request.headers.get('X-CSRF-Token')
    if not csrf_token or csrf_token != session.get('csrf_token'):
        return "CSRF validation failed", 403
```

### 5. Re-Authentication for Sensitive Actions

Require password confirmation for critical operations:

```python
@app.route('/transfer', methods=['POST'])
def transfer():
    password = request.form.get('confirm_password')
    if not verify_password(session['user'], password):
        return "Password confirmation required", 403

    # Process transfer...
```

### 6. Framework Built-In Protection

Use web framework CSRF protection:

```python
# Flask with Flask-WTF
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
csrf = CSRFProtect(app)

# Django (enabled by default)
# {% csrf_token %} in templates

# Express.js with csurf
const csrf = require('csurf');
app.use(csrf());
```

## Defense Patterns Comparison

| Method | Effectiveness | Complexity | Notes |
|--------|--------------|------------|-------|
| Synchronizer Token | ⭐⭐⭐⭐⭐ | Medium | Gold standard, most reliable |
| SameSite Cookies | ⭐⭐⭐⭐ | Low | Modern browsers only |
| Double Submit | ⭐⭐⭐⭐ | Low | Good for stateless apps |
| Custom Headers | ⭐⭐⭐ | Medium | AJAX only, won't work with forms |
| Re-Authentication | ⭐⭐⭐ | High | High friction, sensitive actions only |

## Testing for CSRF

### Manual Testing

1. Log in to application
2. Intercept a state-changing request (Burp Suite)
3. Create HTML form replicating the request
4. Visit the HTML file while logged in
5. Check if action was performed

### Testing Tools

- **Burp Suite**: Generate CSRF PoC
- **OWASP ZAP**: CSRF scanner
- **CSRFTester**: Automated CSRF testing

### Example Test HTML

```html
<html>
<body>
    <form action="http://target.com/transfer" method="POST">
        <input type="hidden" name="to" value="attacker">
        <input type="hidden" name="amount" value="1000">
        <input type="submit" value="Click me!">
    </form>
    <script>
        // Auto-submit on page load
        document.forms[0].submit();
    </script>
</body>
</html>
```

## Prevention Checklist

- [ ] Implement CSRF tokens for all state-changing requests
- [ ] Set SameSite attribute on session cookies
- [ ] Use framework built-in CSRF protection
- [ ] Validate Origin and Referer headers (secondary defense)
- [ ] Require re-authentication for sensitive actions
- [ ] Implement rate limiting
- [ ] Use HTTPS only (Secure flag on cookies)
- [ ] Log and monitor suspicious request patterns
- [ ] Educate users about phishing and social engineering
- [ ] Regular security testing and code reviews

## Common Mistakes

1. **Only checking Referer header**: Can be spoofed or stripped
2. **Using GET for state changes**: Never use GET for modifications
3. **Token in URL**: Tokens leak through browser history, logs
4. **Same token for all users**: Defeats the purpose
5. **Not validating token server-side**: Client-side checks are useless

## References

- [OWASP CSRF Guide](https://owasp.org/www-community/attacks/csrf)
- [PortSwigger CSRF Tutorial](https://portswigger.net/web-security/csrf)
- [MDN SameSite Cookies](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Set-Cookie/SameSite)
- [CSRF Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)

## Key Takeaways

1. **State-changing requests need CSRF protection** - Always validate origin
2. **Defense in depth** - Use multiple protections (tokens + SameSite)
3. **Framework defaults** - Use built-in CSRF protection
4. **User education** - Train users to recognize phishing
5. **Test thoroughly** - Manual testing + automated scans
6. **GET is safe, POST is protected** - Never use GET for modifications

Remember: CSRF is preventable with proper token validation and cookie settings!
