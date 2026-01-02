#!/bin/bash

# Level 25 Validation: NetworkPolicy Too Restrictive
# Validates that the NetworkPolicy allows frontend to access backend

set -e

NAMESPACE="k8squest"
FRONTEND_POD="frontend"
BACKEND_POD="backend"
NETWORK_POLICY="backend-network-policy"

echo "🔍 Level 25: NetworkPolicy Too Restrictive - Validation"
echo "========================================================="
echo ""

# Stage 1: Check if all pods exist
echo "Stage 1: Checking pod existence..."
if ! kubectl get pod $FRONTEND_POD -n $NAMESPACE &>/dev/null; then
    echo "❌ VALIDATION FAILED!"
    echo ""
    echo "📋 Issue: Frontend pod '$FRONTEND_POD' not found in namespace '$NAMESPACE'"
    echo ""
    echo "💡 Hint: Apply the YAML configuration with: kubectl apply -f solution.yaml"
    exit 1
fi

if ! kubectl get pod $BACKEND_POD -n $NAMESPACE &>/dev/null; then
    echo "❌ VALIDATION FAILED!"
    echo ""
    echo "📋 Issue: Backend pod '$BACKEND_POD' not found in namespace '$NAMESPACE'"
    echo ""
    echo "💡 Hint: Apply the YAML configuration with: kubectl apply -f solution.yaml"
    exit 1
fi
echo "✅ Both frontend and backend pods exist"
echo ""

# Stage 2: Check if pods are running
echo "Stage 2: Checking pod status..."
FRONTEND_STATUS=$(kubectl get pod $FRONTEND_POD -n $NAMESPACE -o jsonpath='{.status.phase}')
BACKEND_STATUS=$(kubectl get pod $BACKEND_POD -n $NAMESPACE -o jsonpath='{.status.phase}')

if [ "$FRONTEND_STATUS" != "Running" ]; then
    echo "❌ VALIDATION FAILED!"
    echo ""
    echo "📋 Issue: Frontend pod is in '$FRONTEND_STATUS' state, not 'Running'"
    echo ""
    echo "💡 Hint: Wait for the pod to start or check: kubectl describe pod $FRONTEND_POD -n $NAMESPACE"
    exit 1
fi

if [ "$BACKEND_STATUS" != "Running" ]; then
    echo "❌ VALIDATION FAILED!"
    echo ""
    echo "📋 Issue: Backend pod is in '$BACKEND_STATUS' state, not 'Running'"
    echo ""
    echo "💡 Hint: Wait for the pod to start or check: kubectl describe pod $BACKEND_POD -n $NAMESPACE"
    exit 1
fi
echo "✅ Both pods are running"
echo ""

# Stage 3: Check if NetworkPolicy exists
echo "Stage 3: Checking NetworkPolicy..."
if ! kubectl get networkpolicy $NETWORK_POLICY -n $NAMESPACE &>/dev/null; then
    echo "❌ VALIDATION FAILED!"
    echo ""
    echo "📋 Issue: NetworkPolicy '$NETWORK_POLICY' not found in namespace '$NAMESPACE'"
    echo ""
    echo "💡 Hint: The NetworkPolicy should be defined in your YAML"
    exit 1
fi
echo "✅ NetworkPolicy '$NETWORK_POLICY' exists"
echo ""

# Stage 4: Check NetworkPolicy configuration
echo "Stage 4: Checking NetworkPolicy configuration..."
POLICY_SELECTOR=$(kubectl get networkpolicy $NETWORK_POLICY -n $NAMESPACE -o jsonpath='{.spec.ingress[0].from[0].podSelector.matchLabels.app}')

