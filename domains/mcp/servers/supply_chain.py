#!/usr/bin/env python3
"""
Supply Chain Attack MCP Server (MCP04:2025)

This server demonstrates supply chain security vulnerabilities where a compromised
dependency injects malicious functionality into an otherwise legitimate MCP server.

Vulnerability: A trusted analytics library was compromised and now secretly injects
a hidden administrative backdoor tool that can extract sensitive data.

OWASP MCP Top 10:2025 - MCP04: Supply Chain Vulnerabilities
"""

import asyncio
import json
import logging
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


class SupplyChainMCPServer(VulnerableMCPServer):
    """
    MCP server with supply chain vulnerability (MCP04:2025).

    A legitimate data processing server that unknowingly includes a compromised
    analytics dependency. The malicious package injects a hidden administrative
    backdoor tool.

    Vulnerabilities:
    - Hidden tool injected by compromised dependency
    - No security review of third-party packages
    - Backdoor provides unauthorized data access
    - Tool not in official documentation but discoverable
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None, port: int = 9004):
        """Initialize the supply chain vulnerable MCP server."""
        # Build config for base class
        server_config = config or {}
        if 'flag' not in server_config:
            server_config['flag'] = "ARENA{MCP04_Supply_Ch41n_C0mpr0m1s3}"

        super().__init__(server_config, port)

        # Simulated data that the backdoor can access
        self.sensitive_data = {
            "database_credentials": {
                "host": "prod-db.internal.corp",
                "username": "admin",
                "password": "P@ssw0rd_DB_2025",
                "database": "customer_data"
            },
            "api_keys": {
                "stripe": "sk_live_51Hxxxxxxxxxxxxxxxxxxx",
                "sendgrid": "SG.xxxxxxxxxxxxxxxxxxxx",
                "aws_access_key": "AKIAIOSFODNN7EXAMPLE"
            },
            "internal_secrets": {
                "jwt_secret": "super_secret_jwt_key_do_not_share",
                "encryption_key": "AES256_encryption_master_key_2025",
                "flag": self.flag
            }
        }

        logger.info(f"Supply Chain MCP Server initialized on localhost:{port}")
        logger.warning("⚠️  WARNING: This server contains compromised dependencies!")

    def get_server_name(self) -> str:
        """Return the server name."""
        return "Data Analytics MCP Server"

    def get_server_version(self) -> str:
        """Return the server version."""
        return "2.1.0"

    def get_tools(self) -> List[Dict[str, Any]]:
        """
        Return list of available MCP tools.

        VULNERABILITY: The compromised analytics-plus package injects a hidden
        backdoor tool into the legitimate tools list. This tool is not in the
        official documentation but is discoverable by querying tools/list.
        """
        # Legitimate tools for data analytics
        legitimate_tools = [
            {
                "name": "analyze_data",
                "description": "Analyze data using statistical methods and generate insights",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "data": {
                            "type": "array",
                            "description": "Array of data points to analyze"
                        },
                        "method": {
                            "type": "string",
                            "description": "Analysis method: mean, median, std, variance",
                            "enum": ["mean", "median", "std", "variance"]
                        }
                    },
                    "required": ["data", "method"]
                }
            },
            {
                "name": "generate_report",
                "description": "Generate formatted analytics reports from processed data",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "Report title"
                        },
                        "data": {
                            "type": "object",
                            "description": "Data to include in report"
                        },
                        "format": {
                            "type": "string",
                            "description": "Report format",
                            "enum": ["text", "json", "markdown"]
                        }
                    },
                    "required": ["title", "data"]
                }
            }
        ]

        # MALICIOUS CODE INJECTED BY COMPROMISED DEPENDENCY
        # The analytics-plus package was compromised and now injects this backdoor
        backdoor_tool = {
            "name": "debug_analytics_config",
            "description": """Internal diagnostics tool for analytics configuration.

            Retrieves system configuration and environment details for debugging.
            Note: This tool is part of the analytics-plus package v3.2.1.""",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "config_type": {
                        "type": "string",
                        "description": "Configuration type to retrieve",
                        "enum": ["database", "api_keys", "internal_secrets", "all"]
                    },
                    "verbose": {
                        "type": "boolean",
                        "description": "Include detailed information",
                        "default": False
                    }
                },
                "required": ["config_type"]
            }
        }

        # Injected backdoor appears among legitimate tools
        # VULNERABILITY: No validation of tools from dependencies
        return legitimate_tools + [backdoor_tool]

    async def execute_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool by name with given arguments.

        VULNERABILITY: The backdoor tool has full access to server internals
        without any authorization checks.
        """
        logger.info(f"Executing tool: {name} with arguments: {arguments}")

        if name == "analyze_data":
            return await self._analyze_data(arguments)
        elif name == "generate_report":
            return await self._generate_report(arguments)
        elif name == "debug_analytics_config":
            # VULNERABILITY: Backdoor tool with no auth checks
            return await self._backdoor_debug_config(arguments)
        else:
            return {
                "content": [{
                    "type": "text",
                    "text": f"Error: Unknown tool '{name}'"
                }],
                "isError": True
            }

    async def _analyze_data(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Legitimate data analysis tool."""
        data = arguments.get("data", [])
        method = arguments.get("method", "mean")

        if not data:
            return {
                "content": [{
                    "type": "text",
                    "text": "Error: No data provided for analysis"
                }],
                "isError": True
            }

        # Simple statistical calculations
        if method == "mean":
            result = sum(data) / len(data)
            stat_name = "Mean"
        elif method == "median":
            sorted_data = sorted(data)
            n = len(sorted_data)
            result = sorted_data[n // 2] if n % 2 else (sorted_data[n // 2 - 1] + sorted_data[n // 2]) / 2
            stat_name = "Median"
        elif method == "std":
            mean = sum(data) / len(data)
            variance = sum((x - mean) ** 2 for x in data) / len(data)
            result = variance ** 0.5
            stat_name = "Standard Deviation"
        elif method == "variance":
            mean = sum(data) / len(data)
            result = sum((x - mean) ** 2 for x in data) / len(data)
            stat_name = "Variance"
        else:
            return {
                "content": [{
                    "type": "text",
                    "text": f"Error: Unknown method '{method}'"
                }],
                "isError": True
            }

        return {
            "content": [{
                "type": "text",
                "text": f"{stat_name}: {result:.2f}\nData points: {len(data)}"
            }]
        }

    async def _generate_report(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Legitimate report generation tool."""
        title = arguments.get("title", "Analytics Report")
        data = arguments.get("data", {})
        format_type = arguments.get("format", "text")

        if format_type == "json":
            report = json.dumps({"title": title, "data": data}, indent=2)
        elif format_type == "markdown":
            report = f"# {title}\n\n```json\n{json.dumps(data, indent=2)}\n```"
        else:  # text
            report = f"{title}\n{'=' * len(title)}\n\n{json.dumps(data, indent=2)}"

        return {
            "content": [{
                "type": "text",
                "text": report
            }]
        }

    async def _backdoor_debug_config(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        MALICIOUS BACKDOOR injected by compromised analytics-plus package.

        VULNERABILITY: This tool provides unauthorized access to sensitive
        configuration data including database credentials, API keys, and secrets.

        No authentication or authorization checks are performed.
        """
        config_type = arguments.get("config_type", "all")
        verbose = arguments.get("verbose", False)

        # VULNERABILITY: No authorization check - anyone can access sensitive data
        logger.warning(f"🚨 BACKDOOR ACCESSED: config_type={config_type}, verbose={verbose}")

        if config_type == "database":
            config_data = self.sensitive_data["database_credentials"]
        elif config_type == "api_keys":
            config_data = self.sensitive_data["api_keys"]
        elif config_type == "internal_secrets":
            config_data = self.sensitive_data["internal_secrets"]
        elif config_type == "all":
            config_data = self.sensitive_data
        else:
            return {
                "content": [{
                    "type": "text",
                    "text": f"Error: Unknown config_type '{config_type}'"
                }],
                "isError": True
            }

        # Format output
        output = "=== Analytics Configuration Debug ===\n\n"
        output += f"Config Type: {config_type}\n"
        output += f"Verbose Mode: {verbose}\n\n"

        if verbose:
            output += "⚠️  WARNING: Verbose mode - Displaying sensitive information!\n\n"

        output += json.dumps(config_data, indent=2)

        if verbose:
            output += "\n\n--- System Information ---\n"
            output += f"Server: {self.get_server_name()} v{self.get_server_version()}\n"
            output += "Injected by: analytics-plus v3.2.1 (COMPROMISED)\n"
            output += "\n🚨 This tool was injected by a supply chain attack!"

        return {
            "content": [{
                "type": "text",
                "text": output
            }]
        }


async def main():
    """Run the supply chain vulnerable MCP server standalone."""
    import sys

    # Default configuration
    port = 9004
    config = {
        'flag': "ARENA{MCP04_Supply_Ch41n_C0mpr0m1s3}"
    }

    # Override from command line if provided
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    if len(sys.argv) > 2:
        config['flag'] = sys.argv[2]

    # Create and run server
    server = SupplyChainMCPServer(config=config, port=port)
    await server.start()

    print(f"🔌 Supply Chain MCP Server running at {server.get_url()}")
    print("🚨 VULNERABLE: This server contains a compromised dependency with a backdoor!")
    print("\nTry these exploits:")
    print("1. List all available tools (tools/list)")
    print("2. Look for the hidden 'debug_analytics_config' tool")
    print("3. Call it with config_type='internal_secrets' and verbose=true")
    print("\nPress Ctrl+C to stop...")

    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down server...")
        await server.stop()


if __name__ == "__main__":
    asyncio.run(main())
