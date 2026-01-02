#!/usr/bin/env python3
"""
Safety Guard Abstract Base Class

Defines the interface for safety guards that prevent dangerous operations.
Each domain implements patterns to block destructive commands.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from enum import Enum


class SafetySeverity(Enum):
    """Severity levels for safety violations"""
    SAFE = "safe"           # Command is safe
    WARNING = "warning"     # Requires user confirmation
    CRITICAL = "critical"   # Blocked completely


class SafetyPattern:
    """
    Represents a dangerous pattern to detect.

    Attributes:
        pattern: Regex pattern to match
        message: Message to show user when pattern matches
        severity: How dangerous this pattern is
        suggestion: Optional suggestion for safer alternative
    """

    def __init__(
        self,
        pattern: str,
        message: str,
        severity: SafetySeverity,
        suggestion: Optional[str] = None
    ):
        self.pattern = pattern
        self.message = message
        self.severity = severity
        self.suggestion = suggestion

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format"""
        return {
            "pattern": self.pattern,
            "message": self.message,
            "severity": self.severity.value,
            "suggestion": self.suggestion
        }


class SafetyGuard(ABC):
    """
    Abstract base class for safety guards.

    Each domain implements safety checks appropriate for their tooling:
    - Kubernetes: Prevent deletion of system namespaces, nodes, etc.
    - Docker: Prevent privileged mode without confirmation, bind mounts to /, etc.
    - Terraform: Prevent destruction of stateful resources without confirmation
    """

    def __init__(self, domain_config: Dict[str, Any]):
        """
        Initialize the safety guard with domain-specific configuration.

        Args:
            domain_config: Configuration dictionary from domain_config.yaml
        """
        self.config = domain_config
        self.enabled = domain_config.get("safety_enabled", True)

    @abstractmethod
    def get_dangerous_patterns(self) -> List[SafetyPattern]:
        """
        Get list of dangerous patterns for this domain.

        Returns:
            List of SafetyPattern objects defining what to block

        Example (Kubernetes):
            >>> guard.get_dangerous_patterns()
            [
                SafetyPattern(
                    pattern=r"kubectl\\s+delete\\s+namespace\\s+kube-system",
                    message="Cannot delete system namespace",
                    severity=SafetySeverity.CRITICAL
                ),
                ...
            ]
        """
        raise NotImplementedError("Subclass must implement get_dangerous_patterns()")

    @abstractmethod
    def validate_command(self, command: str, interactive: bool = True) -> tuple[bool, str, SafetySeverity]:
        """
        Validate a command against safety patterns.

        Args:
            command: The command to validate
            interactive: If True, can prompt user for confirmation on warnings

        Returns:
            tuple[bool, str, SafetySeverity]:
                - allowed: Whether command should be executed
                - message: Explanation message
                - severity: Severity level of the violation (if any)

        Example:
            >>> guard.validate_command("kubectl delete namespace kube-system")
            (False, "🚨 BLOCKED: Cannot delete critical system namespaces!", SafetySeverity.CRITICAL)

            >>> guard.validate_command("kubectl delete namespace arena", interactive=True)
            # Prompts user for confirmation, returns:
            (True, "User confirmed deletion", SafetySeverity.WARNING)
        """
        raise NotImplementedError("Subclass must implement validate_command()")

    def is_enabled(self) -> bool:
        """
        Check if safety guard is enabled.

        Returns:
            True if safety checks should be performed
        """
        return self.enabled

    def disable(self):
        """Disable safety guard (use with caution!)"""
        self.enabled = False

    def enable(self):
        """Enable safety guard"""
        self.enabled = True

    def pre_deploy_check(self, level_path) -> tuple[bool, str]:
        """
        Optional hook to check safety before deploying a challenge.

        Override this to perform domain-specific safety checks before
        deployment (e.g., checking for port conflicts, resource limits).

        Args:
            level_path: Path to the level directory

        Returns:
            tuple[bool, str]: (is_safe, message)
        """
        return True, "Pre-deploy safety check: OK"

    def get_safety_info(self) -> str:
        """
        Get human-readable information about safety protections.

        Override this to provide domain-specific safety documentation.

        Returns:
            Markdown-formatted string explaining what is protected
        """
        return """
# Safety Guard

This domain has safety protections enabled to prevent destructive operations.

Use with caution and always work in isolated environments.
"""


class NoOpSafetyGuard(SafetyGuard):
    """
    No-op safety guard that allows everything.

    Use this for domains that don't need safety restrictions
    (e.g., read-only challenges, sandboxed environments).
    """

    def get_dangerous_patterns(self) -> List[SafetyPattern]:
        """Returns empty list - no restrictions"""
        return []

    def validate_command(self, command: str, interactive: bool = True) -> tuple[bool, str, SafetySeverity]:
        """Always allows commands"""
        return True, "", SafetySeverity.SAFE

    def get_safety_info(self) -> str:
        """Return info that safety is disabled"""
        return """
# Safety Guard: Disabled

This domain does not have safety restrictions enabled.
All commands are allowed.
"""
