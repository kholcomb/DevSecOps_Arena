# Kubernetes Security & Operations Domain

**Status:** ✅ Phase 2 Complete

The original 50 Kubernetes challenges wrapped as a domain plugin, preserving full functionality while demonstrating the domain plugin architecture.

## Domain Overview

```
domains/kubernetes/
├── __init__.py              - Package exports
├── domain_config.yaml       - Domain configuration
├── domain.py                - KubernetesDomain class (109 LOC)
├── deployer.py              - KubectlDeployer implementation (365 LOC)
├── safety_guard.py          - K8sSafetyGuard implementation (299 LOC)
├── visualizer.py            - K8sVisualizer implementation (459 LOC)
└── worlds/                  - 50 challenges across 5 worlds
    ├── world-1-basics/      - 10 challenges (1,500 XP)
    ├── world-2-deployments/ - 10 challenges (2,050 XP)
    ├── world-3-networking/  - 10 challenges (2,300 XP)
    ├── world-4-storage/     - 10 challenges (2,450 XP)
    └── world-5-security/    - 10 challenges (3,300 XP)

Total: 1,232 lines of domain code + 50 challenges
```

## Configuration

**domain_config.yaml:**
- Domain ID: `kubernetes`
- Icon: ⎈
- Deployment backend: `kubectl`
- Namespace: `k8squest`
- Safety guards: Enabled
- Total XP: 11,600 across 50 challenges

## Components

### KubernetesDomain
Main domain class that instantiates all components.

**Methods:**
- `create_deployer()` → Returns KubectlDeployer
- `create_validator()` → Returns BashScriptValidator
- `create_safety_guard()` → Returns K8sSafetyGuard
- `create_visualizer()` → Returns K8sVisualizer

### KubectlDeployer
Handles kubectl-based challenge deployment.

**Features:**
- Namespace management (create/delete k8squest)
- Deploys broken.yaml manifests
- Resource status checking (pods, deployments, services)
- Health checks for kubectl and cluster connectivity

**Methods:**
- `health_check()` - Verify kubectl and cluster
- `deploy_challenge()` - Deploy broken.yaml
- `cleanup_challenge()` - Delete namespace
- `get_status()` - Query resource status

### K8sSafetyGuard
Protects against dangerous kubectl operations.

**8 Safety Patterns:**
1. ⛔ CRITICAL: Delete system namespaces
2. ⚠️  WARNING: Delete k8squest namespace
3. ⛔ CRITICAL: Delete nodes
4. ⚠️  WARNING: Delete all resources (--all)
5. ⛔ CRITICAL: Cluster-wide deletions (--all-namespaces)
6. ⛔ CRITICAL: Delete CRDs
7. ⛔ CRITICAL: Delete cluster RBAC
8. ⚠️  WARNING: Delete PersistentVolumes

**Methods:**
- `get_dangerous_patterns()` - Returns list of patterns
- `validate_command(cmd, interactive)` - Check command safety
- `get_safety_info()` - Return safety documentation

### K8sVisualizer
Provides real-time cluster state visualization.

**Queries:**
- Pods (status, readiness, restarts, issues)
- Services (endpoints, selectors)
- Deployments (replica status)
- ConfigMaps, Secrets
- NetworkPolicies
- PVCs, StatefulSets

**Methods:**
- `get_visualization_data()` - Full cluster state
- `detect_issues()` - Find pod/container problems
- `get_resource_graph()` - Generate relationship graph

## Challenge Structure

All 50 challenges follow the standard 8-file pattern:

```
level-N-name/
├── mission.yaml         - Challenge metadata
├── broken.yaml          - Broken K8s manifest
├── solution.yaml        - Fixed version
├── validate.sh          - Validation script
├── hint-1.txt           - First hint
├── hint-2.txt           - Second hint
├── hint-3.txt           - Third hint
└── debrief.md           - Learning content
```

## Worlds

### World 1: Kubernetes Basics (1,500 XP)
Pods, deployments, and core concepts
- Pod crashes and repairs
- Deployment scaling
- Image pull issues
- Label selectors

### World 2: Advanced Deployments (2,050 XP)
Rollouts, scaling, health checks
- Rolling updates and rollbacks
- Liveness and readiness probes
- Horizontal pod autoscaling
- Pod disruption budgets
- Blue/green and canary deployments

### World 3: Networking & Services (2,300 XP)
Services, ingress, network policies
- Service selectors
- NodePort configuration
- DNS resolution
- Ingress rules
- Network policies

### World 4: Storage & Persistence (2,450 XP)
Volumes, PVCs, StatefulSets
- PVC binding issues
- Volume mount paths
- Access modes
- StorageClasses
- StatefulSet ordering

### World 5: Security & RBAC (3,300 XP)
RBAC, security contexts, policies
- Role and RoleBinding
- SecurityContext
- ResourceQuotas
- PodSecurityPolicies
- Secrets management

## Verification Tests

All tests passing:

✅ **Import Tests**
- All components import successfully
- No missing dependencies

✅ **Domain Loading**
- domain_config.yaml loads correctly
- Configuration parsed properly
- All 5 worlds discovered

✅ **Component Creation**
- Deployer instantiates correctly
- Safety guard patterns loaded
- Visualizer initialized

✅ **Challenge Discovery**
- All 50 challenges found
- mission.yaml files parsed
- XP and difficulty loaded correctly

✅ **Safety Guard**
- Critical commands blocked
- Warnings trigger confirmation
- Safe commands allowed

## Backward Compatibility

A symlink preserves compatibility:
```bash
worlds -> domains/kubernetes/worlds
```

This allows existing code to reference `worlds/` and still work.

## Git History Preserved

Used `git mv` to move worlds directory, preserving full commit history:
```bash
git mv worlds domains/kubernetes/worlds
```

## Next Steps: Phase 3

**Engine Refactoring:**
- Add domain discovery to engine.py
- Replace kubectl calls with domain.deployer
- Implement domain-aware progress tracking
- Add domain selection menu
- Test backward compatibility

## Usage Example

```python
from pathlib import Path
from domains.kubernetes import load_domain

# Load the kubernetes domain
domain = load_domain(Path("domains/kubernetes"))

# Check health
is_healthy, msg = domain.health_check()

# Discover challenges in a world
challenges = domain.discover_challenges("world-1-basics")

# Deploy a challenge
level_path = Path("domains/kubernetes/worlds/world-1-basics/level-1-pods")
success, msg = domain.deployer.deploy_challenge(level_path)

# Get cluster state for visualization
viz_data = domain.visualizer.get_visualization_data(level_path)

# Validate a kubectl command
allowed, msg, severity = domain.safety_guard.validate_command(
    "kubectl delete pod test -n k8squest",
    interactive=True
)

# Cleanup
domain.deployer.cleanup_challenge(level_path)
```

## Summary

Phase 2 successfully wrapped all 50 existing Kubernetes challenges as the first domain plugin, demonstrating:

1. ✅ Domain plugin architecture works
2. ✅ All challenges preserved and discoverable
3. ✅ Safety guards functional
4. ✅ Backward compatibility maintained
5. ✅ Clean abstraction boundaries
6. ✅ Ready for engine integration (Phase 3)
