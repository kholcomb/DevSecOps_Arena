#!/usr/bin/env python3
"""
MCP Gateway Server

Main HTTP/SSE server implementing the Model Context Protocol gateway.
Runs on port 8900 and routes requests to challenge-specific backend servers.
"""

from aiohttp import web
import asyncio
import json
import logging
from typing import Dict, Any, Optional
import sys
from pathlib import Path

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from protocol import MCPProtocolHandler
from session_manager import SessionManager
from router import RequestRouter
from traffic_logger import TrafficLogger

logger = logging.getLogger(__name__)


class MCPGatewayServer:
    """
    MCP Gateway Server.

    Provides persistent HTTP/SSE endpoint for AI agents to connect once
    and access multiple MCP security challenges without reconfiguration.

    Architecture:
    - Single endpoint on port 8900
    - POST /mcp - Client sends JSON-RPC messages
    - GET /mcp - Client receives SSE stream for server-to-client messages
    - Routes to backend servers based on active challenge
    """

    def __init__(self, port: int = 8900):
        """
        Initialize MCP gateway server.

        Args:
            port: Port to listen on (default 8900)
        """
        self.port = port
        self.protocol_handler = MCPProtocolHandler()
        self.session_manager = SessionManager()
        self.router = RequestRouter()
        self.traffic_logger = TrafficLogger()

        self.app = web.Application()
        self._setup_routes()

        self.runner: Optional[web.AppRunner] = None
        self.site: Optional[web.TCPSite] = None

    def _setup_routes(self):
        """Setup HTTP routes."""
        self.app.router.add_post('/mcp', self.handle_post_mcp)
        self.app.router.add_get('/mcp', self.handle_get_mcp)
        self.app.router.add_get('/health', self.handle_health)
        self.app.router.add_get('/status', self.handle_status)
        self.app.router.add_post('/admin/register', self.handle_register_backend)

    async def handle_health(self, request: web.Request) -> web.Response:
        """
        Health check endpoint.

        Returns:
            HTTP 200 with health status
        """
        return web.json_response({
            "status": "healthy",
            "service": "mcp-gateway",
            "port": self.port,
            "active_sessions": self.session_manager.get_active_session_count(),
            "active_backend": self.router.get_active_backend()
        })

    async def handle_status(self, request: web.Request) -> web.Response:
        """
        Status endpoint providing detailed gateway information.

        Returns:
            HTTP 200 with gateway status and statistics
        """
        return web.json_response({
            "gateway": {
                "port": self.port,
                "status": "running"
            },
            "sessions": {
                "active_count": self.session_manager.get_active_session_count(),
                "all_sessions": {
                    sid: {
                        "challenge_id": s.challenge_id,
                        "message_count": s.message_count,
                        "last_active": s.last_active.isoformat()
                    }
                    for sid, s in self.session_manager.get_all_sessions().items()
                }
            },
            "routing": self.router.get_routing_info(),
            "traffic": self.traffic_logger.get_traffic_stats()
        })

    async def handle_register_backend(self, request: web.Request) -> web.Response:
        """
        Admin endpoint to register a challenge backend with the gateway.

        Expects JSON body:
        {
            "challenge_id": "level-01-token-exposure",
            "backend_url": "http://localhost:9001"
        }

        Returns:
            HTTP 200 with registration confirmation
        """
        try:
            data = await request.json()
            challenge_id = data.get("challenge_id")
            backend_url = data.get("backend_url")

            if not challenge_id or not backend_url:
                return web.json_response({
                    "success": False,
                    "error": "Missing required fields: challenge_id, backend_url"
                }, status=400)

            # Register backend with router
            self.router.set_active_challenge(challenge_id, backend_url)

            logger.info(f"Registered backend: {challenge_id} -> {backend_url}")

            return web.json_response({
                "success": True,
                "challenge_id": challenge_id,
                "backend_url": backend_url,
                "message": f"Backend registered successfully"
            })

        except json.JSONDecodeError:
            return web.json_response({
                "success": False,
                "error": "Invalid JSON body"
            }, status=400)
        except Exception as e:
            logger.error(f"Error registering backend: {e}")
            return web.json_response({
                "success": False,
                "error": str(e)
            }, status=500)

    async def handle_post_mcp(self, request: web.Request) -> web.Response:
        """
        Handle POST /mcp - Client-to-server JSON-RPC messages.

        Args:
            request: HTTP request

        Returns:
            HTTP response (200 with JSON-RPC response or 202 Accepted for notifications)
        """
        # Validate protocol version
        headers = dict(request.headers)
        is_valid, msg = self.protocol_handler.validate_headers(headers)
        if not is_valid:
            return web.Response(status=400, text=msg)

        # Get or create session
        session_id = headers.get('MCP-Session-Id', '').strip()
        if not session_id:
            session_id = self.session_manager.create_session()
            logger.info(f"Created new session: {session_id}")

        # Parse JSON-RPC message
        try:
            body = await request.text()
            success, message, error_msg = self.protocol_handler.parse_message(body)

            if not success:
                error_response = self.protocol_handler.create_error_response(
                    -32700,  # Parse error
                    error_msg
                )
                return web.json_response(error_response, status=400)

        except Exception as e:
            logger.error(f"Error parsing request: {e}")
            error_response = self.protocol_handler.create_error_response(
                -32700,
                f"Failed to parse request: {e}"
            )
            return web.json_response(error_response, status=400)

        # Log request
        self.traffic_logger.log_request(message, session_id)

        # Handle special MCP methods locally (like initialize)
        if message.get("method") == "initialize":
            response = await self._handle_initialize(message, session_id)
            self.traffic_logger.log_response(response, message.get("id"), session_id)
            return web.json_response(response, headers={"MCP-Session-Id": session_id})

        # Route to backend server
        success, response = await self.router.route_request(message, session_id)

        # Log response
        self.traffic_logger.log_response(response, message.get("id"), session_id)

        # Update session
        self.session_manager.touch_session(session_id)

        # Return response
        if "id" in message:
            # Request - return JSON response
            return web.json_response(response, headers={"MCP-Session-Id": session_id})
        else:
            # Notification - return 202 Accepted
            return web.Response(status=202, headers={"MCP-Session-Id": session_id})

    async def _handle_initialize(self, message: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """
        Handle MCP initialize request at gateway level.

        Args:
            message: JSON-RPC initialize request
            session_id: Session identifier

        Returns:
            JSON-RPC initialize response
        """
        # For now, pass initialize through to backend
        # In future, could handle gateway-level capabilities here
        success, response = await self.router.route_request(message, session_id)
        return response

    async def handle_get_mcp(self, request: web.Request) -> web.StreamResponse:
        """
        Handle GET /mcp - Server-to-client SSE stream.

        Args:
            request: HTTP request

        Returns:
            SSE stream response
        """
        # Validate session
        session_id = request.headers.get('MCP-Session-Id', '').strip()
        if not session_id:
            return web.Response(status=400, text="MCP-Session-Id header required")

        session = self.session_manager.get_session(session_id)
        if not session:
            return web.Response(status=404, text="Session not found or expired")

        # Setup SSE stream
        response = web.StreamResponse()
        response.headers['Content-Type'] = 'text/event-stream'
        response.headers['Cache-Control'] = 'no-cache'
        response.headers['Connection'] = 'keep-alive'
        response.headers['MCP-Session-Id'] = session_id

        await response.prepare(request)

        try:
            # For MVP, SSE stream is primarily for backend-initiated messages
            # Keep connection alive and handle disconnection gracefully
            while True:
                # Heartbeat every 30 seconds
                await asyncio.sleep(30)

                # Send comment (heartbeat)
                await response.write(b': heartbeat\n\n')

                # Update session activity
                self.session_manager.touch_session(session_id)

        except asyncio.CancelledError:
            logger.info(f"SSE stream cancelled for session {session_id}")
        except Exception as e:
            logger.error(f"Error in SSE stream: {e}")
        finally:
            await response.write_eof()

        return response

    async def start(self):
        """Start the gateway server."""
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()

        self.site = web.TCPSite(self.runner, 'localhost', self.port)
        await self.site.start()

        logger.info(f"MCP Gateway started on http://localhost:{self.port}/mcp")

    async def stop(self):
        """Stop the gateway server."""
        if self.site:
            await self.site.stop()
        if self.runner:
            await self.runner.cleanup()
        await self.router.close()

        logger.info("MCP Gateway stopped")

    def get_url(self) -> str:
        """
        Get gateway URL.

        Returns:
            str: Gateway endpoint URL
        """
        return f"http://localhost:{self.port}/mcp"


# For running gateway standalone (during development/testing)
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    async def main():
        gateway = MCPGatewayServer(port=8900)
        await gateway.start()

        print(f"🔌 MCP Gateway running at {gateway.get_url()}")
        print("Press Ctrl+C to stop...")

        try:
            # Keep running until interrupted
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\nShutting down gateway...")
            await gateway.stop()

    asyncio.run(main())
