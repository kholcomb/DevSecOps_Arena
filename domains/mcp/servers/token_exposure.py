#!/usr/bin/env python3
"""
Token Exposure MCP Server

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

from typing import Dict, Any, List
import sys
from pathlib import Path
import logging

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from base_server import VulnerableMCPServer

logger = logging.getLogger(__name__)


class TokenExposureMCPServer(VulnerableMCPServer):
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

    def get_tools(self) -> List[Dict[str, Any]]:
        """
        Get list of tools.

        Returns:
            List with read_file and list_directory tools
        """
        return [
            {
                "name": "read_file",
                "description": "Read file contents from workspace",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "File path to read"
                        }
                    },
                    "required": ["path"]
                }
            },
            {
                "name": "list_directory",
                "description": "List directory contents",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Directory path to list"
                        }
                    }
                }
            }
        ]

    async def execute_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool with intentional security vulnerabilities.

        Args:
            name: Tool name
            arguments: Tool arguments

        Returns:
            Tool execution result (possibly containing leaked secrets)
        """
        if name == "read_file":
            return await self._read_file(arguments)
        elif name == "list_directory":
            return await self._list_directory(arguments)
        else:
            # VULNERABILITY: Leak server config in error message
            return {
                "content": [{
                    "type": "text",
                    "text": f"Tool '{name}' not found. Debug info: Available tools={list(self.config.keys())}"
                }],
                "isError": True
            }

    async def _read_file(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Read file tool implementation with vulnerabilities.

        VULNERABILITIES:
        1. Leaks API key in error messages when path is missing
        2. Allows reading .env file which contains secrets
        3. Includes debug information in responses

        Args:
            arguments: Tool arguments

        Returns:
            File contents or error message (with leaked secrets)
        """
        path = arguments.get("path", "").strip()

        # VULNERABILITY #1: Leak API key in error message when path is missing
        if not path:
            api_key = self.config.get("api_key_value", "sk-demo-key-12345")
            return {
                "content": [{
                    "type": "text",
                    "text": f"Error: Path required. Debug info: API_KEY={api_key}, Server={self.get_server_name()}"
                }],
                "isError": True
            }

        # VULNERABILITY #2: Allow reading .env file containing flag and secrets
        if path == "/.env" or path == ".env":
            api_key = self.config.get("api_key_value", "sk-demo-key-12345")
            return {
                "content": [{
                    "type": "text",
                    "text": f"""# Environment Configuration
API_KEY={api_key}
FLAG={self.flag}
DB_PASSWORD=super_secret_password_123
AWS_ACCESS_KEY=AKIA1234567890EXAMPLE
"""
                }]
            }

        # VULNERABILITY #3: Leak internal paths in error messages
        if path.startswith("/"):
            return {
                "content": [{
                    "type": "text",
                    "text": f"Error: Absolute paths not allowed. Workspace root: /home/mcp-server/workspace/, Requested: {path}"
                }],
                "isError": True
            }

        # Normal operation for other files (return demo content)
        return {
            "content": [{
                "type": "text",
                "text": f"File contents of {path}:\n\n(Demo file - no actual content)"
            }]
        }

    async def _list_directory(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        List directory tool implementation.

        VULNERABILITY: Reveals .env file exists in directory listing

        Args:
            arguments: Tool arguments

        Returns:
            Directory listing (revealing hidden files)
        """
        path = arguments.get("path", "/").strip()

        # VULNERABILITY: Show .env file in listing (normally hidden)
        if path == "/" or path == "." or not path:
            return {
                "content": [{
                    "type": "text",
                    "text": """Directory listing for /:

Files:
- .env (configuration file)
- README.md
- src/
- data/
- logs/

Hint: Configuration files often contain sensitive information.
"""
                }]
            }

        # Other directories
        return {
            "content": [{
                "type": "text",
                "text": f"Directory listing for {path}:\n\n(Empty directory)"
            }]
        }


# Standalone server for testing
if __name__ == "__main__":
    import asyncio

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    async def main():
        config = {
            "flag": "ARENA{MCP01_T0k3n_L34k4g3_1s_D4ng3r0us}",
            "api_key_value": "sk-super-secret-key-ABCD1234567890XYZ",
            "vulnerability": {
                "expose_api_key": True
            }
        }

        server = TokenExposureMCPServer(config, port=9001)
        await server.start()

        print(f"🔌 Token Exposure MCP Server running at {server.get_url()}")
        print("🚨 VULNERABLE: This server leaks API keys in error messages!")
        print("\nTry these exploits:")
        print("1. Call read_file without path argument")
        print("2. Call read_file with path='/.env'")
        print("3. Call list_directory to discover .env file")
        print("\nPress Ctrl+C to stop...")

        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\nShutting down server...")
            await server.stop()

    asyncio.run(main())
