#!/bin/bash
# Flag validation script for Level 05: Command Injection

EXPECTED_FLAG="ARENA{MCP05_C0mm4nd_1nj3ct10n_PWN3D}"

if [ -z "$1" ]; then
    echo "Usage: $0 <flag>"
    exit 1
fi

SUBMITTED_FLAG="$1"

if [ "$SUBMITTED_FLAG" = "$EXPECTED_FLAG" ]; then
    echo "SUCCESS"
    exit 0
else
    echo "FAILURE: Incorrect flag"
    exit 1
fi
