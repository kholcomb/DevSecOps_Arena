#!/usr/bin/env python3
"""
MCP Safety Guard

Safety protections for the MCP security domain.
"""

import sys
from pathlib import Path
from typing import List, Tuple

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from domains._base.safety_guard import SafetyGuard, SafetyPattern, SafetySeverity


class MCPSafetyGuard(SafetyGuard):
    """
    Safety guard for MCP security domain.

    Protections:
    - Prevent binding to 0.0.0.0 (only localhost)
    - Warn about running with production credentials
    - Check port availability
    """

    def get_dangerous_patterns(self) -> List[SafetyPattern]:
        """
        Get list of dangerous command patterns.

        Returns:
            List of SafetyPattern objects
        """
        return [
            SafetyPattern(
                pattern=r"0\.0\.0\.0",
                message="MCP servers should only bind to localhost (127.0.0.1)",
                severity=SafetySeverity.CRITICAL,
                suggestion="Use localhost or 127.0.0.1 instead to prevent external access"
            ),
            SafetyPattern(
                pattern=r"--host\s+0\.0\.0\.0",
                message="Do not expose MCP server to external network",
                severity=SafetySeverity.CRITICAL,
                suggestion="Remove --host flag or use --host localhost"
            )
        ]

    def pre_deploy_check(self, level_path: Path) -> Tuple[bool, str]:
        """
        Safety check before deploying challenge.

        Args:
            level_path: Path to level directory

        Returns:
            tuple[bool, str]: (is_safe, message)
        """
        # Check if server_config.yaml exists
        config_file = level_path / "server_config.yaml"
        if not config_file.exists():
            return False, "server_config.yaml not found"

        # Basic validation - ensure ports are in safe range
        import yaml
        try:
            with open(config_file) as f:
                config = yaml.safe_load(f)

            server_config = config.get("server", {})
            port = server_config.get("port")

            if port and (port < 1024 or port > 65535):
                return False, f"Port {port} is outside safe range (1024-65535)"

            # Warn if using production-like API keys
            config_dict = server_config.get("config", {})
            api_key = config_dict.get("api_key_value", "")

            if api_key and not api_key.startswith("sk-demo") and not api_key.startswith("ARENA"):
                return True, "⚠️  Warning: Configuration contains API key that looks production-like"

            return True, "Pre-deploy safety checks passed"

        except Exception as e:
            return False, f"Error validating configuration: {e}"
