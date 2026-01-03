# SSRF - Server-Side Request Forgery

## OWASP API7:2023

SSRF allows attackers to make the server send requests to unintended locations, including:
- Internal services (metadata services, databases, admin panels)
- Cloud provider metadata endpoints
- Internal network resources

## Fix: Validate and Whitelist URLs
```python
ALLOWED_DOMAINS = ['example.com', 'api.trusted.com']
parsed = urlparse(url)
if parsed.hostname not in ALLOWED_DOMAINS:
    return {"error": "URL not allowed"}, 403
```
