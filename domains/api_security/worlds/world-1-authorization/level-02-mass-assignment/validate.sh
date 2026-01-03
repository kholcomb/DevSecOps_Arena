#!/bin/bash
##
# Validation script for Mass Assignment challenge
# Checks if the user has successfully escalated privileges and extracted the flag
##

EXPECTED_FLAG="ARENA{m4ss_4ss1gnm3nt_pr1v_3sc}"

# Check if flag was provided
if [ -z "$1" ]; then
    echo "❌ No flag provided"
    echo "Usage: ./validate.sh <flag>"
    exit 1
fi

USER_FLAG="$1"

# Check if flag matches
if [ "$USER_FLAG" = "$EXPECTED_FLAG" ]; then
    echo "✅ Correct flag! Challenge completed!"
    exit 0
else
    echo "❌ Incorrect flag"
    echo "The flag you provided: $USER_FLAG"
    echo "Hint: You need to escalate your role to 'admin' using mass assignment, then access /api/admin/flag"
    exit 1
fi
