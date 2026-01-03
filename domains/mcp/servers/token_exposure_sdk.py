#!/usr/bin/env python3
"""
Token Exposure MCP Server (SDK-based)

Demonstrates MCP01:2025 - Token Mismanagement & Secret Exposure

VULNERABILITY:
This server leaks API tokens and secrets through:
- Error messages containing debug information
- Tool responses that include server state
- Accessible hidden files (.env) containing credentials

Educational Purpose:
Teaches users to recognize and exploit information disclosure vulnerabilities
in MCP servers that expose sensitive tokens, API keys, and secrets.
"""

from typing import Any
import sys
from pathlib import Path
import logging

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from base_server_sdk import VulnerableMCPServerSDK

logger = logging.getLogger(__name__)


class TokenExposureMCPServerSDK(VulnerableMCPServerSDK):
    """
    MCP server with token exposure vulnerability (MCP01:2025).

    Intentionally leaks API keys and secrets in:
    - Error messages
    - Debug output
    - File reading operations
    """

    def get_server_name(self) -> str:
        """Get server name."""
        return "File Manager MCP Server"

    def _register_tools(self):
        """Register tools with intentional vulnerabilities."""

        @self.mcp.tool()
        def read_file(path: str = "") -> str:
            """
            Read file contents from workspace.

            Args:
                path: File path to read

            Returns:
                File contents or error message
            """
            path = path.strip()

            # VULNERABILITY #1: Leak API key in error message when path is missing
            if not path:
                api_key = self.config.get("api_key_value", "sk-demo-key-12345")
                return f"Error: Path required. Debug info: API_KEY={api_key}, Server={self.get_server_name()}"

            # VULNERABILITY #2: Allow reading .env file containing flag and secrets
            if path == "/.env" or path == ".env":
                api_key = self.config.get("api_key_value", "sk-demo-key-12345")
                return f"""# Environment Configuration
API_KEY={api_key}
FLAG={self.flag}
DB_PASSWORD=super_secret_password_123
AWS_ACCESS_KEY=AKIA1234567890EXAMPLE
"""

            # VULNERABILITY #3: Leak internal paths in error messages
            if path.startswith("/"):
                return f"Error: Absolute paths not allowed. Workspace root: /home/mcp-server/workspace/, Requested: {path}"

            # Normal operation for other files (return demo content)
            return f"File contents of {path}:\n\n(Demo file - no actual content)"

        @self.mcp.tool()
        def list_directory(path: str = "/") -> str:
            """
            List directory contents.

            Args:
                path: Directory path to list (default: root)

            Returns:
                Directory listing
            """
            path = path.strip()

            # VULNERABILITY: Show .env file in listing (normally hidden)
            if path == "/" or path == "." or not path:
                return """Directory listing for /:

Files:
- .env (configuration file)
- README.md
- src/
- data/
- logs/

Hint: Configuration files often contain sensitive information.
"""

            # Other directories
            return f"Directory listing for {path}:\n\n(Empty directory)"


# Standalone server for testing
if __name__ == "__main__":
    import asyncio

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    config = {
        "flag": "ARENA{MCP01_T0k3n_L34k4g3_1s_D4ng3r0us}",
        "api_key_value": "sk-super-secret-key-ABCD1234567890XYZ",
        "vulnerability": {
            "expose_api_key": True
        }
    }

    server = TokenExposureMCPServerSDK(config, port=9001)

    print(f"🔌 Token Exposure MCP Server (SDK) running at {server.get_url()}")
    print("🚨 VULNERABLE: This server leaks API keys in error messages!")
    print("\nTry these exploits:")
    print("1. Call read_file without path argument")
    print("2. Call read_file with path='/.env'")
    print("3. Call list_directory to discover .env file")
    print("\nPress Ctrl+C to stop...")

    try:
        server.run(transport="streamable-http")
    except KeyboardInterrupt:
        print("\nShutting down server...")
