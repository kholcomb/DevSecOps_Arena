#!/bin/bash
# Validate MCP Tool Poisoning challenge completion

EXPECTED_FLAG="ARENA{MCP03_T00l_P01s0n1ng_H1dd3n_1nstruct10ns}"
USER_FLAG="$1"

if [ -z "$USER_FLAG" ]; then
    echo "❌ No flag provided"
    echo "Usage: arena validate <flag>"
    exit 1
fi

if [ "$USER_FLAG" == "$EXPECTED_FLAG" ]; then
    echo "✅ Correct! You successfully exploited the tool poisoning vulnerability!"
    echo ""
    echo "You discovered how MCP tool descriptions can be weaponized:"
    echo "  • Hidden instructions embedded in tool metadata"
    echo "  • Context injection to manipulate AI agent behavior"
    echo "  • Bypassing security through malicious tool descriptions"
    echo ""
    echo "This is MCP03:2025 - Tool Poisoning & Malicious Descriptions"
    exit 0
else
    echo "❌ Incorrect flag"
    echo ""
    echo "Keep exploring the MCP server's tool descriptions. Try:"
    echo "  • List all available tools with full descriptions"
    echo "  • Look for suspicious instructions in tool metadata"
    echo "  • Check for hidden directives that manipulate AI behavior"
    echo "  • Try following the poisoned instructions"
    exit 1
fi
