#!/usr/bin/env python3
"""
Kubectl Challenge Deployer

Handles deployment of Kubernetes challenges using kubectl.
Extracted from the original engine.py implementation.
"""

from pathlib import Path
from typing import Dict, Any
import subprocess
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from domains._base import ChallengeDeployer


class KubectlDeployer(ChallengeDeployer):
    """
    Deployer for Kubernetes challenges using kubectl.

    Manages:
    - Namespace creation/deletion (k8squest)
    - Deployment of broken.yaml manifests
    - Resource status checking
    - Challenge cleanup
    """

    def __init__(self, domain_config: Dict[str, Any]):
        """
        Initialize kubectl deployer.

        Args:
            domain_config: Configuration from domain_config.yaml
        """
        super().__init__(domain_config)
        self.namespace = domain_config.get('namespace', 'k8squest')

    def health_check(self) -> tuple[bool, str]:
        """
        Check if kubectl is installed and cluster is accessible.

        Returns:
            tuple[bool, str]: (is_healthy, status_message)
        """
        try:
            # Check if kubectl is installed
            result = subprocess.run(
                ["kubectl", "version", "--client", "--short"],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode != 0:
                return False, "kubectl is not installed or not in PATH"

            # Check cluster connectivity
            result = subprocess.run(
                ["kubectl", "cluster-info"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                return False, "Cannot connect to Kubernetes cluster. Is Docker Desktop or kind running?"

            return True, "kubectl is installed and cluster is accessible"

        except subprocess.TimeoutExpired:
            return False, "Timeout checking kubectl/cluster"
        except FileNotFoundError:
            return False, "kubectl command not found"
        except Exception as e:
            return False, f"Health check error: {str(e)}"

    def deploy_challenge(self, level_path: Path) -> tuple[bool, str]:
        """
        Deploy a Kubernetes challenge.

        Steps:
        1. Delete and recreate k8squest namespace
        2. Apply broken.yaml manifest
        3. Wait briefly for resources to be created

        Args:
            level_path: Path to level directory containing broken.yaml

        Returns:
            tuple[bool, str]: (success, message)
        """
        broken_yaml = level_path / "broken.yaml"

        if not broken_yaml.exists():
            return False, f"broken.yaml not found in {level_path}"

        try:
            # Step 1: Delete namespace if it exists (ignore errors)
            subprocess.run(
                ["kubectl", "delete", "namespace", self.namespace, "--ignore-not-found"],
                capture_output=True,
                timeout=30
            )

            # Step 2: Create fresh namespace
            result = subprocess.run(
                ["kubectl", "create", "namespace", self.namespace],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                return False, f"Failed to create namespace: {result.stderr}"

            # Step 3: Apply broken configuration
            # Note: Not forcing namespace here to respect what's in the YAML
            result = subprocess.run(
                ["kubectl", "apply", "-f", str(broken_yaml)],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                # Log warning but don't fail - some challenges intentionally have issues
                message = f"Deployed with warnings: {result.stderr}"
                return True, message

            return True, f"Challenge deployed to namespace '{self.namespace}'"

        except subprocess.TimeoutExpired:
            return False, "Deployment timed out"
        except Exception as e:
            return False, f"Deployment error: {str(e)}"

    def cleanup_challenge(self, level_path: Path) -> tuple[bool, str]:
        """
        Clean up Kubernetes challenge resources.

        Deletes the entire k8squest namespace.

        Args:
            level_path: Path to level directory

        Returns:
            tuple[bool, str]: (success, message)
        """
        try:
            result = subprocess.run(
                ["kubectl", "delete", "namespace", self.namespace, "--ignore-not-found"],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                return False, f"Cleanup failed: {result.stderr}"

            return True, f"Namespace '{self.namespace}' deleted"

        except subprocess.TimeoutExpired:
            return False, "Cleanup timed out"
        except Exception as e:
            return False, f"Cleanup error: {str(e)}"

    def get_status(self, level_path: Path) -> Dict[str, Any]:
        """
        Get status of deployed Kubernetes resources.

        Attempts to detect resource type from level name and query status.

        Args:
            level_path: Path to level directory

        Returns:
            Dictionary with status information:
            - ready: bool
            - message: str
            - resource_type: str (pod, deployment, etc.)
            - details: additional resource-specific info
        """
        level_name = level_path.name

        try:
            # Try to determine resource type from level name
            if "pod" in level_name.lower():
                return self._get_pod_status()
            elif "deployment" in level_name.lower() or "deploy" in level_name.lower():
                return self._get_deployment_status()
            elif "service" in level_name.lower() or "svc" in level_name.lower():
                return self._get_service_status()
            else:
                # Generic status check
                return self._get_generic_status()

        except Exception as e:
            return {
                'ready': False,
                'message': f"Status check error: {str(e)}",
                'resource_type': 'unknown'
            }

    def _get_pod_status(self) -> Dict[str, Any]:
        """Get pod status (assumes pod name is nginx-broken)"""
        try:
            result = subprocess.run(
                ["kubectl", "get", "pod", "nginx-broken", "-n", self.namespace,
                 "-o", "jsonpath={.status.phase}"],
                capture_output=True,
                text=True,
                timeout=5
            )

            phase = result.stdout.strip() if result.returncode == 0 else "Unknown"

            return {
                'ready': phase == "Running",
                'message': f"Pod phase: {phase}",
                'resource_type': 'pod',
                'phase': phase
            }
        except Exception:
            return {
                'ready': False,
                'message': "Pod not found or error checking status",
                'resource_type': 'pod'
            }

    def _get_deployment_status(self) -> Dict[str, Any]:
        """Get deployment status (assumes deployment name is web)"""
        try:
            result = subprocess.run(
                ["kubectl", "get", "deployment", "web", "-n", self.namespace,
                 "-o", "jsonpath={.status.readyReplicas}"],
                capture_output=True,
                text=True,
                timeout=5
            )

            ready = result.stdout.strip() if result.returncode == 0 else "0"

            return {
                'ready': int(ready or "0") > 0,
                'message': f"{ready} replicas ready",
                'resource_type': 'deployment',
                'ready_replicas': int(ready or "0")
            }
        except Exception:
            return {
                'ready': False,
                'message': "Deployment not found or error checking status",
                'resource_type': 'deployment'
            }

    def _get_service_status(self) -> Dict[str, Any]:
        """Get service status"""
        try:
            result = subprocess.run(
                ["kubectl", "get", "svc", "-n", self.namespace,
                 "-o", "jsonpath={.items[*].metadata.name}"],
                capture_output=True,
                text=True,
                timeout=5
            )

            services = result.stdout.strip().split() if result.returncode == 0 else []

            return {
                'ready': len(services) > 0,
                'message': f"{len(services)} service(s) found",
                'resource_type': 'service',
                'services': services
            }
        except Exception:
            return {
                'ready': False,
                'message': "Error checking service status",
                'resource_type': 'service'
            }

    def _get_generic_status(self) -> Dict[str, Any]:
        """Get generic namespace status"""
        try:
            result = subprocess.run(
                ["kubectl", "get", "all", "-n", self.namespace],
                capture_output=True,
                text=True,
                timeout=10
            )

            has_resources = result.returncode == 0 and len(result.stdout.strip()) > 0

            return {
                'ready': has_resources,
                'message': "Resources deployed" if has_resources else "No resources found",
                'resource_type': 'generic'
            }
        except Exception:
            return {
                'ready': False,
                'message': "Error checking namespace status",
                'resource_type': 'generic'
            }

    def get_deployment_files(self, level_path: Path) -> list[Path]:
        """
        Get list of deployment files for this level.

        Args:
            level_path: Path to level directory

        Returns:
            List of deployment file paths
        """
        files = []
        broken_yaml = level_path / "broken.yaml"
        solution_yaml = level_path / "solution.yaml"

        if broken_yaml.exists():
            files.append(broken_yaml)
        if solution_yaml.exists():
            files.append(solution_yaml)

        return files
