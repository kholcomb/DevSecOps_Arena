# Challenge Debrief: Privilege Escalation (MCP02:2025)

## What You Just Exploited

You successfully exploited **Excessive Tool Permissions & Privilege Escalation (MCP02:2025)** - a vulnerability where MCP servers expose privileged administrative tools without implementing proper authorization controls.

### The Vulnerability

The MCP server you exploited had these critical flaws:

1. **No Authorization Checks:** Admin-only tools were accessible to standard users
2. **Missing RBAC:** No role-based access control implementation
3. **Tool Over-Exposure:** All tools exposed to all authenticated users
4. **Insufficient Permission Scoping:** No validation of caller permissions

### What Actually Happened

```
Standard User (guest_user)
    │
    ├─> list_all_users (admin tool)
    │   ✅ Executed without authorization check
    │   └─> Revealed system user accounts
    │
    ├─> create_admin_user (admin tool)
    │   ✅ Executed without authorization check
    │   └─> Created rogue admin account
    │
    └─> get_system_flag (admin tool)
        ✅ Executed without authorization check
        └─> Retrieved FLAG (sensitive system config)

❌ SERVER NEVER CHECKED: "Does this user have admin role?"
```

The server validated that the tools existed and parameters were correct, but **never verified if you had permission to execute them**.

---

## The Mental Model: Authentication vs Authorization

### Authentication (AuthN)
**Question:** "Who are you?"
- Proves identity (username, password, session token)
- You were authenticated as `guest_user`
- ✅ This server handled authentication

### Authorization (AuthZ)
**Question:** "What are you allowed to do?"
- Validates permissions for specific actions
- Should check: "Is guest_user allowed to call list_all_users?"
- ❌ This server **failed** to implement authorization

**Key Insight:** Being logged in (authenticated) doesn't mean you should have access to everything (authorized).

---

## Real-World Impact

### Case Study: AI Agent Platform Breach (2024)

**Scenario:** An AI development platform exposed MCP servers for automated workflows.

**Vulnerability:** MCP servers allowed any authenticated user to:
- Create admin accounts
- Access other users' data
- Execute system-level commands
- Modify billing settings

**Attack Timeline:**
1. Standard user account created (free tier)
2. Enumerated MCP tools via agent API
3. Called `create_admin_account` - succeeded without checks
4. Escalated to full admin privileges
5. Accessed 50,000 customer records
6. Exfiltrated proprietary AI models

**Business Impact:**
- $2.5M in regulatory fines (GDPR violations)
- 30% customer churn after disclosure
- 6 months of security remediation
- Class-action lawsuit from affected users

**Root Cause:** MCP server exposed admin tools without RBAC validation.

---

## Why Developers Make This Mistake

### 1. **Misunderstanding MCP Protocol**
Developers assume MCP protocol handles authorization - it doesn't. MCP only defines the communication format, not security policies.

### 2. **Trusting the AI Agent**
"The AI agent will only call appropriate tools" - **WRONG**. Agents can be manipulated via prompt injection or may have bugs.

### 3. **Development Convenience**
During development, disabling auth checks speeds up testing. Forgetting to re-enable them in production is common.

### 4. **Monolithic Tool Registration**
Registering all tools in a single list makes it easy to accidentally expose admin tools to all users.

---

## How to Fix This

### Proper RBAC Implementation

```python
class SecureMCPServer(VulnerableMCPServer):
    """MCP server with proper authorization controls"""

    # Define permission requirements for each tool
    TOOL_PERMISSIONS = {
        "get_user_info": ["user", "admin"],
        "list_files": ["user", "admin"],
        "create_admin_user": ["admin"],  # Admin only
        "list_all_users": ["admin"],     # Admin only
        "get_system_flag": ["admin"],    # Admin only
    }

    def get_tools(self) -> List[Dict[str, Any]]:
        """Only return tools the current user is authorized to see"""
        user_role = self.get_current_user_role()
        authorized_tools = []

        for tool in self.all_tools:
            required_permissions = self.TOOL_PERMISSIONS.get(tool["name"], [])
            if user_role in required_permissions:
                authorized_tools.append(tool)

        return authorized_tools

    async def execute_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Validate authorization before execution"""
        user_role = self.get_current_user_role()
        required_permissions = self.TOOL_PERMISSIONS.get(name, [])

        # Authorization check
        if user_role not in required_permissions:
            logger.warning(
                f"Authorization denied: {self.get_current_user()} "
                f"(role={user_role}) attempted to call {name}"
            )
            return {
                "content": [{
                    "type": "text",
                    "text": f"Error: Insufficient permissions. "
                           f"Tool '{name}' requires one of: {required_permissions}"
                }],
                "isError": True
            }

        # Execute only if authorized
        return await super().execute_tool(name, arguments)
```

