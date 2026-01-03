#!/usr/bin/env python3
"""
Vulnerable MCP Server Base Class (SDK-based)

Base implementation for vulnerable MCP servers using the official MCP Python SDK.
Replaces custom protocol implementation with FastMCP.

Reference: https://github.com/modelcontextprotocol/python-sdk
"""

from abc import ABC, abstractmethod
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
from typing import Dict, Any, Callable
import logging

logger = logging.getLogger(__name__)


class VulnerableMCPServerSDK(ABC):
    """
    Base class for vulnerable MCP servers using official SDK.

    Implements MCP protocol via FastMCP with intentional
    security vulnerabilities for educational purposes.

    Subclasses implement specific vulnerabilities from OWASP MCP Top 10.
    """

    def __init__(self, config: Dict[str, Any], port: int):
        """
        Initialize vulnerable MCP server.

        Args:
            config: Server configuration including flag, vulnerability settings
            port: Port to listen on
        """
        self.config = config
        self.port = port
        self.flag = config.get('flag', 'ARENA{PLACEHOLDER_FLAG}')

        # Create FastMCP server with disabled DNS rebinding protection
        # This is safe because backend is only accessible within Docker network
        transport_security = TransportSecuritySettings(
            enable_dns_rebinding_protection=False
        )

        self.mcp = FastMCP(
            name=self.get_server_name(),
            json_response=True,
            transport_security=transport_security
        )

        # Register tools
        self._register_tools()

    @abstractmethod
    def get_server_name(self) -> str:
        """
        Get server name for MCP protocol.

        Returns:
            str: Server name (e.g., "File Manager MCP Server")
        """
        pass

    @abstractmethod
    def _register_tools(self):
        """
        Register MCP tools using @self.mcp.tool() decorator.

        Example:
            @self.mcp.tool()
            def read_file(path: str) -> str:
                '''Read a file from workspace'''
                # Implementation with vulnerabilities
                return "file contents"
        """
        pass

    def run(self, transport: str = "streamable-http"):
        """
        Run the MCP server.

        Args:
            transport: Transport type ('stdio', 'sse', 'streamable-http')
        """
        logger.info(f"Starting {self.get_server_name()} on port {self.port}")

        if transport == "streamable-http":
            # Get the Starlette app and add health endpoint
            import uvicorn
            from starlette.responses import JSONResponse

            app = self.mcp.streamable_http_app()

            # Add health endpoint for deployer health checks
            @app.route("/health")
            async def health_check(request):
                return JSONResponse({
                    "status": "healthy",
                    "server": self.get_server_name(),
                    "port": self.port
                })

            uvicorn.run(app, host="0.0.0.0", port=self.port, log_level="info")
        elif transport == "sse":
            # SSE transport
            import uvicorn
            app = self.mcp.sse_app()
            uvicorn.run(app, host="0.0.0.0", port=self.port, log_level="info")
        elif transport == "stdio":
            # Stdio transport (for direct AI client connection)
            import asyncio
            asyncio.run(self.mcp.run_stdio_async())
        else:
            raise ValueError(f"Unsupported transport: {transport}")

    async def run_async(self, transport: str = "streamable-http"):
        """
        Run the MCP server asynchronously.

        Args:
            transport: Transport type ('stdio', 'sse', 'streamable-http')
        """
        if transport == "streamable-http":
            await self.mcp.run_streamable_http_async()
        elif transport == "sse":
            await self.mcp.run_sse_async()
        elif transport == "stdio":
            await self.mcp.run_stdio_async()
        else:
            raise ValueError(f"Unsupported transport: {transport}")

    def get_url(self) -> str:
        """Get server URL."""
        return f"http://localhost:{self.port}"
