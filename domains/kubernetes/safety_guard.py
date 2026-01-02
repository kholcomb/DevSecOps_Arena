#!/usr/bin/env python3
"""
Kubernetes Safety Guard

Prevents destructive kubectl commands and enforces namespace restrictions.
Adapted from the original engine/safety.py implementation.
"""

import re
import sys
from pathlib import Path
from typing import Dict, Any, List
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from domains._base import SafetyGuard, SafetyPattern, SafetySeverity

console = Console()


class K8sSafetyGuard(SafetyGuard):
    """
    Safety guard for Kubernetes challenges.

    Protects against:
    - Deleting critical namespaces (kube-system, kube-public, etc.)
    - Deleting cluster nodes
    - Cluster-wide deletions (--all-namespaces)
    - Deleting CRDs and cluster-level RBAC
    - Operations outside arena namespace
    """

    def __init__(self, domain_config: Dict[str, Any]):
        """Initialize K8s safety guard"""
        super().__init__(domain_config)
        self.allowed_namespaces = ["arena", "default"]

    def get_dangerous_patterns(self) -> List[SafetyPattern]:
        """
        Get list of dangerous kubectl patterns.

        Returns:
            List of SafetyPattern objects
        """
        return [
            # Critical - system namespaces
            SafetyPattern(
                pattern=r"kubectl\s+delete\s+namespace\s+(kube-system|kube-public|kube-node-lease|default)",
                message="🚨 BLOCKED: Cannot delete critical system namespaces!",
                severity=SafetySeverity.CRITICAL,
                suggestion="Work in the arena namespace instead"
            ),

            # Warning - arena namespace
            SafetyPattern(
                pattern=r"kubectl\s+delete\s+namespace\s+arena",
                message="⚠️  WARNING: This will delete the entire arena namespace and all your work!",
                severity=SafetySeverity.WARNING,
                suggestion="Delete individual resources instead"
            ),

            # Critical - nodes
            SafetyPattern(
                pattern=r"kubectl\s+delete\s+node",
                message="🚨 BLOCKED: Cannot delete cluster nodes!",
                severity=SafetySeverity.CRITICAL,
                suggestion="Nodes are cluster infrastructure"
            ),

            # Warning - delete all resources
            SafetyPattern(
                pattern=r"kubectl\s+delete\s+\w+\s+--all",
                message="⚠️  WARNING: This will delete ALL resources of this type in the namespace!",
                severity=SafetySeverity.WARNING,
                suggestion="Delete specific resources by name"
            ),

            # Critical - cluster-wide deletions
            SafetyPattern(
                pattern=r"kubectl\s+delete\s+.*\s+--all-namespaces",
                message="🚨 BLOCKED: Cannot delete resources across all namespaces!",
                severity=SafetySeverity.CRITICAL,
                suggestion="Specify a namespace with -n"
            ),

            # Critical - CRDs
            SafetyPattern(
                pattern=r"kubectl\s+delete\s+crd",
                message="🚨 BLOCKED: Cannot delete CustomResourceDefinitions!",
                severity=SafetySeverity.CRITICAL,
                suggestion="CRDs affect the entire cluster"
            ),

            # Critical - ClusterRoles/ClusterRoleBindings
            SafetyPattern(
                pattern=r"kubectl\s+delete\s+(clusterrole|clusterrolebinding)",
                message="🚨 BLOCKED: Cannot delete cluster-level RBAC resources!",
                severity=SafetySeverity.CRITICAL,
                suggestion="Use namespaced Roles instead"
            ),

            # Warning - PersistentVolumes
            SafetyPattern(
                pattern=r"kubectl\s+delete\s+pv\s+",
                message="⚠️  WARNING: Deleting PersistentVolumes can cause data loss!",
                severity=SafetySeverity.WARNING,
                suggestion="Ensure data is backed up"
            ),
        ]

    def validate_command(self, command: str, interactive: bool = True) -> tuple[bool, str, SafetySeverity]:
        """
        Validate a kubectl command against safety patterns.

        Args:
            command: The command to validate
            interactive: If True, can prompt user for confirmation

        Returns:
            tuple[bool, str, SafetySeverity]:
                - allowed: Whether command should be executed
                - message: Explanation message
                - severity: Severity level
        """
        if not self.enabled:
            return True, "Safety guards disabled", SafetySeverity.SAFE

        command_lower = command.lower().strip()

        # Check dangerous patterns
        for pattern_obj in self.get_dangerous_patterns():
            if re.search(pattern_obj.pattern, command_lower, re.IGNORECASE):
                if pattern_obj.severity == SafetySeverity.CRITICAL:
                    # Block completely
                    if interactive:
                        console.print(Panel(
                            f"[bold red]{pattern_obj.message}[/bold red]\n\n"
                            "[yellow]This command is blocked for your safety.[/yellow]\n"
                            "[dim]DevSecOps Arena limits operations to the 'arena' namespace.[/dim]"
                            + (f"\n\n💡 Suggestion: {pattern_obj.suggestion}" if pattern_obj.suggestion else ""),
                            title="[bold red]⛔ Safety Guard Activated[/bold red]",
                            border_style="red"
                        ))
                    return False, pattern_obj.message, SafetySeverity.CRITICAL

                elif pattern_obj.severity == SafetySeverity.WARNING:
                    # Ask for confirmation
                    if interactive:
                        console.print(Panel(
                            f"[bold yellow]{pattern_obj.message}[/bold yellow]\n\n"
                            "[dim]This operation may have unintended consequences.[/dim]"
                            + (f"\n\n💡 Suggestion: {pattern_obj.suggestion}" if pattern_obj.suggestion else ""),
                            title="[bold yellow]⚠️  Caution Required[/bold yellow]",
                            border_style="yellow"
                        ))

                        if not Confirm.ask("Are you sure you want to proceed?", default=False):
                            console.print("[dim]Command cancelled.[/dim]")
                            return False, "User cancelled", SafetySeverity.WARNING
                    else:
                        # Non-interactive mode: warnings are allowed but logged
                        return True, pattern_obj.message, SafetySeverity.WARNING

        # Check namespace usage
        if "kubectl" in command_lower:
            namespace_match = re.search(r"(-n|--namespace)\s+(\S+)", command_lower)

            if namespace_match:
                namespace = namespace_match.group(2)
                if namespace not in self.allowed_namespaces and namespace != "arena":
                    message = f"⚠️  WARNING: DevSecOps Arena should use namespace 'arena', not '{namespace}'"

                    if interactive:
                        console.print(Panel(
                            f"[bold yellow]{message}[/bold yellow]\n\n"
                            "[dim]You're targeting a different namespace.[/dim]",
                            title="[bold yellow]⚠️  Namespace Warning[/bold yellow]",
                            border_style="yellow"
                        ))

                        if not Confirm.ask("Continue anyway?", default=False):
                            return False, "User cancelled", SafetySeverity.WARNING

                    return True, message, SafetySeverity.WARNING

        # Command is safe
        return True, "", SafetySeverity.SAFE

    def get_safety_info(self) -> str:
        """
        Get safety information documentation.

        Returns:
            Markdown-formatted safety documentation
        """
        return """
# Kubernetes Safety Guards

DevSecOps Arena protects you from dangerous kubectl operations:

## 🚫 Blocked Commands:
- Deleting critical namespaces (kube-system, default, etc.)
- Deleting cluster nodes
- Deleting CustomResourceDefinitions
- Cluster-wide deletions (--all-namespaces)
- Deleting ClusterRoles/ClusterRoleBindings

## ⚠️  Commands Requiring Confirmation:
- Deleting arena namespace
- Deleting all resources (--all)
- PersistentVolume operations
- Operations outside arena namespace

## ✅ Best Practices:
- Always use `-n arena` namespace flag
- Avoid cluster-wide operations
- Test changes before applying
- Use `kubectl apply` instead of `kubectl create`

## 🔓 Disabling Safety Guards:
Safety guards can be bypassed with:
    export ARENA_SAFETY=off

But we **strongly recommend** keeping them enabled!
        """

    def pre_deploy_check(self, level_path: Path) -> tuple[bool, str]:
        """
        Check safety before deploying a challenge.

        Args:
            level_path: Path to level directory

        Returns:
            tuple[bool, str]: (is_safe, message)
        """
        # Check if broken.yaml exists
        broken_yaml = level_path / "broken.yaml"
        if not broken_yaml.exists():
            return False, "broken.yaml not found"

        # Additional safety checks could be added here
        # For example: checking for resource limits, validating YAML syntax, etc.

        return True, "Pre-deploy safety check passed"


def print_safety_info():
    """Print safety information (compatibility function)"""
    guard = K8sSafetyGuard({'safety_enabled': True})
    from rich.markdown import Markdown
    console.print(Panel(
        Markdown(guard.get_safety_info()),
        title="[bold green]Safety Information[/bold green]",
        border_style="green"
    ))


# Compatibility functions for existing code
def validate_kubectl_command(command: str, interactive: bool = True) -> bool:
    """
    Validate a kubectl command (compatibility wrapper).

    Args:
        command: The command to validate
        interactive: If True, ask for confirmation on risky commands

    Returns:
        True if command should be executed, False if blocked
    """
    guard = K8sSafetyGuard({'safety_enabled': True})
    allowed, _, _ = guard.validate_command(command, interactive)
    return allowed
