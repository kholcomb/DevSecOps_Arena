#!/bin/bash
set -e

echo "🎮 DevSecOps Arena Installation"
echo "========================"
echo ""

# Check prerequisites
command -v kind >/dev/null || { echo "❌ kind not found. Install with: brew install kind"; exit 1; }
command -v kubectl >/dev/null || { echo "❌ kubectl not found. Install with: brew install kubectl"; exit 1; }
command -v python3 >/dev/null || { echo "❌ python3 not found"; exit 1; }

echo "✅ Prerequisites OK"
echo ""

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
  echo "🐍 Creating Python virtual environment..."
  python3 -m venv venv
fi

# Activate virtual environment and install dependencies
echo "📦 Installing Python dependencies..."
source venv/bin/activate
pip install -q -r requirements.txt

echo "✅ Python packages installed"
echo ""

# Create Kubernetes cluster
if ! kind get clusters | grep arena >/dev/null 2>&1; then
  echo "🔧 Creating Kubernetes cluster..."
  kind create cluster --name arena
else
  echo "✅ Cluster already exists"
fi

kubectl config use-context kind-arena

# Create arena namespace
echo "🏗️  Setting up arena namespace..."
kubectl create namespace arena --dry-run=client -o yaml | kubectl apply -f -

# Setup RBAC for safety
echo "🛡️  Configuring safety guards (RBAC)..."
if [ -f "rbac/arena-rbac.yaml" ]; then
  kubectl apply -f rbac/arena-rbac.yaml
  echo "✅ Safety guards configured"
else
  echo "⚠️  Warning: RBAC config not found, skipping"
fi

echo ""
echo "🚀 Setup Complete!"
echo ""
echo "To start playing:"
echo "  source venv/bin/activate"
echo "  python3 engine/engine.py"
echo ""
echo "Or use the shortcut:"
echo "  ./play.sh"
echo ""
