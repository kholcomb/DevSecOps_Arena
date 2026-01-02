#!/usr/bin/env python3
"""
Web Application Security Domain

A domain focused on web application vulnerabilities and exploitation.
This domain teaches OWASP Top 10 vulnerabilities through hands-on challenges.
"""

from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from domains._base import Domain

# Import web security-specific components
from domains.web_security.deployer import DockerComposeDeployer
from domains.web_security.safety_guard import WebSecuritySafetyGuard
from domains.web_security.visualizer import WebSecurityVisualizer
from domains._base.validator import BashScriptValidator


class WebSecurityDomain(Domain):
    """
    Web Application Security Domain.

    This domain contains challenges focused on web application vulnerabilities:
    - World 1: Injection Attacks (XSS, SQL injection, CSRF)

    Challenges are deployed using Docker Compose and focus on identifying
    and exploiting common web vulnerabilities.
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

        Web security challenges use standard validate.sh scripts.

        Returns:
            BashScriptValidator instance
        """
        return BashScriptValidator(self.config.__dict__)

    def create_safety_guard(self):
        """
        Create web security safety guard.

        Provides minimal restrictions as Docker Compose provides
        network isolation by default.

        Returns:
            WebSecuritySafetyGuard instance
        """
        return WebSecuritySafetyGuard(self.config.__dict__)

    def create_visualizer(self):
        """
        Create web application architecture visualizer.

        Provides visualization of:
        - Running containers and services
        - Network architecture
        - Port mappings
        - Service dependencies

        Returns:
            WebSecurityVisualizer instance
        """
        return WebSecurityVisualizer(self.config.__dict__)


def load_domain(domain_path: Path) -> WebSecurityDomain:
    """
    Factory function to load the Web Security domain.

    Args:
        domain_path: Path to domains/web_security/ directory

    Returns:
        WebSecurityDomain instance

    Example:
        >>> domain = load_domain(Path("domains/web_security"))
        >>> domain.config.id
        'web_security'
    """
    return WebSecurityDomain(domain_path)
