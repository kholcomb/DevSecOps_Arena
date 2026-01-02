#!/usr/bin/env python3
"""
Challenge Deployer Abstract Base Class

Defines the interface for deploying challenges in different domains.
Each domain implements its own deployer (kubectl, docker-compose, terraform, etc.)
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, Optional


class ChallengeDeployer(ABC):
    """
    Abstract base class for challenge deployment.

    Each domain (Kubernetes, Web Security, Container Security, etc.) implements
    this interface to handle deployment of challenges using their specific tooling.

    Examples:
        - KubectlDeployer: Uses kubectl to deploy K8s manifests
        - DockerComposeDeployer: Uses docker-compose for web apps
        - TerraformDeployer: Uses terraform for IaC challenges
    """

    def __init__(self, domain_config: Dict[str, Any]):
        """
        Initialize the deployer with domain-specific configuration.

        Args:
            domain_config: Configuration dictionary from domain_config.yaml
        """
        self.config = domain_config

    @abstractmethod
    def health_check(self) -> tuple[bool, str]:
        """
        Check if the deployment backend is available and configured.

        This should verify that required tools (kubectl, docker, terraform, etc.)
        are installed and accessible.

        Returns:
            tuple[bool, str]: (is_healthy, status_message)

        Example:
            >>> deployer.health_check()
            (True, "kubectl is installed and cluster is reachable")
        """
        raise NotImplementedError("Subclass must implement health_check()")

    @abstractmethod
    def deploy_challenge(self, level_path: Path) -> tuple[bool, str]:
        """
        Deploy the challenge environment.

        This typically involves:
        1. Reading deployment files (broken.yaml, docker-compose.yml, main.tf, etc.)
        2. Setting up isolated environment (namespace, network, etc.)
        3. Deploying broken/vulnerable infrastructure

        Args:
            level_path: Path to the level directory containing deployment files

        Returns:
            tuple[bool, str]: (success, message)

        Example:
            >>> deployer.deploy_challenge(Path("domains/kubernetes/worlds/world-1/level-1"))
            (True, "Deployed broken pod to arena namespace")
        """
        raise NotImplementedError("Subclass must implement deploy_challenge()")

    @abstractmethod
    def cleanup_challenge(self, level_path: Path) -> tuple[bool, str]:
        """
        Clean up the challenge environment.

        This should remove all resources created by deploy_challenge() to
        prepare for the next challenge.

        Args:
            level_path: Path to the level directory

        Returns:
            tuple[bool, str]: (success, message)

        Example:
            >>> deployer.cleanup_challenge(Path("domains/kubernetes/worlds/world-1/level-1"))
            (True, "Namespace arena deleted")
        """
        raise NotImplementedError("Subclass must implement cleanup_challenge()")

    @abstractmethod
    def get_status(self, level_path: Path) -> Dict[str, Any]:
        """
        Get current status of deployed challenge resources.

        Returns domain-specific status information that can be displayed
        to the user or used for validation.

        Args:
            level_path: Path to the level directory

        Returns:
            Dict with status information. Structure is domain-specific but should include:
            - 'ready': bool - Whether resources are in expected state
            - 'message': str - Human-readable status
            - Additional domain-specific fields

        Example (Kubernetes):
            >>> deployer.get_status(level_path)
            {
                'ready': False,
                'message': 'Pod is CrashLoopBackOff',
                'phase': 'CrashLoopBackOff',
                'restarts': 5
            }

        Example (Docker Compose):
            >>> deployer.get_status(level_path)
            {
                'ready': True,
                'message': 'All containers running',
                'containers': [
                    {'name': 'web', 'status': 'running'},
                    {'name': 'db', 'status': 'running'}
                ]
            }
        """
        raise NotImplementedError("Subclass must implement get_status()")

    def pre_deploy_hook(self, level_path: Path) -> tuple[bool, str]:
        """
        Optional hook called before deployment.

        Override this to perform domain-specific setup tasks.

        Args:
            level_path: Path to the level directory

        Returns:
            tuple[bool, str]: (success, message)
        """
        return True, "Pre-deploy hook: nothing to do"

    def post_deploy_hook(self, level_path: Path) -> tuple[bool, str]:
        """
        Optional hook called after deployment.

        Override this to perform domain-specific post-deployment tasks
        like waiting for resources to be ready.

        Args:
            level_path: Path to the level directory

        Returns:
            tuple[bool, str]: (success, message)
        """
        return True, "Post-deploy hook: nothing to do"

    def get_deployment_files(self, level_path: Path) -> list[Path]:
        """
        Get list of deployment files in the level directory.

        Override this to specify which files your deployer looks for.

        Args:
            level_path: Path to the level directory

        Returns:
            List of Path objects for deployment files

        Example (Kubernetes):
            >>> deployer.get_deployment_files(level_path)
            [Path("broken.yaml"), Path("solution.yaml")]

        Example (Docker Compose):
            >>> deployer.get_deployment_files(level_path)
            [Path("docker-compose.yml")]
        """
        return []