if [ "$POLICY_SELECTOR" != "frontend" ]; then
    echo "❌ VALIDATION FAILED!"
    echo ""
    echo "📋 Issue: NetworkPolicy allows traffic from 'app=$POLICY_SELECTOR' but should allow 'app=frontend'"
    echo ""
    echo "🔍 Current Configuration:"
    echo "   NetworkPolicy allows: app=$POLICY_SELECTOR"
    echo "   Frontend pod has label: app=frontend"
    echo ""
    echo "💡 Hint: The NetworkPolicy podSelector should match the frontend pod's labels"
    echo "💡 Hint: Check the 'ingress.from.podSelector.matchLabels' in the NetworkPolicy"
    echo ""
    echo "🎯 What to fix:"
    echo "   Change the NetworkPolicy to allow traffic from pods with label 'app: frontend'"
    exit 1
fi
echo "✅ NetworkPolicy allows traffic from 'app=frontend' pods"
echo ""

# Stage 5: Wait for frontend to start making requests
echo "Stage 5: Waiting for frontend to initialize (15 seconds)..."
sleep 15
echo "✅ Frontend should have attempted connections"
echo ""

# Stage 6: Check frontend logs for successful connection
echo "Stage 6: Checking frontend connectivity..."
LOGS=$(kubectl logs $FRONTEND_POD -n $NAMESPACE --tail=20 2>&1)

if echo "$LOGS" | grep -q "API Response: Success"; then
    echo "✅ Frontend successfully connected to backend!"
elif echo "$LOGS" | grep -iq "timeout\|connection refused\|network is unreachable"; then
    echo "❌ VALIDATION FAILED!"
    echo ""
    echo "📋 Issue: Frontend cannot connect to backend (network policy blocking)"
    echo ""
    echo "🔍 Frontend logs show connection errors:"
    echo "$LOGS" | tail -5
    echo ""
    echo "💡 Hint: The NetworkPolicy is still blocking the frontend's traffic"
    echo "💡 Hint: Verify the podSelector matchLabels allow 'app: frontend'"
    echo ""
    echo "🎯 Debug commands:"
    echo "   kubectl logs $FRONTEND_POD -n $NAMESPACE"
    echo "   kubectl describe networkpolicy $NETWORK_POLICY -n $NAMESPACE"
    echo "   kubectl get pod $FRONTEND_POD -n $NAMESPACE --show-labels"
    exit 1
else
    echo "⚠️  WARNING: No clear success or failure in logs yet"
    echo "   Logs so far:"
    echo "$LOGS" | tail -5
    echo ""
    echo "💡 Hint: Wait a bit longer and check logs manually:"
    echo "   kubectl logs $FRONTEND_POD -n $NAMESPACE -f"
    exit 1
fi
echo ""

# Stage 7: Verify backend received requests
echo "Stage 7: Verifying backend received requests..."
BACKEND_LOGS=$(kubectl logs $BACKEND_POD -n $NAMESPACE 2>&1)

# The http-echo image doesn't log requests, so we just verify it's running
if [ -z "$BACKEND_LOGS" ] || echo "$BACKEND_LOGS" | grep -q "listening"; then
    echo "✅ Backend is serving requests"
else
    echo "⚠️  Backend status unknown (http-echo doesn't log requests)"
fi
echo ""

# Final Success
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                  ✅ VALIDATION PASSED! ✅                     ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "🎉 Excellent work! Your NetworkPolicy is correctly configured!"
echo ""
echo "📊 What you fixed:"
echo "   • NetworkPolicy now allows traffic from frontend pods (app=frontend)"
echo "   • Frontend successfully connects to backend service"
echo "   • Network security maintained (only frontend can access backend)"
echo ""
echo "🎓 Key Concept Mastered:"
echo "   NetworkPolicies use label selectors to control pod-to-pod traffic."
echo "   The 'podSelector' in 'ingress.from' must match the SOURCE pod's labels!"
echo ""
echo "🚀 In production:"
echo "   • Start with permissive policies, then gradually tighten"
echo "   • Test connectivity after applying NetworkPolicies"
echo "   • Use namespace selectors for cross-namespace traffic"
echo "   • Document which pods need to communicate"
echo "   • Monitor denied connections in NetworkPolicy logs"
echo ""

exit 0
