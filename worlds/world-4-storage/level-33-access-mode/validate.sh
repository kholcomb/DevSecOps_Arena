#!/bin/bash

NAMESPACE="k8squest"
DEPLOYMENT="web-servers"
PVC_NAME="shared-pvc"
PV_NAME="shared-storage"

echo "🔍 Stage 1: Checking if PV exists..."
if ! kubectl get pv "$PV_NAME" &>/dev/null; then
    echo "❌ PersistentVolume '$PV_NAME' not found"
    exit 1
fi
echo "✅ PV exists"

echo ""
echo "🔍 Stage 2: Checking if PVC is bound..."
PVC_STATUS=$(kubectl get pvc "$PVC_NAME" -n "$NAMESPACE" -o jsonpath='{.status.phase}' 2>/dev/null)
if [ "$PVC_STATUS" != "Bound" ]; then
    echo "❌ PVC is not Bound (current: $PVC_STATUS)"
    exit 1
fi
echo "✅ PVC is Bound"

echo ""
echo "🔍 Stage 3: Checking PV access mode..."
PV_ACCESS_MODE=$(kubectl get pv "$PV_NAME" -o jsonpath='{.spec.accessModes[0]}')
if [ "$PV_ACCESS_MODE" != "ReadWriteMany" ]; then
    echo "❌ PV access mode is $PV_ACCESS_MODE (should be ReadWriteMany for multiple pods)"
    echo "💡 Hint: Change accessModes to allow multiple pods to mount the volume"
    exit 1
fi
echo "✅ PV has ReadWriteMany access mode"

echo ""
echo "🔍 Stage 4: Checking PVC access mode..."
PVC_ACCESS_MODE=$(kubectl get pvc "$PVC_NAME" -n "$NAMESPACE" -o jsonpath='{.spec.accessModes[0]}')
if [ "$PVC_ACCESS_MODE" != "ReadWriteMany" ]; then
    echo "❌ PVC access mode is $PVC_ACCESS_MODE (should be ReadWriteMany)"
    exit 1
fi
echo "✅ PVC has ReadWriteMany access mode"

echo ""
echo "🔍 Stage 5: Checking if deployment exists..."
if ! kubectl get deployment "$DEPLOYMENT" -n "$NAMESPACE" &>/dev/null; then
    echo "❌ Deployment '$DEPLOYMENT' not found"
    exit 1
fi
echo "✅ Deployment exists"

echo ""
echo "🔍 Stage 6: Checking if all 3 pods are ready..."
READY_PODS=$(kubectl get deployment "$DEPLOYMENT" -n "$NAMESPACE" -o jsonpath='{.status.readyReplicas}' 2>/dev/null)
if [ "$READY_PODS" != "3" ]; then
    echo "❌ Only $READY_PODS out of 3 pods are ready"
    echo "💡 Check: kubectl get pods -n $NAMESPACE -l app=web"
    echo "💡 Describe stuck pods to see volume mount issues"
    exit 1
fi
echo "✅ All 3 pods are ready and running"

echo ""
echo "🔍 Stage 7: Verifying all pods can mount the volume..."
POD_COUNT=$(kubectl get pods -n "$NAMESPACE" -l app=web -o json | jq '[.items[] | select(.status.phase=="Running")] | length')
if [ "$POD_COUNT" != "3" ]; then
    echo "❌ Only $POD_COUNT pods are running (expected 3)"
    exit 1
fi
echo "✅ All 3 pods successfully mounted the shared volume"

echo ""
echo "🎉 SUCCESS! All pods can access the shared storage with ReadWriteMany!"
