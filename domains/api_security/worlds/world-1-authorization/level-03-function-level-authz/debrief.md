# Broken Function Level Authorization - Debrief

## Vulnerability Overview

**Broken Function Level Authorization** is **API5:2023** in the OWASP API Security Top 10:2023.

This occurs when administrative or privileged API functions are accessible to unauthorized users because the API:
1. Doesn't properly check user roles/permissions before executing sensitive functions
2. Relies on obscurity (hidden endpoints) instead of proper access control
3. Implements client-side restrictions that can be bypassed

## What You Exploited

The `DELETE /api/users/<user_id>` endpoint was accessible to any authenticated user:

```python
# VULNERABLE CODE
@app.route('/api/users/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    # Only checks authentication
    if not valid_api_key(request.headers.get('API-Key')):
        return 401

    # MISSING: Role/permission check!
    # Should verify user is admin

    delete_user_from_db(user_id)
    return {"success": True}
```

## Real-World Impact

- **Data Destruction:** Unauthorized deletion of records
- **Privilege Escalation:** Access to admin-only functions
- **Business Logic Bypass:** Manipulating orders, refunds, transactions
- **Account Takeover:** Resetting passwords, changing permissions

### Real Examples
1. **Facebook (2016):** Delete any video via undocumented API endpoint
2. **Bumble (2020):** Admin API endpoints accessible to regular users
3. **Various APIs:** Unprotected POST/PUT/DELETE methods on resources

## How to Fix It

### ❌ Vulnerable
```python
@app.route('/api/users/<id>', methods=['DELETE'])
def delete_user(id):
    if not authenticated():
        return 401
    # No authorization check!
    delete(id)
    return 200
```

### ✅ Secure
```python
@app.route('/api/users/<id>', methods=['DELETE'])
def delete_user(id):
    current_user = get_authenticated_user()
    if not current_user:
        return 401

    # AUTHORIZATION CHECK
    if current_user.role != 'admin':
        return {"error": "Forbidden"}, 403

    delete(id)
    return 200
```

## Defense Strategies

### 1. Implement Role-Based Access Control (RBAC)
```python
from functools import wraps

def require_role(role):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if current_user.role != role:
                return {"error": "Forbidden"}, 403
            return f(*args, **kwargs)
        return wrapper
    return decorator

@app.route('/api/admin/users', methods=['DELETE'])
@require_role('admin')
def delete_user():
    # Authorization already checked
    pass
```

### 2. Default Deny Access
All endpoints should deny access by default, explicitly allowing only authorized roles:
```python
# Centralized authorization
ENDPOINT_PERMISSIONS = {
    'DELETE /api/users': ['admin'],
    'POST /api/orders/refund': ['admin', 'support'],
    'GET /api/users': ['admin', 'user']
}
```

### 3. Separate Admin Endpoints
Use distinct URL paths for admin functions:
```python
# User endpoints
/api/users          GET  - All authenticated
/api/users/:id      GET  - All authenticated

# Admin endpoints (with prefix)
/api/admin/users          GET, POST, DELETE  - Admins only
/api/admin/users/:id      PUT, DELETE        - Admins only
```

### 4. Test ALL HTTP Methods
Ensure every HTTP method on every endpoint has proper authorization:
- GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS

## Testing for Function-Level Authorization

### Manual Testing
1. **Enumerate endpoints** - Check documentation, JavaScript files, proxy logs
2. **Try all HTTP methods** on each endpoint
3. **Access admin paths** - /admin, /api/admin, /api/v1/admin
4. **Test with different roles** - Can regular user access admin functions?

### Automated Testing
- **Burp Suite Autorize** - Replays requests with different user privileges
- **OWASP ZAP Access Control Testing**
- **Postman Collection Tests** - Test each endpoint with multiple user roles

## Key Takeaways

1. **Document ≠ Secure** - Hiding endpoints from docs doesn't protect them
2. **Test Every HTTP Method** - Don't assume only GET is implemented
3. **Explicit Authorization** - Check permissions on EVERY endpoint
4. **Separate Admin Functions** - Use distinct paths and clear RBAC

## OWASP API Security Top 10:2023 Mapping

- **API5:2023 - Broken Function Level Authorization** ✅ This challenge

## Further Learning

- [OWASP API Security](https://owasp.org/API-Security/)
- [PortSwigger: Access Control](https://portswigger.net/web-security/access-control)
- [OWASP Testing Guide: Testing for Function Level Authorization](https://owasp.org/www-project-web-security-testing-guide/)
