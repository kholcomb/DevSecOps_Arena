#!/bin/bash
##
# Validation script for BOLA challenge
# Checks if the user has successfully extracted the admin's flag
##

EXPECTED_FLAG="ARENA{b0l4_1d0r_g3t_4ll_d4t4}"

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
    echo "Hint: The flag is in the admin user's (user ID 2) profile data."
    exit 1
fi
