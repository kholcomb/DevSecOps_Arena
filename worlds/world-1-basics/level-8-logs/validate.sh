#!/bin/bash

echo "🔍 Checking pod status and stability..."

POD_STATUS=$(kubectl get pod database-app -n k8squest -o jsonpath='{.status.phase}' 2>/dev/null)
READY=$(kubectl get pod database-app -n k8squest -o jsonpath='{.status.containerStatuses[0].ready}' 2>/dev/null)
RESTART_COUNT=$(kubectl get pod database-app -n k8squest -o jsonpath='{.status.containerStatuses[0].restartCount}' 2>/dev/null)

echo "   Pod Phase: $POD_STATUS"
echo "   Ready: $READY"
echo "   Restarts: $RESTART_COUNT"

if [[ "$POD_STATUS" == "Running" ]] && [[ "$READY" == "true" ]] && [[ "$RESTART_COUNT" -eq 0 ]]; then
    echo "✅ Pod is running without restarts"
    exit 0
else
    echo "❌ Pod is not stable - Status: $POD_STATUS, Restarts: $RESTART_COUNT"
    echo "💡 Hint: Check logs with 'kubectl logs database-app -n k8squest'"
    echo "💡 Look for error messages about missing configuration"
    exit 1
fi
