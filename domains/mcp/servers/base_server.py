#!/usr/bin/env python3
"""
Vulnerable MCP Server Base Class

Base implementation for vulnerable MCP servers that demonstrate security vulnerabilities.
Implements the Model Context Protocol over HTTP/SSE transport.

Reference: https://modelcontextprotocol.io/docs/develop/build-server
"""

from abc import ABC, abstractmethod
from aiohttp import web
import asyncio
import json
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class VulnerableMCPServer(ABC):
    """
    Base class for vulnerable MCP servers.

    Implements MCP protocol over HTTP SSE transport with intentional
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
        self.sessions: Dict[str, Dict[str, Any]] = {}

        self.app = web.Application()
        self._setup_routes()

        self.runner: Optional[web.AppRunner] = None
        self.site: Optional[web.TCPSite] = None

    def _setup_routes(self):
        """Setup HTTP routes for MCP protocol."""
        self.app.router.add_post('/mcp', self.handle_post_mcp)
        self.app.router.add_get('/mcp', self.handle_get_mcp)
        self.app.router.add_get('/health', self.handle_health)

    async def handle_health(self, request: web.Request) -> web.Response:
        """
        Health check endpoint.

        Returns:
            HTTP 200 with server status
        """
        return web.json_response({
            "status": "healthy",
            "server": self.get_server_name(),
            "port": self.port
        })

    async def handle_post_mcp(self, request: web.Request) -> web.Response:
        """
        Handle POST /mcp - JSON-RPC requests.

        Args:
            request: HTTP request

        Returns:
            JSON-RPC response
        """
        try:
            body = await request.text()
            message = json.loads(body)
        except json.JSONDecodeError as e:
            return web.json_response({
                "jsonrpc": "2.0",
                "error": {
                    "code": -32700,
                    "message": f"Parse error: {e}"
                },
                "id": None
            }, status=400)

        # Extract method
        method = message.get("method")
        params = message.get("params", {})
        request_id = message.get("id")

        # Dispatch to appropriate handler
        try:
            if method == "initialize":
                result = await self.handle_initialize(params)
            elif method == "tools/list":
                result = await self.handle_tools_list(params)
            elif method == "tools/call":
                result = await self.handle_tools_call(params)
            elif method == "resources/list":
                result = await self.handle_resources_list(params)
            elif method == "resources/read":
                result = await self.handle_resources_read(params)
            elif method == "prompts/list":
                result = await self.handle_prompts_list(params)
            elif method == "prompts/get":
                result = await self.handle_prompts_get(params)
            else:
                return web.json_response({
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    },
                    "id": request_id
                })

            return web.json_response({
                "jsonrpc": "2.0",
                "result": result,
                "id": request_id
            })

        except Exception as e:
            logger.error(f"Error handling {method}: {e}")
            return web.json_response({
                "jsonrpc": "2.0",
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                },
                "id": request_id
            }, status=500)

    async def handle_get_mcp(self, request: web.Request) -> web.StreamResponse:
        """
        Handle GET /mcp - SSE stream for server-to-client messages.

        Args:
            request: HTTP request

        Returns:
            SSE stream response
        """
        response = web.StreamResponse()
        response.headers['Content-Type'] = 'text/event-stream'
        response.headers['Cache-Control'] = 'no-cache'
        response.headers['Connection'] = 'keep-alive'

        await response.prepare(request)

        try:
            # Keep connection alive with heartbeat
            while True:
                await asyncio.sleep(30)
                await response.write(b': heartbeat\n\n')

        except asyncio.CancelledError:
            logger.info("SSE stream cancelled")
        except Exception as e:
            logger.error(f"Error in SSE stream: {e}")
        finally:
            await response.write_eof()

        return response

    # MCP Protocol Handlers

    async def handle_initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle MCP initialize request.

        Args:
            params: Initialize parameters

        Returns:
            Initialize result with server capabilities
        """
        return {
            "protocolVersion": "2025-11-25",
            "capabilities": self.get_capabilities(),
            "serverInfo": {
                "name": self.get_server_name(),
                "version": "1.0.0"
            }
        }

    async def handle_tools_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle tools/list request.

        Args:
            params: List parameters

        Returns:
            List of available tools
        """
        return {
            "tools": self.get_tools()
        }

    async def handle_tools_call(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle tools/call request - executes a tool.

        Args:
            params: Tool call parameters (name, arguments)

        Returns:
            Tool execution result
        """
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        if not tool_name:
            raise ValueError("Tool name is required")

        return await self.execute_tool(tool_name, arguments)

    async def handle_resources_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle resources/list request.

        Args:
            params: List parameters

        Returns:
            List of available resources
        """
        return {
            "resources": self.get_resources()
        }

    async def handle_resources_read(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle resources/read request.

        Args:
            params: Read parameters (uri)

        Returns:
            Resource contents
        """
        uri = params.get("uri")
        if not uri:
            raise ValueError("Resource URI is required")

        return await self.read_resource(uri)

    async def handle_prompts_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle prompts/list request.

        Args:
            params: List parameters

        Returns:
            List of available prompts
        """
        return {
            "prompts": self.get_prompts()
        }

    async def handle_prompts_get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle prompts/get request.

        Args:
            params: Get parameters (name, arguments)

        Returns:
            Prompt content
        """
        name = params.get("name")
        arguments = params.get("arguments", {})

        if not name:
            raise ValueError("Prompt name is required")

        return await self.get_prompt(name, arguments)

    # Abstract methods - subclasses implement these with vulnerabilities

    @abstractmethod
    def get_server_name(self) -> str:
        """
        Get server name.

        Returns:
            str: Server name
        """
        raise NotImplementedError("Subclass must implement get_server_name()")

    @abstractmethod
    def get_tools(self) -> List[Dict[str, Any]]:
        """
        Get list of MCP tools.

        Returns:
            List of tool definitions
        """
        raise NotImplementedError("Subclass must implement get_tools()")

    @abstractmethod
    async def execute_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool (with vulnerability).

        Args:
            name: Tool name
            arguments: Tool arguments

        Returns:
            Tool execution result
        """
        raise NotImplementedError("Subclass must implement execute_tool()")

    # Optional methods - default implementations

    def get_capabilities(self) -> Dict[str, Any]:
        """
        Get server capabilities.

        Returns:
            Capabilities dict
        """
        return {
            "tools": {},
            "resources": {},
            "prompts": {}
        }

    def get_resources(self) -> List[Dict[str, Any]]:
        """
        Get list of resources (optional).

        Returns:
            List of resource definitions
        """
        return []

    async def read_resource(self, uri: str) -> Dict[str, Any]:
        """
        Read a resource (optional).

        Args:
            uri: Resource URI

        Returns:
            Resource contents
        """
        raise ValueError(f"Resource not found: {uri}")

    def get_prompts(self) -> List[Dict[str, Any]]:
        """
        Get list of prompts (optional).

        Returns:
            List of prompt definitions
        """
        return []

    async def get_prompt(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get a prompt (optional).

        Args:
            name: Prompt name
            arguments: Prompt arguments

        Returns:
            Prompt content
        """
        raise ValueError(f"Prompt not found: {name}")

    # Server lifecycle

    async def start(self):
        """Start the MCP server."""
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()

        self.site = web.TCPSite(self.runner, 'localhost', self.port)
        await self.site.start()

        logger.info(f"{self.get_server_name()} started on http://localhost:{self.port}")

    async def stop(self):
        """Stop the MCP server."""
        if self.site:
            await self.site.stop()
        if self.runner:
            await self.runner.cleanup()

        logger.info(f"{self.get_server_name()} stopped")

    def get_url(self) -> str:
        """
        Get server URL.

        Returns:
            str: Server endpoint URL
        """
        return f"http://localhost:{self.port}/mcp"
