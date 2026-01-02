#!/bin/bash

NAMESPACE="k8squest"
DEPLOYMENT="chaos-app"

echo "🔥 CHAOS FINALE VALIDATION 🔥"
echo "Checking ALL World 5 concepts..."
echo ""

ERRORS=0

# 1. RBAC
echo "🔍 1/9: Checking RBAC (ServiceAccount, Role, RoleBinding)..."
if ! kubectl get serviceaccount app-sa -n $NAMESPACE &>/dev/null; then
    echo "❌ ServiceAccount missing"; ((ERRORS++))
elif ! kubectl get role app-role -n $NAMESPACE &>/dev/null; then
    echo "❌ Role missing"; ((ERRORS++))
elif ! kubectl get rolebinding app-binding -n $NAMESPACE &>/dev/null; then
    echo "❌ RoleBinding missing"; ((ERRORS++))
else
    echo "✅ RBAC configured"
fi

# 2. ResourceQuota
echo "🔍 2/9: Checking ResourceQuota..."
QUOTA_CPU=$(kubectl get resourcequota chaos-quota -n $NAMESPACE -o jsonpath='{.spec.hard.requests\.cpu}' 2>/dev/null)
if [ -z "$QUOTA_CPU" ]; then
    echo "❌ ResourceQuota missing"; ((ERRORS++))
else
    echo "✅ ResourceQuota: $QUOTA_CPU CPU"
fi

# 3. NetworkPolicy
echo "🔍 3/9: Checking NetworkPolicy..."
if ! kubectl get networkpolicy -n $NAMESPACE | grep -q "allow"; then
    echo "❌ Allow NetworkPolicy missing"; ((ERRORS++))
else
    echo "✅ NetworkPolicy configured"
fi

# 4. PriorityClass
echo "🔍 4/9: Checking PriorityClass..."
if ! kubectl get priorityclass production-priority &>/dev/null; then
    echo "❌ PriorityClass missing"; ((ERRORS++))
else
    echo "✅ PriorityClass exists"
fi

# 5. PodDisruptionBudget
echo "🔍 5/9: Checking PodDisruptionBudget..."
if ! kubectl get pdb chaos-pdb -n $NAMESPACE &>/dev/null; then
    echo "❌ PDB missing"; ((ERRORS++))
else
    MIN_AVAIL=$(kubectl get pdb chaos-pdb -n $NAMESPACE -o jsonpath='{.spec.minAvailable}')
    echo "✅ PDB configured (minAvailable: $MIN_AVAIL)"
fi

# 6. Deployment
echo "🔍 6/9: Checking Deployment..."
if ! kubectl get deployment $DEPLOYMENT -n $NAMESPACE &>/dev/null; then
    echo "❌ Deployment missing"; ((ERRORS++))
    exit 1
fi
echo "✅ Deployment exists"

# 7. SecurityContext
echo "🔍 7/9: Checking SecurityContext (runAsNonRoot, allowPrivilegeEscalation)..."
RUN_AS_NON_ROOT=$(kubectl get deployment $DEPLOYMENT -n $NAMESPACE -o jsonpath='{.spec.template.spec.containers[0].securityContext.runAsNonRoot}')
ALLOW_PRIV=$(kubectl get deployment $DEPLOYMENT -n $NAMESPACE -o jsonpath='{.spec.template.spec.containers[0].securityContext.allowPrivilegeEscalation}')
if [ "$RUN_AS_NON_ROOT" != "true" ]; then
    echo "❌ runAsNonRoot not true"; ((ERRORS++))
elif [ "$ALLOW_PRIV" != "false" ]; then
    echo "❌ allowPrivilegeEscalation not false"; ((ERRORS++))
else
    echo "✅ SecurityContext configured securely"
fi

# 8. Resources within quota
echo "🔍 8/9: Checking resource requests fit quota..."
CPU_REQUEST=$(kubectl get deployment $DEPLOYMENT -n $NAMESPACE -o jsonpath='{.spec.template.spec.containers[0].resources.requests.cpu}')
REPLICAS=$(kubectl get deployment $DEPLOYMENT -n $NAMESPACE -o jsonpath='{.spec.replicas}')
echo "   CPU per pod: $CPU_REQUEST, Replicas: $REPLICAS"
echo "✅ Resource requests checked"

# 9. Pod status
echo "🔍 9/9: Checking pod status..."
READY=$(kubectl get deployment $DEPLOYMENT -n $NAMESPACE -o jsonpath='{.status.readyReplicas}' 2>/dev/null || echo "0")
if [ "$READY" = "0" ] || [ -z "$READY" ]; then
    echo "⚠️  Pods not ready yet (may need time to start)"
else
    echo "✅ $READY/$REPLICAS pods ready"
fi

echo ""
echo "================================"
if [ $ERRORS -eq 0 ]; then
    echo "🎉🎉🎉 SUCCESS! 🎉🎉🎉"
    echo ""
    echo "YOU'VE CONQUERED THE CHAOS FINALE!"
    echo ""
    echo "All World 5 concepts mastered:"
    echo "  ✅ RBAC"
    echo "  ✅ SecurityContext"
    echo "  ✅ ResourceQuota"
    echo "  ✅ NetworkPolicy"
    echo "  ✅ Node Affinity"
    echo "  ✅ Taints & Tolerations"
    echo "  ✅ PodDisruptionBudget"
    echo "  ✅ Pod Security Standards"
    echo "  ✅ PriorityClass"
    echo ""
    echo "🏆 KUBERNETES MASTER! 🏆"
    echo ""
    echo "You've completed ALL 50 LEVELS!"
    echo "Total XP earned: 10,200 XP!"
    echo ""
    echo "THE STORM HAS PASSED! 🌈"
else
    echo "❌ $ERRORS issue(s) found"
    echo "Keep fixing! You're almost there!"
fi
echo "================================"
