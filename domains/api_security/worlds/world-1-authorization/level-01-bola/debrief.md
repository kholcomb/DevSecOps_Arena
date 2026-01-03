# BOLA (Broken Object Level Authorization) - Debrief

## Vulnerability Overview

**BOLA** (Broken Object Level Authorization), also known as **IDOR** (Insecure Direct Object Reference), is the **#1 risk** in the OWASP API Security Top 10:2023.

This vulnerability occurs when an API endpoint:
1. ✅ **Authenticates** the user (checks if they're logged in)
2. ❌ **Fails to authorize** whether that user should access the specific resource

## What You Exploited

The `/api/users/<user_id>` endpoint had a critical flaw:

```python
# VULNERABLE CODE
@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    # Check authentication (is user logged in?)
    api_key = request.headers.get('API-Key')
    if not api_key or not valid_key(api_key):
        return {"error": "Unauthorized"}, 401

    # MISSING: Authorization check!
    # Should verify: Does authenticated_user have permission to access user_id?

    # Directly returns ANY user's data
    return USERS[user_id]
```

**The Problem:** The API checked if you had a valid API key but never checked if you were allowed to access user ID 2's data.

## Real-World Impact

BOLA vulnerabilities are extremely common and dangerous:

- **Financial Impact:** Access to other users' bank accounts, transactions, invoices
- **Privacy Breach:** Access to personal data, medical records, private messages
- **Business Logic Bypass:** Manipulate other users' orders, bookings, subscriptions

### Notable Real-World Examples

1. **Venmo (2019):** Could access any user's transaction history by changing user IDs
2. **Peloton (2021):** Could access any user's private profile data and activity
3. **T-Mobile (2022):** API exposed customer data via IDOR vulnerability

## How to Fix It

### ❌ Vulnerable Code
```python
def get_user(user_id):
    if not authenticated():
        return 401
    return USERS[user_id]  # Returns ANY user's data
```

### ✅ Secure Code
```python
def get_user(user_id):
    current_user = get_authenticated_user()
    if not current_user:
        return 401

    # AUTHORIZATION CHECK
    if current_user.id != user_id and not current_user.is_admin:
        return {"error": "Forbidden"}, 403

    return USERS[user_id]
```

## Defense Strategies

### 1. Implement Authorization Checks
Always verify the authenticated user has permission to access the requested resource:
```python
# Check ownership
if resource.owner_id != current_user.id:
    return 403

# Or check role-based access
if not current_user.has_permission('view_user', user_id):
    return 403
```

### 2. Use Indirect References
Instead of exposing internal IDs, use random tokens or UUIDs:
```python
# Instead of: /api/users/123
# Use: /api/users/7f3a9c2b-4d1e-4a8f-9b2c-5e6d7f8a9b0c
```

### 3. Implement an Authorization Framework
Use a consistent authorization layer across all endpoints:
```python
from flask_principal import Permission, RoleNeed

@app.route('/api/users/<user_id>')
@permission_required('view_user')  # Decorator enforces authz
def get_user(user_id):
    # Authorization already checked
    return USERS[user_id]
```

### 4. Default Deny
Only return data that the current user owns by default:
```python
def get_user_orders():
    # Automatically filter by current user
    orders = Order.query.filter_by(user_id=current_user.id).all()
    return orders
```

## Testing for BOLA

### Manual Testing
1. Authenticate as User A
2. Note a resource ID accessible to User A (e.g., `/api/orders/123`)
3. Authenticate as User B
4. Try to access User A's resource using User B's credentials
5. If successful → BOLA vulnerability

### Automated Testing
Use tools like:
- **Burp Suite Autorize extension**
- **OWASP ZAP with AutoAuthz plugin**
- **Custom scripts** that test access control across different user roles

## Key Takeaways

1. **Authentication ≠ Authorization**
   - Authentication: "Who are you?"
   - Authorization: "Are you allowed to do this?"

2. **Never Trust User Input**
   - User IDs in URLs/parameters can be manipulated

3. **Every Endpoint Needs Authz**
   - Even "read-only" endpoints can leak sensitive data

4. **Test with Multiple Users**
   - Test if User A can access User B's resources

## OWASP API Security Top 10:2023 Mapping

- **API1:2023 - Broken Object Level Authorization** ✅ This challenge
- Related to API5:2023 (Broken Function Level Authorization)

## Further Learning

- [OWASP API Security Project](https://owasp.org/www-project-api-security/)
- [PortSwigger: Access Control Vulnerabilities](https://portswigger.net/web-security/access-control)
- [OWASP Testing Guide: Authorization Testing](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/05-Authorization_Testing/)
