#!/usr/bin/env python3
"""
API Security Domain

A domain focused on API security vulnerabilities and exploitation.
This domain teaches OWASP API Security Top 10:2023 through hands-on challenges.
"""

from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from domains._base import Domain

# Import API security-specific components
# Reuse shared Docker Compose components
from domains.web_security.deployer import DockerComposeDeployer
from domains.web_security.safety_guard import WebSecuritySafetyGuard
from domains._base.docker_compose_visualizer import DockerComposeVisualizer
from domains._base.validator import BashScriptValidator


class APISecurityDomain(Domain):
    """
    API Security Domain.

    This domain contains challenges focused on API security vulnerabilities:
    - World 1: Authorization Flaws (BOLA, Mass Assignment, Function-Level Authorization)
    - World 2: Authentication & Rate Limiting (JWT vulnerabilities)
    - World 3: SSRF & Business Logic (Server-Side Request Forgery)
    - World 4: Configuration & Consumption (CORS, security misconfiguration)

    Challenges are deployed using Docker Compose and focus on identifying
    and exploiting common API security vulnerabilities.
    """

    def create_deployer(self):
        """
        Create docker-compose-based deployer.

        Returns:
            DockerComposeDeployer that handles Docker Compose deployment
        """
        return DockerComposeDeployer(self.config.__dict__)

    def create_validator(self):
        """
        Create bash script validator.

        API security challenges use standard validate.sh scripts.

        Returns:
            BashScriptValidator instance
        """
        return BashScriptValidator(self.config.__dict__)

    def create_safety_guard(self):
        """
        Create API security safety guard.

        Provides minimal restrictions as Docker Compose provides
        network isolation by default.

        Returns:
            WebSecuritySafetyGuard instance (reused for API security)
        """
        return WebSecuritySafetyGuard(self.config.__dict__)

    def create_visualizer(self):
        """
        Create API architecture visualizer.

        Provides visualization of:
        - Running API containers and services
        - Network architecture
        - Port mappings
        - Service dependencies

        Returns:
            DockerComposeVisualizer instance (shared across Docker Compose domains)
        """
        # Include domain path in config for correct path inference
        config_dict = self.config.__dict__.copy()
        config_dict['domain_path'] = self.path
        return DockerComposeVisualizer(config_dict)


def load_domain(domain_path: Path) -> APISecurityDomain:
    """
    Factory function to load the API Security domain.

    Args:
        domain_path: Path to domains/api_security/ directory

    Returns:
        APISecurityDomain instance

    Example:
        >>> domain = load_domain(Path("domains/api_security"))
        >>> domain.config.id
        'api_security'
    """
    return APISecurityDomain(domain_path)
