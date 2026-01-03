#!/usr/bin/env python3
"""
MCP Security Domain

A domain focused on Model Context Protocol security vulnerabilities.
Teaches OWASP MCP Top 10:2025 through hands-on exploitation challenges.
"""

from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from domains._base import Domain
from domains._base.validator import BashScriptValidator

# Import MCP-specific components
# Use absolute imports to avoid module resolution issues
import importlib.util
import inspect

def _load_mcp_module(module_name, file_path):
    """Dynamically load MCP module"""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# Load MCP modules dynamically
_mcp_path = Path(__file__).parent

# Check if Docker should be used (default: yes for easier management)
import os
USE_DOCKER = os.environ.get("MCP_USE_DOCKER", "true").lower() in ("true", "1", "yes")

# Load appropriate deployer
if USE_DOCKER:
    _deployer_mod = _load_mcp_module("mcp_deployer_docker", _mcp_path / "deployer_docker.py")
    MCPDeployer = _deployer_mod.MCPDockerDeployer
else:
    _deployer_mod = _load_mcp_module("mcp_deployer", _mcp_path / "deployer.py")
    MCPDeployer = _deployer_mod.MCPDeployer

_safety_mod = _load_mcp_module("mcp_safety", _mcp_path / "safety_guard.py")
_viz_mod = _load_mcp_module("mcp_visualizer", _mcp_path / "visualizer.py")

MCPSafetyGuard = _safety_mod.MCPSafetyGuard
MCPVisualizer = _viz_mod.MCPVisualizer


class MCPDomain(Domain):
    """
    MCP Security Domain.

    This domain contains challenges focused on Model Context Protocol security:
    - World 1: Foundations (Token Exposure, Privilege Escalation)
    - World 2: Injection Attacks (Tool Poisoning, Supply Chain, Command Injection, Prompt Injection)
    - World 3: Advanced Threats (Auth Bypass, No Audit, Shadow Servers, Context Injection)

    Challenges demonstrate OWASP MCP Top 10:2025 vulnerabilities through
    hands-on exploitation of intentionally vulnerable MCP servers.

    Key Innovation:
    - Single persistent MCP gateway on port 8900
    - Users configure AI agent once
    - Gateway routes to challenge-specific backend servers
    - No reconfiguration needed when switching challenges
    """

    def create_deployer(self):
        """
        Create MCP-specific deployer.

        The MCPDeployer manages:
        - Persistent gateway server lifecycle
        - Backend vulnerable server processes
        - State persistence and process tracking

        Returns:
            MCPDeployer instance
        """
        return MCPDeployer(self.config.__dict__)

    def create_validator(self):
        """
        Create validator for MCP challenges.

        MCP challenges use standard bash script validation.
        Users exploit vulnerabilities to extract flags, then run:
            arena validate ARENA{...}

        Returns:
            BashScriptValidator instance
        """
        return BashScriptValidator(self.config.__dict__)

    def create_safety_guard(self):
        """
        Create MCP safety guard.

        Provides protections:
        - Prevent external network exposure (localhost only)
        - Warn about production credentials
        - Validate port ranges

        Returns:
            MCPSafetyGuard instance
        """
        return MCPSafetyGuard(self.config.__dict__)

    def create_visualizer(self):
        """
        Create MCP visualizer.

        Provides visualization of:
        - Gateway status and URL
        - Backend server status
        - Active challenges
        - Architecture diagrams

        Returns:
            MCPVisualizer instance
        """
        return MCPVisualizer(self.config.__dict__)


def load_domain(domain_path: Path) -> MCPDomain:
    """
    Factory function to load the MCP Security domain.

    This function is called by the game engine during domain discovery.

    Args:
        domain_path: Path to domains/mcp/ directory

    Returns:
        MCPDomain instance

    Example:
        >>> domain = load_domain(Path("domains/mcp"))
        >>> print(domain.config.name)
        "MCP Security"
    """
    return MCPDomain(domain_path)
