#!/usr/bin/env python3
"""
MCP Visualizer

Provides visualization data for the MCP security domain.
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from domains._base.visualizer import DomainVisualizer


class MCPVisualizer(DomainVisualizer):
    """
    Visualizer for MCP security challenges.

    Provides real-time information about:
    - Gateway status
    - Backend server status
    - Active sessions
    - MCP traffic (for debugging)
    """

    STATE_FILE = Path.home() / ".arena" / "mcp_state.json"

    def get_visualization_data(self, level_path: Optional[Path] = None) -> Dict[str, Any]:
        """
        Get MCP-specific visualization data.

        Args:
            level_path: Optional path to level directory

        Returns:
            dict: Visualization data including gateway and backend status
        """
        state = self._load_state()

        # Gateway status
        gateway_info = state.get("gateway", {})
        gateway_running = bool(gateway_info.get("pid"))
        gateway_port = gateway_info.get("port", 8900)

        # Backend status
        backends = state.get("backends", {})
        active_backend = None
        if level_path and level_path.name in backends:
            active_backend = backends[level_path.name]

        # Collect backend info
        backend_list = []
        for challenge_id, backend_info in backends.items():
            backend_list.append({
                "challenge_id": challenge_id,
                "port": backend_info.get("port"),
                "pid": backend_info.get("pid"),
                "module": backend_info.get("module"),
                "started_at": backend_info.get("started_at")
            })

        # Determine ready state
        ready = gateway_running and (len(backends) > 0 if not level_path else active_backend is not None)

        # Generate message
        if gateway_running and active_backend:
            message = f"MCP challenge ready on port {active_backend.get('port')}"
        elif gateway_running:
            message = "Gateway running, waiting for challenge deployment"
        else:
            message = "MCP services not running"

        return {
            "domain": "mcp",
            "gateway": {
                "running": gateway_running,
                "port": gateway_port,
                "url": f"http://localhost:{gateway_port}/mcp",
                "pid": gateway_info.get("pid")
            },
            "backend": {
                "running": active_backend is not None,
                "port": active_backend.get("port") if active_backend else None,
                "challenge": level_path.name if level_path and active_backend else None,
                "module": active_backend.get("module") if active_backend else None
            },
            "backends": backend_list,
            "ready": ready,
            "message": message
        }

    def _load_state(self) -> Dict[str, Any]:
        """
        Load MCP state from file.

        Returns:
            dict: State dictionary or empty dict if file doesn't exist
        """
        if not self.STATE_FILE.exists():
            return {}

        try:
            with open(self.STATE_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            return {}

    def get_diagram_template(self, world: str, level: str) -> Optional[Dict[str, Any]]:
        """
        Generate architecture diagram for MCP challenge.

        Args:
            world: World identifier
            level: Level identifier

        Returns:
            dict: Diagram template or None
        """
        return {
            "title": "MCP Challenge Architecture",
            "diagram": """
┌─────────────┐      HTTP POST/GET       ┌──────────────┐
│  AI Agent   │─────────────────────────>│ MCP Gateway  │
│  (Claude)   │<─────────────────────────│  Port 8900   │
└─────────────┘      SSE Stream          └───────┬──────┘
                                                  │
                                         JSON-RPC Proxy
                                                  │
                                         ┌────────▼────────┐
                                         │ Vulnerable MCP  │
                                         │     Server      │
                                         │  [CHALLENGE]    │
                                         └─────────────────┘
""",
            "description": "AI agent connects to gateway which routes to vulnerable backend server"
        }
