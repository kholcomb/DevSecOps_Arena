# MCP01: Token Mismanagement & Secret Exposure

## What You Learned

### The Vulnerability

MCP servers can expose sensitive tokens and secrets through multiple attack vectors:

1. **Error Messages with Debug Information**
   - Developers often include debug data in error messages
   - Production servers with debug mode enabled leak internal state
   - Error handlers that don't sanitize responses

2. **Accessible Configuration Files**
   - `.env` files containing secrets stored in accessible locations
   - Missing access controls on sensitive resources
   - File reading tools without proper path validation

3. **Information Disclosure in Responses**
   - Tool responses that include server state
   - Verbose error messages revealing internal paths
   - Debug endpoints left enabled in production

### Real-World Impact

Token exposure vulnerabilities have led to:

- **API Key Theft**: Leaked OpenAI API keys resulting in thousands of dollars in unauthorized usage
- **Database Breaches**: Exposed database credentials enabling full data exfiltration
- **Cloud Account Compromise**: AWS/Azure credentials in config files leading to resource hijacking
- **Lateral Movement**: Service account tokens allowing attackers to access other systems
- **Supply Chain Attacks**: Compromised tokens in public repositories affecting downstream users

### OWASP MCP Top 10 Context

This challenge demonstrates **MCP01:2025 - Token Mismanagement & Secret Exposure**:

> "Hard-coded credentials, long-lived tokens, and secrets stored in model memory or protocol logs can expose sensitive environments to unauthorized access."

Attack scenarios include:
- Retrieving tokens through prompt injection
- Accessing secrets via compromised context
- Extracting credentials from debug traces
- Reading configuration files with overly permissive tools

## Mitigation Strategies

### For MCP Server Developers

1. **Sanitize Error Messages**
   ```python
   # BAD - Leaks internal state
   return {"error": f"Failed: {exception}, API_KEY={self.api_key}"}

   # GOOD - Generic error message
   return {"error": "Request failed", "code": "INTERNAL_ERROR"}
   ```

2. **Never Log Secrets**
   ```python
   # BAD - Logs API key
   logger.info(f"Initializing with key: {api_key}")

   # GOOD - Redact sensitive data
   logger.info(f"Initializing with key: {api_key[:8]}...")
   ```

3. **Restrict File Access**
   ```python
   # BAD - No path validation
   def read_file(path):
       return open(path).read()

   # GOOD - Whitelist allowed paths
   ALLOWED_PATHS = ["/workspace/public/"]
   def read_file(path):
       if not any(path.startswith(allowed) for allowed in ALLOWED_PATHS):
           raise PermissionError("Access denied")
       return open(path).read()
   ```

4. **Use Environment Variables Properly**
   - Never commit `.env` files to repositories
   - Use secret management systems (AWS Secrets Manager, HashiCorp Vault)
   - Implement proper access controls on configuration files
   - Rotate credentials regularly

5. **Implement Proper Error Handling**
   ```python
   # BAD - Exposes stack trace
   except Exception as e:
       return {"error": str(e), "trace": traceback.format_exc()}

   # GOOD - Log internally, return generic error
   except Exception as e:
       logger.error(f"Internal error: {e}", exc_info=True)
       return {"error": "An error occurred", "code": "SERVER_ERROR"}
   ```

### For MCP Client Developers

1. **Validate Server Responses**
   - Check for sensitive patterns in responses
   - Alert on unexpected data in error messages
   - Monitor for credential-like strings

2. **Implement Response Filtering**
   ```python
   SENSITIVE_PATTERNS = [r'sk-[a-zA-Z0-9]{32,}', r'password[:=]', r'api[_-]?key']

   def validate_response(response):
       for pattern in SENSITIVE_PATTERNS:
           if re.search(pattern, str(response)):
               logger.warning("Sensitive data detected in response!")
   ```

3. **Audit MCP Servers**
   - Review server code before connecting
   - Check for proper error handling
   - Verify access controls on tools/resources

### For AI Agent Users

1. **Audit MCP Servers Before Use**
   - Review server source code if available
   - Check for debug mode indicators
   - Test with invalid inputs to see error responses

2. **Monitor Agent Interactions**
   - Review logs for sensitive data exposure
   - Watch for unexpected server responses
   - Alert on credential-like patterns

3. **Use Least-Privilege Configurations**
   - Only connect to trusted MCP servers
   - Limit tool permissions where possible
   - Regularly rotate any credentials the server might access

## Prevention Checklist

- [ ] Sanitize all error messages before returning to clients
- [ ] Never include secrets in error messages or debug output
- [ ] Implement proper access controls on file reading tools
- [ ] Use secret management systems instead of .env files
- [ ] Remove debug endpoints from production deployments
- [ ] Audit server responses for information disclosure
- [ ] Implement proper logging that redacts sensitive data
- [ ] Use environment variables correctly (never commit them)
- [ ] Add automated tests for information disclosure
- [ ] Regularly scan codebase for hardcoded secrets

## Further Reading

- [OWASP MCP Top 10 - MCP01:2025](https://owasp.org/www-project-mcp-top-10/)
- [Model Context Protocol Specification](https://modelcontextprotocol.io)
- [OWASP Top 10 - Security Logging and Monitoring Failures](https://owasp.org/Top10/A09_2021-Security_Logging_and_Monitoring_Failures/)
- [OWASP Sensitive Data Exposure](https://owasp.org/www-community/vulnerabilities/Information_exposure_through_query_strings_in_url)

## Next Steps

Continue to **World 1, Level 2: Privilege Escalation** to learn about MCP02:2025 - Privilege Escalation via Scope Creep.

Congratulations on completing your first MCP security challenge! 🎉
