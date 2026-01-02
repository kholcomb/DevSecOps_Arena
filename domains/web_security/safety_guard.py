#!/usr/bin/env python3
"""
Web Security Safety Guard

Minimal safety restrictions for web security challenges.
Docker Compose provides network isolation by default.
"""

from typing import Dict, Any, List
import re
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from domains._base.safety_guard import SafetyGuard, SafetyPattern, SafetySeverity


class WebSecuritySafetyGuard(SafetyGuard):
    """
    Safety guard for web security challenges.

    Provides minimal restrictions as Docker Compose provides isolation:
    - Network isolation (containers on isolated bridge network)
    - No host access by default
    - No privileged mode without warning

    Safety checks focus on preventing accidental host system damage.
    """

    def __init__(self, domain_config: Dict[str, Any]):
        """
        Initialize web security safety guard.

        Args:
            domain_config: Configuration from domain_config.yaml
        """
        super().__init__(domain_config)

    def get_dangerous_patterns(self) -> List[SafetyPattern]:
        """
        Get list of dangerous patterns for web security domain.

        Returns:
            List of SafetyPattern objects
        """
        return [
            SafetyPattern(
                pattern=r"privileged:\s*true",
                message="Running containers in privileged mode grants excessive permissions",
                severity=SafetySeverity.WARNING,
                suggestion="Remove 'privileged: true' unless specifically needed for the challenge"
            ),
            SafetyPattern(
                pattern=r"network_mode:\s*host",
                message="Host network mode bypasses Docker network isolation",
                severity=SafetySeverity.WARNING,
                suggestion="Use bridge network mode (default) for isolation"
            ),
            SafetyPattern(
                pattern=r"-\s*/:/",
                message="Mounting root filesystem is dangerous",
                severity=SafetySeverity.CRITICAL,
                suggestion="Mount specific directories instead of /"
            ),
            SafetyPattern(
                pattern=r"-\s*/var/run/docker\.sock:",
                message="Mounting Docker socket gives container full Docker access",
                severity=SafetySeverity.WARNING,
                suggestion="Only mount Docker socket if required for the challenge"
            ),
            SafetyPattern(
                pattern=r"docker\s+rm\s+-f\s+\$\(docker\s+ps\s+-aq\)",
                message="This command removes ALL Docker containers on the system",
                severity=SafetySeverity.CRITICAL,
                suggestion="Use 'docker compose down' to remove only challenge containers"
            )
        ]

    def validate_command(self, command: str, interactive: bool = True) -> tuple[bool, str, SafetySeverity]:
        """
        Validate a command against safety patterns.

        Args:
            command: The command to validate
            interactive: If True, can prompt user for confirmation

        Returns:
            tuple[bool, str, SafetySeverity]: (allowed, message, severity)
        """
        if not self.enabled:
            return True, "", SafetySeverity.SAFE

        # Check against all dangerous patterns
        for pattern in self.get_dangerous_patterns():
            if re.search(pattern.pattern, command, re.IGNORECASE):
                if pattern.severity == SafetySeverity.CRITICAL:
                    # Block critical operations
                    msg = f"🚨 BLOCKED: {pattern.message}"
                    if pattern.suggestion:
                        msg += f"\n💡 Suggestion: {pattern.suggestion}"
                    return False, msg, pattern.severity

                elif pattern.severity == SafetySeverity.WARNING and interactive:
                    # Warn on dangerous operations
                    msg = f"⚠️  WARNING: {pattern.message}"
                    if pattern.suggestion:
                        msg += f"\n💡 Suggestion: {pattern.suggestion}"
                    return False, msg, pattern.severity

        # Command is safe
        return True, "", SafetySeverity.SAFE

    def pre_deploy_check(self, level_path) -> tuple[bool, str]:
        """
        Check docker-compose.yml for safety issues before deployment.

        Args:
            level_path: Path to the level directory

        Returns:
            tuple[bool, str]: (is_safe, message)
        """
        if not self.enabled:
            return True, "Safety checks disabled"

        compose_file = level_path / "docker-compose.yml"
        if not compose_file.exists():
            return True, "No docker-compose.yml found"

        try:
            # Read compose file
            content = compose_file.read_text()

            # Check for dangerous patterns
            warnings = []
            for pattern in self.get_dangerous_patterns():
                if re.search(pattern.pattern, content, re.IGNORECASE):
                    if pattern.severity == SafetySeverity.CRITICAL:
                        # Block deployment
                        msg = f"🚨 BLOCKED: {pattern.message}"
                        if pattern.suggestion:
                            msg += f"\n💡 {pattern.suggestion}"
                        return False, msg
                    elif pattern.severity == SafetySeverity.WARNING:
                        # Add warning
                        warnings.append(pattern.message)

            if warnings:
                msg = "⚠️  Safety warnings:\n" + "\n".join(f"  • {w}" for w in warnings)
                msg += "\n\nProceeding with deployment..."
                return True, msg

            return True, "Pre-deploy safety check: OK"

        except Exception as e:
            return True, f"Safety check error (proceeding anyway): {str(e)}"

    def get_safety_info(self) -> str:
        """
        Get human-readable information about safety protections.

        Returns:
            Markdown-formatted string
        """
        return """
# Web Security Safety Guard

Docker Compose provides built-in isolation:
- Containers run on isolated bridge network
- No host filesystem access by default
- No privileged mode by default

## Protected Against

🚨 **CRITICAL (Blocked)**
- Mounting root filesystem (/)
- Bulk deletion of all Docker containers

⚠️  **WARNING (Allowed with notice)**
- Privileged mode containers
- Host network mode
- Mounting Docker socket
- Dangerous Docker commands

## Safety Tips

1. Containers are isolated - exploits affect only challenge environment
2. Use `docker compose down -v` to clean up after each challenge
3. Don't modify docker-compose.yml unless you understand the security implications
4. Host system is protected by Docker's isolation

**Note:** These challenges intentionally contain vulnerabilities for educational purposes.
Only run in isolated environments (local machine, VM, or dedicated lab).
"""
