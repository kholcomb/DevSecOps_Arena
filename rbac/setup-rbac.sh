#!/bin/bash
set -e

echo "🛡️  Setting up DevSecOps Arena Safety Guards"
echo "======================================"
echo ""

# Check if arena namespace exists
if ! kubectl get namespace arena >/dev/null 2>&1; then
  echo "Creating arena namespace..."
  kubectl create namespace arena
fi

# Apply RBAC configuration
echo "Applying RBAC policies..."
kubectl apply -f rbac/arena-rbac.yaml

echo ""
echo "✅ RBAC Setup Complete!"
echo ""
echo "📋 What was configured:"
echo "  • ServiceAccount: arena-player"
echo "  • Role: Full access within arena namespace"
echo "  • ClusterRole: Read-only cluster-wide access"
echo ""
echo "🔒 Safety Features:"
echo "  ✓ Cannot modify resources outside arena namespace"
echo "  ✓ Cannot delete nodes or critical namespaces"
echo "  ✓ Cannot modify cluster-level resources"
echo "  ✓ Read-only access to cluster info (nodes, storage classes)"
echo ""
echo "💡 To use this ServiceAccount:"
echo "   kubectl --as=system:serviceaccount:arena:arena-player <command>"
echo ""
echo "Or configure your context to use it by default."
echo ""
