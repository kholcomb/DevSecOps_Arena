#!/bin/bash

echo "🔍 Checking pod status..."

POD_STATUS=$(kubectl get pod web-app -n arena -o jsonpath='{.status.phase}' 2>/dev/null)
READY=$(kubectl get pod web-app -n arena -o jsonpath='{.status.containerStatuses[0].ready}' 2>/dev/null)

echo "   Phase: $POD_STATUS"
echo "   Ready: $READY"

if [[ "$POD_STATUS" == "Running" ]] && [[ "$READY" == "true" ]]; then
    echo "✅ Pod is running with a valid image"
    exit 0
else
    echo "❌ Pod is not running properly"
    echo "💡 Hint: Check 'kubectl describe pod web-app -n arena' for ImagePullBackOff errors"
    exit 1
fi
