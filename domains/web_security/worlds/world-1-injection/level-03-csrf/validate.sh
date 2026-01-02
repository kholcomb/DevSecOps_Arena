#!/bin/bash
##
# Validation script for CSRF challenge
# Checks if the user has successfully executed a CSRF attack
##

EXPECTED_FLAG="ARENA{CSRF_f0rc3d_tr4nsf3r}"

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
    echo "Hint: Complete the CSRF attack to see the flag on the banking app."
    exit 1
fi
