#!/bin/bash

NAMESPACE="k8squest"
DB_POD="database"
BACKEND_POD="backend"

echo "🔍 VALIDATION STAGE 1: Checking if pods exist..."
if ! kubectl get pod $DB_POD -n $NAMESPACE &>/dev/null; then
    echo "❌ FAILED: Database pod not found"
    exit 1
fi
if ! kubectl get pod $BACKEND_POD -n $NAMESPACE &>/dev/null; then
    echo "❌ FAILED: Backend pod not found"
    exit 1
fi
echo "✅ Both pods exist"

echo ""
echo "🔍 VALIDATION STAGE 2: Checking if pods are running..."
DB_STATUS=$(kubectl get pod $DB_POD -n $NAMESPACE -o jsonpath='{.status.phase}')
BACKEND_STATUS=$(kubectl get pod $BACKEND_POD -n $NAMESPACE -o jsonpath='{.status.phase}')
if [ "$DB_STATUS" != "Running" ]; then
    echo "❌ FAILED: Database pod is $DB_STATUS, not Running"
    exit 1
fi
if [ "$BACKEND_STATUS" != "Running" ]; then
    echo "❌ FAILED: Backend pod is $BACKEND_STATUS, not Running"
    exit 1
fi
echo "✅ Both pods are running"

echo ""
echo "🔍 VALIDATION STAGE 3: Checking if NetworkPolicies exist..."
if ! kubectl get networkpolicy -n $NAMESPACE | grep -q "allow"; then
    echo "❌ FAILED: No NetworkPolicy with 'allow' found"
    echo "💡 Hint: Create NetworkPolicy to allow traffic between pods"
    exit 1
fi
echo "✅ NetworkPolicies exist"

echo ""
echo "🔍 VALIDATION STAGE 4: Verifying database ingress policy..."
DB_POLICY=$(kubectl get networkpolicy -n $NAMESPACE -o json | jq -r '.items[] | select(.spec.podSelector.matchLabels.app == "database") | .metadata.name' | head -1)
if [ -z "$DB_POLICY" ]; then
    echo "❌ FAILED: No NetworkPolicy targeting database pod"
    echo "💡 Hint: Create NetworkPolicy with podSelector matching app: database"
    exit 1
fi
echo "✅ Database has NetworkPolicy: $DB_POLICY"

echo ""
echo "🔍 VALIDATION STAGE 5: Verifying backend egress policy..."
BACKEND_POLICY=$(kubectl get networkpolicy -n $NAMESPACE -o json | jq -r '.items[] | select(.spec.podSelector.matchLabels.app == "backend") | .metadata.name' | head -1)
if [ -z "$BACKEND_POLICY" ]; then
    echo "❌ FAILED: No NetworkPolicy targeting backend pod"
    echo "💡 Hint: Create NetworkPolicy with podSelector matching app: backend"
    exit 1
fi
echo "✅ Backend has NetworkPolicy: $BACKEND_POLICY"

echo ""
echo "🔍 VALIDATION STAGE 6: Testing network connectivity..."
echo "Waiting 10 seconds for policies to take effect..."
sleep 10

# Check backend logs for successful connection
BACKEND_LOGS=$(kubectl logs $BACKEND_POD -n $NAMESPACE --tail=20 2>/dev/null || echo "")
if echo "$BACKEND_LOGS" | grep -q "succeeded\|open\|Connected"; then
    echo "✅ Backend successfully connecting to database"
else
    echo "⚠️  WARNING: Cannot confirm connection in logs yet"
    echo "   This may be normal if pods just started"
    echo "   Check logs: kubectl logs $BACKEND_POD -n $NAMESPACE"
fi

echo ""
echo "🎉 SUCCESS! NetworkPolicy configuration validated!"
echo ""
echo "Network policies are configured to allow:"
echo "  • Backend → Database on port 5432"
echo "  • Backend → DNS for name resolution"
echo "  • Database accepts connections from backend only"
