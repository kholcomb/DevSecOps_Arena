# JWT None Algorithm Attack - Debrief

## Vulnerability Overview

The **JWT None Algorithm** vulnerability is part of **API2:2023 - Broken Authentication** in OWASP API Security Top 10:2023.

JWTs support multiple algorithms including 'none', which means no signature verification. If an API accepts the 'none' algorithm, attackers can forge tokens with arbitrary claims.

## What You Exploited

```python
# VULNERABLE CODE
payload = jwt.decode(
    token,
    SECRET_KEY,
    algorithms=['HS256', 'none'],  # Accepts 'none'!
    options={"verify_signature": True}
)
```

By creating a JWT with `"alg": "none"` and `"role": "admin"`, you bypassed authentication.

## How to Fix

### ✅ Secure Implementation
```python
# Only accept specific algorithms
payload = jwt.decode(
    token,
    SECRET_KEY,
    algorithms=['HS256'],  # Never include 'none'
    options={"verify_signature": True}
)
```

## Key Takeaways

1. **Never accept 'none' algorithm** in production
2. **Always verify signatures** explicitly
3. **Whitelist allowed algorithms** (HS256, RS256, etc.)
4. **Rotate secrets regularly**
5. **Use short expiration times** for tokens

## OWASP Mapping
- **API2:2023 - Broken Authentication** ✅