### Defense in Depth Layers

1. **Tool Filtering:** Don't expose admin tools in tool list for standard users
2. **Execution Validation:** Check permissions before executing any tool
3. **Audit Logging:** Log all tool calls with user identity and role
4. **Rate Limiting:** Prevent brute-force privilege testing
5. **Alerting:** Notify security team of authorization failures

---

## Interview Questions You Can Now Answer

### Junior Level

**Q:** "What's the difference between authentication and authorization?"

**A:** "Authentication verifies who you are (identity), while authorization determines what you're allowed to do (permissions). You can be authenticated but not authorized for specific actions. In the MCP challenge, I was authenticated as guest_user but the server failed to authorize my access to admin tools."

### Mid Level

**Q:** "How would you implement RBAC for an MCP server?"

**A:** "I'd implement a multi-layer approach: (1) Define permission requirements for each tool, (2) Filter tool list based on user role, (3) Validate permissions before executing tools, (4) Maintain audit logs, (5) Implement defense in depth with tool filtering AND execution validation. This prevents both discovery and exploitation of privileged tools."

### Senior Level

**Q:** "An MCP server needs to support different permission models (RBAC, ABAC, custom). How would you architect this?"

**A:** "I'd create an authorization interface with pluggable backends: (1) Abstract AuthorizationProvider interface, (2) Concrete implementations (RBACProvider, ABACProvider, etc.), (3) Tool decorators for permission metadata, (4) Centralized authorization middleware, (5) Policy as code for complex rules. This allows flexibility while maintaining consistent enforcement at the execution boundary."

---

## Commands You Mastered

### MCP Security Audit Commands

```bash
# Enumerate available tools
curl http://localhost:9002/mcp -X POST -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'

# Test authorization bypass
curl http://localhost:9002/mcp -X POST -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"list_all_users","arguments":{}}}'

# Extract sensitive data
curl http://localhost:9002/mcp -X POST -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"get_system_flag","arguments":{}}}'
```

---

## Key Takeaways

✅ **Always implement authorization, not just authentication**
- Authentication proves identity
- Authorization validates permissions
- Both are required for security

✅ **Follow least privilege principle**
- Only expose tools users need
- Filter tool lists by role
- Validate permissions at execution

✅ **Defense in depth**
- Don't rely on a single security layer
- Combine tool filtering + execution validation
- Add logging, monitoring, and alerting

✅ **Assume compromise**
- Design systems expecting attackers to enumerate tools
- Make authorization failures noisy (logs, alerts)
- Implement rate limiting on sensitive operations

---

## OWASP MCP Top 10:2025 Context

**MCP02:2025 - Excessive Tool Permissions & Privilege Escalation**

**Rank:** #2 (Very High Severity)

**Why It's Common:**
- MCP protocol doesn't mandate authorization
- Easy to forget during rapid development
- Complexity of implementing RBAC correctly
- Trusting AI agents to "do the right thing"

**Prevention Checklist:**
- [ ] Define permission requirements for each tool
- [ ] Implement RBAC with role-based tool filtering
- [ ] Validate permissions before tool execution
- [ ] Audit and log all privileged operations
- [ ] Test with different user roles
- [ ] Review tool exposure in security assessments

---

## Next Steps

Practice secure MCP development:
1. Review OWASP MCP Top 10:2025 full specification
2. Study authorization patterns (RBAC, ABAC, ReBAC)
3. Implement authorization in your own MCP servers
4. Test with security scanning tools
5. Continue to Level 03: Tool Poisoning

**Congratulations!** You've mastered privilege escalation vulnerabilities in MCP servers. +120 XP 🎉
