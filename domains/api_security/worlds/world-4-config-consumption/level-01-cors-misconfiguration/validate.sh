#!/bin/bash
EXPECTED_FLAG="ARENA{c0rs_m1sc0nf1g_l34k}"
if [ "$1" = "$EXPECTED_FLAG" ]; then echo "✅ Correct!"; exit 0; else echo "❌ Incorrect"; exit 1; fi
