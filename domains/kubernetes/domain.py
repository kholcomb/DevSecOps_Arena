#!/usr/bin/env python3
"""
Kubernetes Security & Operations Domain

The original 50 K8s challenges wrapped as a domain plugin.
This domain teaches Kubernetes operations and security through hands-on challenges.
"""

from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from domains._base import Domain

# Import kubernetes-specific components
from domains.kubernetes.deployer import KubectlDeployer
from domains.kubernetes.safety_guard import K8sSafetyGuard
from domains.kubernetes.visualizer import K8sVisualizer
from domains._base.validator import BashScriptValidator


class KubernetesDomain(Domain):
    """
    Kubernetes Security & Operations Domain.

    This domain contains 50 challenges across 5 worlds covering:
    - World 1: Kubernetes Basics (pods, deployments)
    - World 2: Advanced Deployments (rollouts, scaling, health checks)
    - World 3: Networking & Services (services, ingress, network policies)
    - World 4: Storage & Persistence (volumes, PVCs, StatefulSets)
    - World 5: Security & RBAC (RBAC, security contexts, policies)

    Total: 10,200 XP across 50 challenges
    """

    def create_deployer(self):
        """
        Create kubectl-based deployer.

        Returns:
            KubectlDeployer that handles K8s manifest deployment
        """
        return KubectlDeployer(self.config.__dict__)

    def create_validator(self):
        """
        Create bash script validator.

        Kubernetes challenges use standard validate.sh scripts.

        Returns:
            BashScriptValidator instance
        """
        return BashScriptValidator(self.config.__dict__)

    def create_safety_guard(self):
        """
        Create Kubernetes safety guard.

        Protects against:
        - Deleting system namespaces (kube-system, kube-public, etc.)
        - Deleting nodes
        - Cluster-wide deletions
        - Deleting CRDs and cluster-level RBAC

        Returns:
            K8sSafetyGuard instance
        """
        return K8sSafetyGuard(self.config.__dict__)

    def create_visualizer(self):
        """
        Create Kubernetes cluster visualizer.

        Provides real-time visualization of:
        - Pod status and issues
        - Service endpoints
        - Deployment replica status
        - Network policies
        - Resource relationships

        Returns:
            K8sVisualizer instance
        """
        return K8sVisualizer(self.config.__dict__)


def load_domain(domain_path: Path) -> KubernetesDomain:
    """
    Factory function to load the Kubernetes domain.

    Args:
        domain_path: Path to domains/kubernetes/ directory

    Returns:
        KubernetesDomain instance

    Example:
        >>> domain = load_domain(Path("domains/kubernetes"))
        >>> domain.config.id
        'kubernetes'
    """
    return KubernetesDomain(domain_path)
