#!/bin/bash
# Validate MCP Token Exposure challenge completion

EXPECTED_FLAG="ARENA{MCP01_T0k3n_L34k4g3_1s_D4ng3r0us}"
USER_FLAG="$1"

if [ -z "$USER_FLAG" ]; then
    echo "❌ No flag provided"
    echo "Usage: arena validate <flag>"
    exit 1
fi

if [ "$USER_FLAG" == "$EXPECTED_FLAG" ]; then
    echo "✅ Correct! You successfully exploited the token exposure vulnerability!"
    echo ""
    echo "You discovered how MCP servers can leak sensitive information through:"
    echo "  • Error messages containing debug data"
    echo "  • Accessible configuration files (.env)"
    echo "  • Verbose responses revealing internal state"
    echo ""
    echo "This is MCP01:2025 - Token Mismanagement & Secret Exposure"
    exit 0
else
    echo "❌ Incorrect flag"
    echo ""
    echo "Keep exploring the MCP server's responses. Try:"
    echo "  • Calling tools with invalid inputs"
    echo "  • Reading configuration files"
    echo "  • Examining error messages carefully"
    exit 1
fi
