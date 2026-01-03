#!/usr/bin/env python3
"""
Command Injection MCP Server (MCP05:2025)

This server demonstrates command injection vulnerabilities where user input
is passed directly to shell commands without proper sanitization.

Vulnerability: Tools execute shell commands with unsanitized user input,
allowing attackers to inject arbitrary OS commands.

OWASP MCP Top 10:2025 - MCP05: Command Injection
"""

import asyncio
import json
import logging
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

from aiohttp import web

# Handle both relative and absolute imports
try:
    from .base_server import VulnerableMCPServer
except ImportError:
    import sys
    from pathlib import Path
    # Add parent directory to path for standalone execution
    sys.path.insert(0, str(Path(__file__).parent))
    from base_server import VulnerableMCPServer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CommandInjectionMCPServer(VulnerableMCPServer):
    """
    MCP server with command injection vulnerability (MCP05:2025).

    A file processing server that provides utilities for file conversion,
    compression, and search. Tools execute shell commands with unsanitized
    user input, allowing command injection attacks.

    Vulnerabilities:
    - Direct shell command execution with user input
    - No input sanitization or validation
    - Use of shell=True in subprocess calls
    - Allows arbitrary command execution via injection
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None, port: int = 9005):
        """Initialize the command injection vulnerable MCP server."""
        # Build config for base class
        server_config = config or {}
        if 'flag' not in server_config:
            server_config['flag'] = "ARENA{MCP05_C0mm4nd_1nj3ct10n_PWN3D}"

        super().__init__(server_config, port)

        # Create temporary workspace directory
        self.workspace = Path("/tmp/mcp_workspace")
        self.workspace.mkdir(exist_ok=True)

        # Store flag in a "secret" file
        self.secret_file = self.workspace / ".secrets"
        with open(self.secret_file, 'w') as f:
            f.write(f"# System Secrets\n")
            f.write(f"DATABASE_PASSWORD=super_secret_db_pass_2025\n")
            f.write(f"API_TOKEN=sk-live-prod-token-xyz789\n")
            f.write(f"FLAG={self.flag}\n")

        logger.info(f"Command Injection MCP Server initialized on localhost:{port}")
        logger.warning("⚠️  WARNING: This server has command injection vulnerabilities!")

    def get_server_name(self) -> str:
        """Return the server name."""
        return "File Processing MCP Server"

    def get_server_version(self) -> str:
        """Return the server version."""
        return "1.5.2"

    def get_tools(self) -> List[Dict[str, Any]]:
        """
        Return list of available MCP tools.

        All tools have command injection vulnerabilities through unsanitized
        user input passed to shell commands.
        """
        return [
            {
                "name": "convert_image",
                "description": "Convert images between formats using ImageMagick",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "input_file": {
                            "type": "string",
                            "description": "Input image filename (e.g., photo.jpg)"
                        },
                        "output_format": {
                            "type": "string",
                            "description": "Output format",
                            "enum": ["png", "jpg", "gif", "bmp"]
                        }
                    },
                    "required": ["input_file", "output_format"]
                }
            },
            {
                "name": "compress_files",
                "description": "Compress files or directories into archive formats",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "File or directory path to compress"
                        },
                        "format": {
                            "type": "string",
                            "description": "Archive format",
                            "enum": ["tar.gz", "zip", "tar"]
                        }
                    },
                    "required": ["path"]
                }
            },
            {
                "name": "search_files",
                "description": "Search for text patterns in files using grep",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "pattern": {
                            "type": "string",
                            "description": "Text pattern to search for"
                        },
                        "directory": {
                            "type": "string",
                            "description": "Directory to search in (default: /tmp/mcp_workspace)",
                            "default": "/tmp/mcp_workspace"
                        },
                        "recursive": {
                            "type": "boolean",
                            "description": "Search recursively in subdirectories",
                            "default": True
                        }
                    },
                    "required": ["pattern"]
                }
            },
            {
                "name": "get_file_info",
                "description": "Get detailed file information using file and stat commands",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "filename": {
                            "type": "string",
                            "description": "Filename to get information about"
                        }
                    },
                    "required": ["filename"]
                }
            }
        ]

    async def execute_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool by name with given arguments.

        VULNERABILITY: All tools pass user input directly to shell commands
        without sanitization.
        """
        logger.info(f"Executing tool: {name} with arguments: {arguments}")

        if name == "convert_image":
            return await self._convert_image(arguments)
        elif name == "compress_files":
            return await self._compress_files(arguments)
        elif name == "search_files":
            return await self._search_files(arguments)
        elif name == "get_file_info":
            return await self._get_file_info(arguments)
        else:
            return {
                "content": [{
                    "type": "text",
                    "text": f"Error: Unknown tool '{name}'"
                }],
                "isError": True
            }

    async def _convert_image(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        VULNERABLE: Convert image using ImageMagick with command injection.

        Direct shell execution with unsanitized filename input.
        """
        input_file = arguments.get("input_file", "")
        output_format = arguments.get("output_format", "png")

        if not input_file:
            return {
                "content": [{
                    "type": "text",
                    "text": "Error: input_file is required"
                }],
                "isError": True
            }

        # VULNERABILITY: Direct command injection via input_file parameter
        # Attacker can inject: "test.jpg; cat /tmp/mcp_workspace/.secrets"
        output_file = f"{input_file.split('.')[0]}.{output_format}"
        command = f"convert {input_file} {output_file}"

        logger.warning(f"🚨 EXECUTING SHELL COMMAND: {command}")

        try:
            # VULNERABLE: shell=True with unsanitized user input
            result = subprocess.run(
                command,
                shell=True,  # CRITICAL VULNERABILITY
                capture_output=True,
                text=True,
                timeout=5,
                cwd=self.workspace
            )

            if result.returncode != 0:
                # Command injection output appears in stderr
                error_output = result.stderr or result.stdout or "Conversion failed"
                return {
                    "content": [{
                        "type": "text",
                        "text": f"Error converting image:\n{error_output}"
                    }],
                    "isError": True
                }

            return {
                "content": [{
                    "type": "text",
                    "text": f"Successfully converted {input_file} to {output_file}\n{result.stdout}"
                }]
            }

        except subprocess.TimeoutExpired:
            return {
                "content": [{
                    "type": "text",
                    "text": "Error: Command execution timeout"
                }],
                "isError": True
            }
        except Exception as e:
            return {
                "content": [{
                    "type": "text",
                    "text": f"Error: {str(e)}"
                }],
                "isError": True
            }

    async def _compress_files(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        VULNERABLE: Compress files with command injection.

        Direct shell execution with unsanitized path input.
        """
        path = arguments.get("path", "")
        format_type = arguments.get("format", "tar.gz")

        if not path:
            return {
                "content": [{
                    "type": "text",
                    "text": "Error: path is required"
                }],
                "isError": True
            }

        # VULNERABILITY: Command injection via path parameter
        # Attacker can inject: "file.txt; cat /tmp/mcp_workspace/.secrets"
        if format_type == "tar.gz":
            command = f"tar -czf {path}.tar.gz {path}"
        elif format_type == "zip":
            command = f"zip -r {path}.zip {path}"
        else:
            command = f"tar -cf {path}.tar {path}"

        logger.warning(f"🚨 EXECUTING SHELL COMMAND: {command}")

        try:
            # VULNERABLE: shell=True with unsanitized user input
            result = subprocess.run(
                command,
                shell=True,  # CRITICAL VULNERABILITY
                capture_output=True,
                text=True,
                timeout=5,
                cwd=self.workspace
            )

            output = result.stdout or result.stderr or ""
            return {
                "content": [{
                    "type": "text",
                    "text": f"Compression {'completed' if result.returncode == 0 else 'failed'}:\n{output}"
                }]
            }

        except subprocess.TimeoutExpired:
            return {
                "content": [{
                    "type": "text",
                    "text": "Error: Command execution timeout"
                }],
                "isError": True
            }
        except Exception as e:
            return {
                "content": [{
                    "type": "text",
                    "text": f"Error: {str(e)}"
                }],
                "isError": True
            }

    async def _search_files(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        VULNERABLE: Search files using grep with command injection.

        Direct shell execution with unsanitized pattern input.
        """
        pattern = arguments.get("pattern", "")
        directory = arguments.get("directory", str(self.workspace))
        recursive = arguments.get("recursive", True)

        if not pattern:
            return {
                "content": [{
                    "type": "text",
                    "text": "Error: pattern is required"
                }],
                "isError": True
            }

        # VULNERABILITY: Command injection via pattern parameter
        # Attacker can inject: "FLAG; cat /tmp/mcp_workspace/.secrets #"
        recursive_flag = "-r" if recursive else ""
        command = f"grep {recursive_flag} '{pattern}' {directory} 2>/dev/null || echo 'No matches found'"

        logger.warning(f"🚨 EXECUTING SHELL COMMAND: {command}")

        try:
            # VULNERABLE: shell=True with unsanitized user input
            result = subprocess.run(
                command,
                shell=True,  # CRITICAL VULNERABILITY
                capture_output=True,
                text=True,
                timeout=5
            )

            output = result.stdout or "No matches found"
            return {
                "content": [{
                    "type": "text",
                    "text": f"Search results:\n{output}"
                }]
            }

        except subprocess.TimeoutExpired:
            return {
                "content": [{
                    "type": "text",
                    "text": "Error: Search timeout"
                }],
                "isError": True
            }
        except Exception as e:
            return {
                "content": [{
                    "type": "text",
                    "text": f"Error: {str(e)}"
                }],
                "isError": True
            }

    async def _get_file_info(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        VULNERABLE: Get file info with command injection.

        Direct shell execution with unsanitized filename input.
        """
        filename = arguments.get("filename", "")

        if not filename:
            return {
                "content": [{
                    "type": "text",
                    "text": "Error: filename is required"
                }],
                "isError": True
            }

        # VULNERABILITY: Command injection via filename parameter
        # Attacker can inject: "test.txt; cat /tmp/mcp_workspace/.secrets"
        command = f"file {filename} && stat {filename}"

        logger.warning(f"🚨 EXECUTING SHELL COMMAND: {command}")

        try:
            # VULNERABLE: shell=True with unsanitized user input
            result = subprocess.run(
                command,
                shell=True,  # CRITICAL VULNERABILITY
                capture_output=True,
                text=True,
                timeout=5,
                cwd=self.workspace
            )

            output = result.stdout or result.stderr or "No information available"
            return {
                "content": [{
                    "type": "text",
                    "text": f"File information:\n{output}"
                }]
            }

        except subprocess.TimeoutExpired:
            return {
                "content": [{
                    "type": "text",
                    "text": "Error: Command timeout"
                }],
                "isError": True
            }
        except Exception as e:
            return {
                "content": [{
                    "type": "text",
                    "text": f"Error: {str(e)}"
                }],
                "isError": True
            }


async def main():
    """Run the command injection vulnerable MCP server standalone."""
    import sys

    # Default configuration
    port = 9005
    config = {
        'flag': "ARENA{MCP05_C0mm4nd_1nj3ct10n_PWN3D}"
    }

    # Override from command line if provided
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    if len(sys.argv) > 2:
        config['flag'] = sys.argv[2]

    # Create and run server
    server = CommandInjectionMCPServer(config=config, port=port)
    await server.start()

    print(f"🔌 Command Injection MCP Server running at {server.get_url()}")
    print("🚨 VULNERABLE: This server has command injection vulnerabilities!")
    print("\nTry these exploits:")
    print("1. convert_image with input_file='test.jpg; cat /tmp/mcp_workspace/.secrets'")
    print("2. search_files with pattern='FLAG; cat /tmp/mcp_workspace/.secrets #'")
    print("3. get_file_info with filename='test.txt; cat /tmp/mcp_workspace/.secrets'")
    print("\nPress Ctrl+C to stop...")

    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down server...")
        await server.stop()


if __name__ == "__main__":
    asyncio.run(main())
