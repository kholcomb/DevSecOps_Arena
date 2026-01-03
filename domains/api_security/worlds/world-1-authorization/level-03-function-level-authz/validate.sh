#!/bin/bash
EXPECTED_FLAG="ARENA{func_lvl_4uthz_byp4ss}"

if [ -z "$1" ]; then
    echo "❌ No flag provided"
    echo "Usage: ./validate.sh <flag>"
    exit 1
fi

if [ "$1" = "$EXPECTED_FLAG" ]; then
    echo "✅ Correct flag! Challenge completed!"
    exit 0
else
    echo "❌ Incorrect flag: $1"
    echo "Hint: Find and use the hidden DELETE endpoint."
    exit 1
fi
