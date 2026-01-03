#!/usr/bin/env python3
"""
MCP Gateway (SDK-based with Proxying)

HTTP/SSE-based MCP gateway that proxies requests to backend challenge servers.

Architecture:
- Client (Claude Desktop/Code/etc) <--(HTTP)--> Gateway <--(HTTP)--> Backend Servers
"""

import sys
import logging
from pathlib import Path
import json
import httpx
import asyncio
from typing import Dict, Any, Optional, List
from mcp.server.fastmcp import FastMCP
from mcp.types import Tool

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

logger = logging.getLogger(__name__)

# State file for tracking active backend
STATE_FILE = Path.home() / ".arena" / "mcp_state.json"


class MCPGatewayProxySDK:
    """
    MCP Gateway that proxies requests to backend challenge servers.

    Uses FastMCP with streamable-http and forwards all tool calls
    to the active backend server.
    """

    def __init__(self, port: int = 8900):
        """Initialize gateway."""
        self.port = port
        self.mcp = FastMCP(
            name="DevSecOps Arena MCP Gateway",
            json_response=True
        )
        self.active_backend_url: Optional[str] = None
        self.active_challenge_id: Optional[str] = None
        self.http_client = httpx.AsyncClient(timeout=30.0)
        self.backend_tools: List[Dict[str, Any]] = []

        # Load active backend from state file
        self._load_active_backend()

        # Register gateway admin tool
        self._register_admin_tools()

    def _load_active_backend(self):
        """Load active backend URL from state file."""
        if STATE_FILE.exists():
            try:
                with open(STATE_FILE) as f:
                    state = json.load(f)
                    backends = state.get("backends", {})
                    if backends:
                        # Get first backend (assumes only one active)
                        for challenge_id, info in backends.items():
                            port = info.get("port")
                            if port:
                                self.active_backend_url = f"http://localhost:{port}"
                                self.active_challenge_id = challenge_id
                                logger.info(f"Loaded active backend: {challenge_id} -> {self.active_backend_url}")
                                break
            except Exception as e:
                logger.warning(f"Could not load state: {e}")

    def _register_admin_tools(self):
        """Register gateway administration tools."""

        @self.mcp.tool()
        async def gateway_status() -> dict:
            """Get gateway status and active challenge information."""
            status = {
                "gateway": "DevSecOps Arena MCP Gateway",
                "active_challenge": self.active_challenge_id or "None",
                "active_backend": self.active_backend_url or "None",
                "backend_healthy": False
            }

            # Check backend health if available
            if self.active_backend_url:
                try:
                    response = await self.http_client.get(
                        f"{self.active_backend_url}/health",
                        timeout=2.0
                    )
                    status["backend_healthy"] = response.status_code == 200
                except Exception:
                    pass

            return status

        @self.mcp.tool()
        def set_backend(challenge_id: str, backend_url: str) -> str:
            """
            Set the active backend server (admin only).

            Args:
                challenge_id: Challenge identifier
                backend_url: Backend server URL (e.g., http://localhost:9001)

            Returns:
                Success message
            """
            self.active_challenge_id = challenge_id
            self.active_backend_url = backend_url
            self.backend_tools = []  # Clear cached tools
            logger.info(f"Backend updated: {challenge_id} -> {backend_url}")
            return f"Backend set to: {challenge_id} ({backend_url})"

    async def fetch_backend_tools(self) -> List[Dict[str, Any]]:
        """Fetch tools from active backend."""
        if not self.active_backend_url:
            return []

        if self.backend_tools:  # Return cached
            return self.backend_tools

        try:
            # Initialize session with backend
            init_response = await self.http_client.post(
                f"{self.active_backend_url}/mcp",
                json={
                    "jsonrpc": "2.0",
                    "id": "init",
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {},
                        "clientInfo": {"name": "gateway", "version": "1.0"}
                    }
                },
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                }
            )

            # List tools from backend
            tools_response = await self.http_client.post(
                f"{self.active_backend_url}/mcp",
                json={
                    "jsonrpc": "2.0",
                    "id": "list_tools",
                    "method": "tools/list",
                    "params": {}
                },
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "MCP-Session-Id": init_response.headers.get("MCP-Session-Id", "")
                }
            )

            data = tools_response.json()
            if "result" in data and "tools" in data["result"]:
                self.backend_tools = data["result"]["tools"]
                logger.info(f"Fetched {len(self.backend_tools)} tools from backend")

        except Exception as e:
            logger.error(f"Error fetching backend tools: {e}")

        return self.backend_tools

    def run(self):
        """Run gateway with streamable-http transport."""
        import uvicorn

        logger.info(f"Starting MCP Gateway on port {self.port}")
        logger.info(f"Active backend: {self.active_backend_url or 'None'}")

        # Get FastMCP Starlette app
        app = self.mcp.streamable_http_app()

        # Run with uvicorn
        uvicorn.run(app, host="127.0.0.1", port=self.port, log_level="info")


async def main():
    """Main entry point."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    gateway = MCPGatewayProxySDK(port=8900)

    print("🔌 MCP Gateway (SDK) running on http://localhost:8900/mcp", file=sys.stderr)
    print(f"📡 Active challenge: {gateway.active_challenge_id or 'None'}", file=sys.stderr)
    print("", file=sys.stderr)
    print("Connect your MCP client to: http://localhost:8900/mcp", file=sys.stderr)
    print("", file=sys.stderr)

    gateway.run()


if __name__ == "__main__":
    asyncio.run(main())
