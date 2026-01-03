#!/bin/bash
# Validate MCP Privilege Escalation challenge completion

EXPECTED_FLAG="ARENA{MCP02_Pr1v1l3g3_3sc4l4t10n_N0_RBAC}"
USER_FLAG="$1"

if [ -z "$USER_FLAG" ]; then
    echo "❌ No flag provided"
    echo "Usage: arena validate <flag>"
    exit 1
fi

if [ "$USER_FLAG" == "$EXPECTED_FLAG" ]; then
    echo "✅ Correct! You successfully exploited the privilege escalation vulnerability!"
    echo ""
    echo "You discovered how MCP servers can fail to implement proper authorization:"
    echo "  • Missing role-based access control (RBAC)"
    echo "  • Admin tools accessible to standard users"
    echo "  • No permission validation before tool execution"
    echo ""
    echo "This is MCP02:2025 - Excessive Tool Permissions & Privilege Escalation"
    exit 0
else
    echo "❌ Incorrect flag"
    echo ""
    echo "Keep exploring the MCP server's authorization controls. Try:"
    echo "  • Check what user role you currently have"
    echo "  • Look for tools marked as 'admin only'"
    echo "  • Try calling privileged tools without admin access"
    echo "  • The server might not validate your permissions"
    exit 1
fi
