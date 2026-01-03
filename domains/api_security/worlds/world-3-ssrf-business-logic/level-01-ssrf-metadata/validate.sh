#!/bin/bash
EXPECTED_FLAG="ARENA{ssrf_m3t4d4t4_s3rv1c3}"
if [ "$1" = "$EXPECTED_FLAG" ]; then echo "✅ Correct!"; exit 0; else echo "❌ Incorrect"; exit 1; fi
