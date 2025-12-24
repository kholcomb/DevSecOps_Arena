#!/bin/bash

# Check if client pod can resolve service DNS
LOGS=$(kubectl logs app-client -n k8squest --tail=5 2>/dev/null)

if echo "$LOGS" | grep -q "Connection successful"; then
  echo "✅ Level complete! DNS resolution working"
  exit 0
else
  echo "❌ DNS resolution failing. Check the service name in client pod"
  echo "Hint: Service is named 'database-service', not 'database'"
  exit 1
fi
