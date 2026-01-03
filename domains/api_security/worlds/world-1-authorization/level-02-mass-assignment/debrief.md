# Mass Assignment - Debrief

## Vulnerability Overview

**Mass Assignment** (also called **Auto-binding** or **Object Injection**) is part of **API3:2023 - Broken Object Property Level Authorization** in the OWASP API Security Top 10:2023.

This vulnerability occurs when an API automatically binds client-provided data (from JSON, form data, query parameters) to code variables or objects without proper filtering of which properties should be modifiable.

## What You Exploited

The `/api/profile` PUT endpoint blindly accepted all fields from the request:

```python
# VULNERABLE CODE
@app.route('/api/profile', methods=['PUT'])
def update_profile():
    data = request.get_json()

    # VULNERABLE: Updates ALL fields from request
    for key, value in data.items():
        user[key] = value

    return {"success": True}
```

**The Problem:** The API didn't validate which fields users should be allowed to modify. You exploited this to change your `role` from `"user"` to `"admin"`.

## Real-World Impact

Mass assignment vulnerabilities have led to serious breaches:

- **Privilege Escalation:** Change role from user to admin
- **Financial Fraud:** Modify account_balance, is_premium, pricing fields
- **Account Takeover:** Change email, password_reset_token
- **Business Logic Bypass:** Modify discount_applied, order_status

### Notable Real-World Examples

1. **GitHub (2012):** Mass assignment allowed users to add themselves as collaborators to any repository
2. **Ruby on Rails Apps:** Framework's auto-binding made mass assignment a common vulnerability
3. **Peloton (2021):** Could modify subscription level and payment status via mass assignment

## How to Fix It

### ❌ Vulnerable Code
```python
def update_profile():
    data = request.get_json()
    for key, value in data.items():
        user[key] = value  # Accepts ANY field
    return user
```

### ✅ Secure Code - Whitelist Approach
```python
def update_profile():
    data = request.get_json()

    # Whitelist of allowed fields
    ALLOWED_FIELDS = ['username', 'email', 'bio']

    # Only update allowed fields
    for key in ALLOWED_FIELDS:
        if key in data:
            user[key] = data[key]

    return user
```

### ✅ Alternative - Explicit Assignment
```python
def update_profile():
    data = request.get_json()

    # Explicitly set each allowed field
    if 'username' in data:
        user['username'] = data['username']
    if 'email' in data:
        user['email'] = data['email']
    if 'bio' in data:
        user['bio'] = data['bio']

    # Sensitive fields like 'role' are never assigned from user input
    return user
```

## Defense Strategies

### 1. Use DTOs (Data Transfer Objects)
Define explicit objects for API inputs:

```python
from pydantic import BaseModel

class ProfileUpdateRequest(BaseModel):
    username: str | None = None
    email: str | None = None
    bio: str | None = None
    # 'role' is NOT in the DTO, so it can't be set

@app.route('/api/profile', methods=['PUT'])
def update_profile():
    # Pydantic validates and only allows defined fields
    update_data = ProfileUpdateRequest(**request.get_json())
    # ... update logic
```

### 2. Use Read-Only Fields
Mark sensitive fields as read-only in your ORM:

```python
class User(db.Model):
    username = db.Column(db.String(50))
    email = db.Column(db.String(100))
    role = db.Column(db.String(20), readonly=True)  # Can't be mass-assigned
```

### 3. Separate Update Methods
Have different endpoints for different types of updates:

```python
PUT /api/profile/basic    # Updates username, email, bio
PUT /api/profile/settings # Updates preferences, notifications
POST /api/admin/promote   # Only admins can change roles
```

### 4. Input Validation + Blacklist
As a defense-in-depth measure, also blacklist sensitive fields:

```python
FORBIDDEN_FIELDS = ['role', 'is_admin', 'account_balance', 'api_key']

for key in data.keys():
    if key in FORBIDDEN_FIELDS:
        return {"error": f"Field '{key}' cannot be modified"}, 400
```

## Testing for Mass Assignment

### Manual Testing
1. Identify update/create endpoints
2. Inspect the data model (or guess common sensitive fields)
3. Try adding fields like:
   - `role`, `is_admin`, `is_staff`
   - `account_balance`, `credits`, `points`
   - `email_verified`, `is_premium`
   - `price`, `discount`, `total`
4. Check if the extra fields are accepted

### Automated Testing
- **Burp Suite:** Intruder with field fuzzing wordlists
- **OWASP ZAP:** Active scanning for parameter pollution
- **Custom scripts:** Enumerate model fields and try setting each

## Framework-Specific Guidance

### Ruby on Rails
```ruby
# Vulnerable
def update
  @user.update(params[:user])  # Mass assignment vulnerability
end

# Secure
def update
  @user.update(user_params)
end

private
def user_params
  params.require(:user).permit(:username, :email, :bio)  # Whitelist
end
```

### Django
```python
# Vulnerable
user.__dict__.update(request.data)

# Secure - use ModelSerializer with explicit fields
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'bio']  # Whitelist
        read_only_fields = ['role', 'is_staff']
```

## Key Takeaways

1. **Never Auto-Bind User Input** - Always explicitly define what can be modified
2. **Whitelist > Blacklist** - Explicitly allow fields rather than block fields
3. **Use DTOs/Schemas** - Leverage libraries like Pydantic, Marshmallow, Joi
4. **Separate Concerns** - Different endpoints for different privilege levels
5. **Defense in Depth** - Combine whitelisting, validation, and authorization checks

## OWASP API Security Top 10:2023 Mapping

- **API3:2023 - Broken Object Property Level Authorization** ✅ This challenge
- Related to API1:2023 (BOLA) and API5:2023 (Function-Level Authorization)

## Further Learning

- [OWASP Mass Assignment Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Mass_Assignment_Cheat_Sheet.html)
- [PortSwigger: Server-side parameter pollution](https://portswigger.net/web-security/server-side-parameter-pollution)
- [CWE-915: Improperly Controlled Modification of Dynamically-Determined Object Attributes](https://cwe.mitre.org/data/definitions/915.html)
