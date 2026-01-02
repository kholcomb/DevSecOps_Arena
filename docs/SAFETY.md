# DevSecOps Arena Safety Guards

## Overview

DevSecOps Arena includes comprehensive safety guards to protect your system from accidental damage during training exercises. These guards are enabled by default and strongly recommended for all users.

## Three-Layer Protection System

### Layer 1: Command Pattern Validation

Pre-execution validation using regex pattern matching to detect dangerous commands before they run.

**Blocked Operations (Cannot Execute):**

```bash
# Critical namespace deletion
kubectl delete namespace kube-system
kubectl delete namespace kube-public
kubectl delete namespace kube-node-lease
kubectl delete namespace default

# Node operations
kubectl delete node <node-name>
kubectl drain node <node-name>
kubectl cordon node <node-name>

# Cluster-wide deletions
kubectl delete pods --all-namespaces
kubectl delete deployments --all-namespaces

# CustomResourceDefinitions
kubectl delete crd <crd-name>

# Cluster-level RBAC
kubectl delete clusterrole <name>
kubectl delete clusterrolebinding <name>
```

**Operations Requiring Confirmation:**

```bash
# Namespace deletion (non-critical)
kubectl delete namespace arena

# Bulk deletions within allowed namespace
kubectl delete pods --all -n arena

# PersistentVolume operations
kubectl delete pv <pv-name>
```

### Layer 2: RBAC Enforcement

Role-Based Access Control limits permissions at the Kubernetes cluster level.

**Namespace-Level Permissions (Full Access):**
- Pods, Services, ConfigMaps, Secrets
- Deployments, ReplicaSets, StatefulSets, DaemonSets
- Jobs, CronJobs
- Ingresses, NetworkPolicies
- PersistentVolumeClaims

**Cluster-Level Permissions (Read-Only):**
- Nodes (view cluster info)
- Namespaces (list available namespaces)
- StorageClasses (for storage challenges)
- Metrics (for observability challenges)

**Prohibited Operations:**
- Modify resources outside designated namespace
- Create or delete namespaces without confirmation
- Modify cluster-level resources (CRDs, ClusterRoles)
- Delete or modify nodes
- Access secrets in other namespaces

### Layer 3: Namespace Isolation

All operations are scoped to isolated training namespace with system namespaces protected.

## Setup

### Automatic Setup (Recommended)

RBAC is automatically configured during installation:

```bash
./install.sh
```

### Manual Setup

```bash
# Apply RBAC configuration
./rbac/setup-rbac.sh

# Or manually
kubectl apply -f rbac/arena-rbac.yaml
```

## Using Safety Guards

Safety guards are automatically active when using the game engine:

```bash
./play.sh
```

### Testing Safety Guards

Test if a command would be blocked:

```bash
python3 engine/safety.py kubectl delete namespace kube-system
# Output: BLOCKED: Cannot delete critical system namespaces

python3 engine/safety.py kubectl get pods -n arena
# Output: Command passed safety checks
```

### View Safety Information

```bash
python3 engine/safety.py info
```

## Disabling Safety Guards

**Not recommended** - Only disable if absolutely necessary:

```bash
# Temporary (current session only)
export ARENA_SAFETY=off
./play.sh

# Re-enable
unset ARENA_SAFETY
# or
export ARENA_SAFETY=on
```

## Real-World Examples

**Scenario 1: Accidental Namespace Delete**

Developer meant to type:
```bash
kubectl delete deployment myapp -n arena
```

But accidentally typed:
```bash
kubectl delete namespace arena
```

- Without safety guards: Entire namespace gone, all work lost
- With safety guards: Prompted for confirmation, chance to cancel

**Scenario 2: Copy-Paste Disaster**

Copied from documentation for production:
```bash
kubectl delete pods --all-namespaces
```

Ran in development cluster by mistake.

- Without safety guards: All pods in all namespaces deleted
- With safety guards: Command blocked completely

**Scenario 3: Node Deletion**

Trying to delete a pod, mistyped:
```bash
kubectl delete node kind-control-plane
```

- Without safety guards: Entire cluster node removed
- With safety guards: Command blocked, cluster saved

## Safety Guard Implementation

### Command Validation

Pattern matching detects dangerous commands before execution:

```python
# Example: Detect namespace deletion
pattern = r"kubectl\s+delete\s+namespace\s+(kube-system|default)"

if matches_dangerous_pattern(command):
    block_command()
```

### RBAC Enforcement

Even if detection is bypassed, RBAC enforces limits:

```yaml
kind: Role
metadata:
  namespace: arena
# Cannot affect other namespaces
```

## Troubleshooting

### "Command blocked by safety guards"

This is working as intended. The command you tried is dangerous. Options:

1. Review what you're trying to do
2. Ensure you're using correct namespace flag
3. Check for typos
4. See "Disabling Safety Guards" if operation is truly necessary (not recommended)

### "Permission denied" errors

You may be trying to access resources outside the designated namespace:

```bash
# Won't work
kubectl get pods -n default

# Works
kubectl get pods -n arena
```

### Safety guards not working

Check if they're enabled:

```bash
echo $ARENA_SAFETY
# Should be empty or "on"

# If it says "off", re-enable
unset ARENA_SAFETY
```

## Best Practices

1. **Always use namespace flag**
   ```bash
   kubectl get pods -n arena
   kubectl apply -f myapp.yaml -n arena
   ```

2. **Test changes before applying**
   ```bash
   # Dry-run first
   kubectl apply -f deployment.yaml --dry-run=client -n arena

   # Then apply for real
   kubectl apply -f deployment.yaml -n arena
   ```

3. **Use kubectl apply instead of kubectl create**
   ```bash
   # Fails if exists
   kubectl create -f deployment.yaml

   # Creates or updates
   kubectl apply -f deployment.yaml
   ```

4. **Check what will be deleted**
   ```bash
   kubectl delete pod <name> --dry-run=client -n arena
   ```

5. **Keep safety guards enabled**
   - Only disable if you absolutely know what you're doing
   - Re-enable immediately after

## FAQ

**Q: Why can't I delete the default namespace?**

A: The default namespace is critical to Kubernetes. Deleting it would break many system components. Use the designated training namespace instead.

**Q: Can I practice RBAC challenges with safety guards?**

A: Yes. You have full RBAC control within the training namespace. You just can't modify cluster-level RBAC.

**Q: What if I'm an experienced user?**

A: Safety guards help prevent accidents. Even experts make typos. You can disable them if needed, but we recommend keeping them enabled.

**Q: Will this work on production clusters?**

A: DevSecOps Arena is designed for LOCAL clusters only. Never run on production. Safety guards are an extra layer of protection, not a replacement for proper cluster isolation.

## Summary

Safety guards provide multiple layers of protection:

1. Command validation - Blocks dangerous patterns before execution
2. RBAC enforcement - Limits permissions at cluster level
3. Namespace isolation - Restricts operations to training namespace
4. User confirmation - Prompts for risky but allowed operations

Together, these make DevSecOps Arena safe for learning while providing realistic experience.

The goal is learning, not breaking things. Safety guards enable confident experimentation.
