#!/bin/bash
##
# Validation script for SQL Injection challenge
# Checks if the user has successfully extracted the admin flag
##

EXPECTED_FLAG="ARENA{SQL_1nj3ct10n_m4st3r}"

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
    echo "Hint: The admin user has a secret field containing the flag. Use SQL injection to bypass authentication."
    exit 1
fi
