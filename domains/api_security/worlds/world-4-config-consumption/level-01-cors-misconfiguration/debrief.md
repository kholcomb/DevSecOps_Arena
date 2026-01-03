# CORS Misconfiguration

## OWASP API8:2023 - Security Misconfiguration

Overly permissive CORS allows malicious websites to read sensitive data.

## Fix: Whitelist Specific Origins
```python
ALLOWED_ORIGINS = ['https://myapp.com']
if origin in ALLOWED_ORIGINS:
    response.headers['Access-Control-Allow-Origin'] = origin
```

Never use `Access-Control-Allow-Origin: *` with credentials!
