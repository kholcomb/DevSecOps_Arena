#!/usr/bin/env python3
"""
MCP Request Router

Routes JSON-RPC requests from the gateway to appropriate backend MCP servers
based on the active challenge.
"""

from typing import Dict, Optional, Any, Tuple
import httpx


class RequestRouter:
    """
    Routes MCP requests to backend servers.

    Responsibilities:
    - Map challenge IDs to backend server URLs
    - Forward JSON-RPC messages to backends
    - Handle backend health checking
    - Manage backend server registry
    - Map gateway session IDs to backend session IDs
    """

    def __init__(self):
        """Initialize request router."""
        self.active_challenge_id: Optional[str] = None
        self.backend_servers: Dict[str, str] = {}  # challenge_id -> backend_url
        self.client = httpx.AsyncClient(timeout=30.0)
        self.session_map: Dict[str, str] = {}  # gateway_session_id -> backend_session_id

    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()

    def set_active_challenge(self, challenge_id: str, backend_url: str):
        """
        Set the active challenge and register its backend server.

        Args:
            challenge_id: Challenge identifier (e.g., "mcp-level-01-token-exposure")
            backend_url: Backend server URL (e.g., "http://localhost:9001")
        """
        self.active_challenge_id = challenge_id
        self.backend_servers[challenge_id] = backend_url

    def get_active_backend(self) -> Optional[str]:
        """
        Get the backend URL for the active challenge.

        Returns:
            str: Backend URL if active challenge is set, None otherwise
        """
        if self.active_challenge_id:
            return self.backend_servers.get(self.active_challenge_id)
        return None

    def get_backend_for_challenge(self, challenge_id: str) -> Optional[str]:
        """
        Get backend URL for a specific challenge.

        Args:
            challenge_id: Challenge identifier

        Returns:
            str: Backend URL if registered, None otherwise
        """
        return self.backend_servers.get(challenge_id)

    def register_backend(self, challenge_id: str, backend_url: str):
        """
        Register a backend server for a challenge.

        Args:
            challenge_id: Challenge identifier
            backend_url: Backend server URL
        """
        self.backend_servers[challenge_id] = backend_url

    def unregister_backend(self, challenge_id: str) -> bool:
        """
        Unregister a backend server.

        Args:
            challenge_id: Challenge identifier

        Returns:
            bool: True if unregistered, False if not found
        """
        if challenge_id in self.backend_servers:
            del self.backend_servers[challenge_id]
            if self.active_challenge_id == challenge_id:
                self.active_challenge_id = None
            return True
        return False

    async def route_request(self, json_rpc_msg: Dict[str, Any],
                          session_id: Optional[str] = None) -> Tuple[bool, Dict[str, Any], Optional[str]]:
        """
        Route a JSON-RPC request to the appropriate backend server.

        Args:
            json_rpc_msg: JSON-RPC message to forward
            session_id: Optional session ID for routing (currently uses active challenge)

        Returns:
            tuple[bool, dict, str|None]: (success, response_dict, backend_session_id)
                - success: True if request succeeded
                - response_dict: Backend response or error response
                - backend_session_id: Session ID from backend (if any)
        """
        backend_url = self.get_active_backend()

        if not backend_url:
            return False, {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32001,
                    "message": "No active challenge backend",
                    "data": "Deploy a challenge first using arena deploy"
                },
                "id": json_rpc_msg.get("id")
            }, None

        try:
            # Prepare headers for backend request
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "MCP-Protocol-Version": "2025-11-25"
            }

            # For initialize requests, don't send session ID - let backend create one
            # For other requests, map gateway session ID to backend session ID
            if json_rpc_msg.get("method") != "initialize" and session_id:
                # Use mapped backend session ID if available
                backend_session_id_to_send = self.session_map.get(session_id)
                if backend_session_id_to_send:
                    headers["MCP-Session-Id"] = backend_session_id_to_send

            # Forward request to backend server
            response = await self.client.post(
                f"{backend_url}/mcp",
                json=json_rpc_msg,
                headers=headers
            )

            # Extract backend session ID from headers
            backend_session_id = response.headers.get("MCP-Session-Id") or response.headers.get("mcp-session-id")

            # Store session mapping for future requests
            if backend_session_id and session_id:
                self.session_map[session_id] = backend_session_id

            if response.status_code == 200:
                return True, response.json(), backend_session_id
            else:
                return False, {
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32002,
                        "message": f"Backend server error: HTTP {response.status_code}",
                        "data": response.text[:500]  # Limit error message size
                    },
                    "id": json_rpc_msg.get("id")
                }, None

        except httpx.ConnectError as e:
            return False, {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32003,
                    "message": "Cannot connect to backend server",
                    "data": f"Backend at {backend_url} is not responding. Is it running?"
                },
                "id": json_rpc_msg.get("id")
            }, None
        except httpx.TimeoutException:
            return False, {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32004,
                    "message": "Backend server timeout",
                    "data": "Backend server took too long to respond"
                },
                "id": json_rpc_msg.get("id")
            }, None
        except Exception as e:
            return False, {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32603,
                    "message": "Internal routing error",
                    "data": str(e)
                },
                "id": json_rpc_msg.get("id")
            }, None

    async def health_check_backend(self, backend_url: str) -> Tuple[bool, str]:
        """
        Check if a backend server is healthy and responding.

        Args:
            backend_url: Backend server URL

        Returns:
            tuple[bool, str]: (is_healthy, status_message)
        """
        try:
            # Send a simple health check request (or use dedicated health endpoint)
            response = await self.client.get(
                f"{backend_url}/health",
                timeout=5.0
            )

            if response.status_code == 200:
                return True, "Backend server is healthy"
            else:
                return False, f"Backend returned HTTP {response.status_code}"

        except httpx.ConnectError:
            return False, f"Cannot connect to {backend_url}"
        except httpx.TimeoutException:
            return False, "Backend health check timed out"
        except Exception as e:
            return False, f"Health check error: {e}"

    def get_routing_info(self) -> Dict[str, Any]:
        """
        Get current routing configuration.

        Returns:
            dict: Routing information including active challenge and backends
        """
        return {
            "active_challenge": self.active_challenge_id,
            "active_backend": self.get_active_backend(),
            "registered_backends": dict(self.backend_servers),
            "backend_count": len(self.backend_servers)
        }
