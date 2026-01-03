#!/bin/bash
# DevSecOps Arena Container Cleanup Utility
# Removes all containers created by the arena across all domains

set -e

echo "🧹 DevSecOps Arena Container Cleanup"
echo "====================================="
echo ""

# Function to cleanup containers by prefix
cleanup_by_prefix() {
    local prefix=$1
    local domain_name=$2

    containers=$(docker ps -a --filter "name=${prefix}" --format "{{.Names}}" 2>/dev/null || true)

    if [ -n "$containers" ]; then
        echo "📦 Cleaning up ${domain_name} containers..."
        echo "$containers" | while read container; do
            echo "  ➜ Removing: $container"
            docker rm -f "$container" 2>/dev/null || true
        done
        echo ""
    fi
}

# Cleanup MCP domain containers
cleanup_by_prefix "devsecops-arena-mcp" "MCP"

# Cleanup Web Security domain containers
cleanup_by_prefix "arena_web" "Web Security"

# Cleanup API Security domain containers
cleanup_by_prefix "arena_api" "API Security"

# Cleanup any orphaned networks
echo "🌐 Cleaning up orphaned networks..."
docker network rm devsecops-arena-mcp 2>/dev/null || true

# Show summary
echo ""
echo "✅ Cleanup complete!"
echo ""
echo "Remaining arena containers:"
docker ps -a --filter "name=arena" --filter "name=devsecops" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null || echo "  (none)"
echo ""
