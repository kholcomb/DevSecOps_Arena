#!/bin/bash
##
# Validation script for Reflected XSS challenge
# Checks if the user has successfully extracted the flag
##

EXPECTED_FLAG="ARENA{xss_c00k13_th3ft_FTW}"

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
    echo "Hint: The flag is stored in a cookie. Use XSS to extract it."
    exit 1
fi
