#!/bin/bash
set -e

echo "🛡️  Setting up DevSecOps Arena Safety Guards"
echo "======================================"
echo ""

# Check if devsecops-arena namespace exists
if ! kubectl get namespace devsecops-arena >/dev/null 2>&1; then
  echo "Creating devsecops-arena namespace..."
  kubectl create namespace devsecops-arena
fi

# Apply RBAC configuration
echo "Applying RBAC policies..."
kubectl apply -f rbac/devsecops-arena-rbac.yaml

echo ""
echo "✅ RBAC Setup Complete!"
echo ""
echo "📋 What was configured:"
echo "  • ServiceAccount: devsecops-arena-player"
echo "  • Role: Full access within devsecops-arena namespace"
echo "  • ClusterRole: Read-only cluster-wide access"
echo ""
echo "🔒 Safety Features:"
echo "  ✓ Cannot modify resources outside devsecops-arena namespace"
echo "  ✓ Cannot delete nodes or critical namespaces"
echo "  ✓ Cannot modify cluster-level resources"
echo "  ✓ Read-only access to cluster info (nodes, storage classes)"
echo ""
echo "💡 To use this ServiceAccount:"
echo "   kubectl --as=system:serviceaccount:devsecops-arena:devsecops-arena-player <command>"
echo ""
echo "Or configure your context to use it by default."
echo ""
