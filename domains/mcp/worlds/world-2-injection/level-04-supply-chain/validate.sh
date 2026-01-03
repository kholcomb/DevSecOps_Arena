#!/bin/bash
# Flag validation script for Level 04: Supply Chain Compromise

EXPECTED_FLAG="ARENA{MCP04_Supply_Ch41n_C0mpr0m1s3}"

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
