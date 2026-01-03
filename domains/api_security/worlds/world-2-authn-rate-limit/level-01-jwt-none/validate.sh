#!/bin/bash
EXPECTED_FLAG="ARENA{jwt_n0n3_alg0r1thm_byp4ss}"
if [ -z "$1" ]; then
    echo "❌ No flag provided. Usage: ./validate.sh <flag>"
    exit 1
fi
if [ "$1" = "$EXPECTED_FLAG" ]; then
    echo "✅ Correct flag! Challenge completed!"
    exit 0
else
    echo "❌ Incorrect flag: $1"
    exit 1
fi
