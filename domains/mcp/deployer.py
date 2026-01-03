#!/usr/bin/env python3
"""
MCP Deployer

Manages deployment of MCP security challenges including:
- Persistent MCP gateway lifecycle
- Backend vulnerable server processes
- State persistence
- Port allocation and health checking
"""

import sys
from pathlib import Path
import subprocess
import signal
import time
import json
import logging
from typing import Dict, Any, Optional, Tuple
import shutil

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from domains._base.deployer import ChallengeDeployer

logger = logging.getLogger(__name__)


class MCPDeployer(ChallengeDeployer):
    """
    Deployer for MCP security challenges.

    Manages:
    - Persistent MCP gateway on port 8900
    - Per-challenge backend MCP servers on ports 9001-9010
    - Process tracking and state persistence
    - Health checking
    """

    GATEWAY_PORT = 8900
    BACKEND_PORT_START = 9001
    STATE_FILE = Path.home() / ".arena" / "mcp_state.json"

    def __init__(self, domain_config: Dict[str, Any]):
        """
        Initialize MCP deployer.

        Args:
            domain_config: Domain configuration dictionary
        """
        super().__init__(domain_config)
        self.state_file = self.STATE_FILE
        self.state_file.parent.mkdir(parents=True, exist_ok=True)

    def health_check(self) -> Tuple[bool, str]:
        """
        Check if MCP deployment requirements are met.

        Checks:
        - Python version >= 3.8
        - Required packages (aiohttp) installed
        - Gateway port available or already running

        Returns:
            tuple[bool, str]: (is_healthy, status_message)
        """
        # Check Python version
        if sys.version_info < (3, 8):
            return False, f"Python >= 3.8 required, found {sys.version_info.major}.{sys.version_info.minor}"

        # Check aiohttp package
        try:
            import aiohttp
        except ImportError:
            return False, "Required package 'aiohttp' not installed. Run: pip install aiohttp"

        # Check if gateway is running or port is available
        state = self._load_state()
        if state and state.get("gateway", {}).get("pid"):
            gateway_pid = state["gateway"]["pid"]
            if self._is_process_running(gateway_pid):
                return True, f"Gateway already running (PID {gateway_pid})"
            else:
                # Stale PID - clean it up
                self._cleanup_stale_gateway()

        # Check if port is available
        if self._is_port_in_use(self.GATEWAY_PORT):
            return False, f"Port {self.GATEWAY_PORT} is in use by another process"

        return True, "MCP deployer ready"

    def deploy_challenge(self, level_path: Path) -> Tuple[bool, str]:
        """
        Deploy an MCP security challenge.

        Steps:
        1. Ensure gateway is running
        2. Load server_config.yaml from level
        3. Start backend server process
        4. Wait for backend health check
        5. Update gateway routing
        6. Save state

        Args:
            level_path: Path to level directory

        Returns:
            tuple[bool, str]: (success, message)
        """
        try:
            # Step 1: Ensure gateway is running
            gateway_success, gateway_msg = self._ensure_gateway_running()
            if not gateway_success:
                return False, f"Failed to start gateway: {gateway_msg}"

            logger.info(f"Gateway status: {gateway_msg}")

            # Step 2: Load server configuration
            server_config_file = level_path / "server_config.yaml"
            if not server_config_file.exists():
                return False, f"server_config.yaml not found in {level_path}"

            import yaml
            with open(server_config_file, 'r') as f:
                server_config = yaml.safe_load(f)

            server_info = server_config.get("server", {})
            module_name = server_info.get("module")
            port = server_info.get("port")
            config = server_info.get("config", {})

            if not module_name or not port:
                return False, "server_config.yaml must specify 'module' and 'port'"

            # Step 3: Start backend server
            challenge_id = level_path.name
            backend_success, backend_msg = self._start_backend_server(
                challenge_id, level_path, module_name, port, config
            )

            if not backend_success:
                return False, f"Failed to start backend server: {backend_msg}"

            # Step 4: Wait for backend health check
            backend_url = f"http://localhost:{port}"
            if not self._wait_for_backend(backend_url, timeout=10):
                self._stop_backend_server(challenge_id)
                return False, "Backend server failed to start (health check timeout)"

            # Step 5: Update gateway routing (via HTTP API)
            routing_success, routing_msg = self._update_gateway_routing(challenge_id, backend_url)
            if not routing_success:
                logger.warning(f"Gateway routing update failed: {routing_msg}")

            # Step 6: Save state
            self._save_state()

            # Return concise setup message
            setup_msg = self._get_setup_message(challenge_id)
            return True, f"MCP challenge deployed successfully!\n\n{setup_msg}"

        except Exception as e:
            logger.error(f"Error deploying challenge: {e}", exc_info=True)
            return False, f"Deployment error: {str(e)}"

    def cleanup_challenge(self, level_path: Path) -> Tuple[bool, str]:
        """
        Clean up an MCP challenge.

        Steps:
        1. Stop backend server process
        2. Remove from gateway routing
        3. Update state (keep gateway running)

        Args:
            level_path: Path to level directory

        Returns:
            tuple[bool, str]: (success, message)
        """
        try:
            challenge_id = level_path.name

            # Stop backend server
            backend_stopped = self._stop_backend_server(challenge_id)

            # Save updated state
            self._save_state()

            if backend_stopped:
                return True, f"Challenge {challenge_id} cleaned up (gateway still running)"
            else:
                return True, f"Challenge {challenge_id} was not running"

        except Exception as e:
            logger.error(f"Error cleaning up challenge: {e}", exc_info=True)
            return False, f"Cleanup error: {str(e)}"

    def get_status(self, level_path: Path) -> Dict[str, Any]:
        """
        Get status of MCP challenge deployment.

        Args:
            level_path: Path to level directory

        Returns:
            dict: Status information including gateway and backend status
        """
        challenge_id = level_path.name
        state = self._load_state()

        gateway_running = False
        gateway_pid = None
        if state and state.get("gateway"):
            gateway_pid = state["gateway"].get("pid")
            if gateway_pid and self._is_process_running(gateway_pid):
                gateway_running = True

        backend_running = False
        backend_port = None
        backend_info = state.get("backends", {}).get(challenge_id, {}) if state else {}
        if backend_info:
            backend_pid = backend_info.get("pid")
            backend_port = backend_info.get("port")
            if backend_pid and self._is_process_running(backend_pid):
                backend_running = True

        return {
            "ready": gateway_running and backend_running,
            "message": self._get_status_message(gateway_running, backend_running),
            "gateway": {
                "running": gateway_running,
                "pid": gateway_pid,
                "port": self.GATEWAY_PORT,
                "url": f"http://localhost:{self.GATEWAY_PORT}/mcp"
            },
            "backend": {
                "running": backend_running,
                "port": backend_port,
                "challenge_id": challenge_id if backend_running else None
            }
        }

    def _get_status_message(self, gateway_running: bool, backend_running: bool) -> str:
        """Generate status message based on component states."""
        if gateway_running and backend_running:
            return "MCP challenge ready - gateway and backend running"
        elif gateway_running:
            return "Gateway running but no backend server deployed"
        elif backend_running:
            return "Backend running but gateway is down"
        else:
            return "MCP services not running"

    # Gateway management

    def _ensure_gateway_running(self) -> Tuple[bool, str]:
        """
        Ensure MCP gateway is running, start if needed.

        Returns:
            tuple[bool, str]: (success, message)
        """
        state = self._load_state()

        # Check if already running
        if state and state.get("gateway"):
            gateway_pid = state["gateway"].get("pid")
            if gateway_pid and self._is_process_running(gateway_pid):
                return True, f"Gateway already running (PID {gateway_pid})"

        # Start new gateway
        return self._start_gateway()

    def _start_gateway(self) -> Tuple[bool, str]:
        """
        Start the MCP gateway server.

        Returns:
            tuple[bool, str]: (success, message)
        """
        gateway_script = Path(__file__).parent / "gateway" / "gateway_server.py"

        if not gateway_script.exists():
            return False, f"Gateway script not found: {gateway_script}"

        try:
            # Start gateway as subprocess
            process = subprocess.Popen(
                [sys.executable, str(gateway_script)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                start_new_session=True  # Detach from parent
            )

            # Wait a moment for startup
            time.sleep(2)

            # Check if process started successfully
            if process.poll() is not None:
                # Process exited immediately
                _, stderr = process.communicate()
                return False, f"Gateway failed to start: {stderr.decode()[:500]}"

            # Save gateway state
            state = self._load_state() or {}
            state["gateway"] = {
                "pid": process.pid,
                "port": self.GATEWAY_PORT,
                "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            }
            self._save_state_dict(state)

            return True, f"Gateway started (PID {process.pid})"

        except Exception as e:
            return False, f"Failed to start gateway: {str(e)}"

    def _cleanup_stale_gateway(self):
        """Remove stale gateway info from state."""
        state = self._load_state()
        if state and "gateway" in state:
            del state["gateway"]
            self._save_state_dict(state)

    # Backend server management

    def _start_backend_server(self, challenge_id: str, level_path: Path,
                             module_name: str, port: int,
                             config: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Start a backend MCP server.

        Args:
            challenge_id: Challenge identifier
            level_path: Path to level directory
            module_name: Python module to load (e.g., "servers.token_exposure")
            port: Port to listen on
            config: Server configuration

        Returns:
            tuple[bool, str]: (success, message)
        """
        # Write config to temp file for server to load
        config_file = level_path / ".server_runtime_config.json"
        with open(config_file, 'w') as f:
            json.dump({"config": config, "port": port}, f)

        # Create server startup script
        startup_script = f"""
import sys
import json
import asyncio
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)

# Add paths for imports
arena_root = Path(__file__).parent.parent.parent.parent.parent.parent
mcp_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(arena_root))
sys.path.insert(0, str(mcp_dir))

# Load config (in same directory as this script)
config_file = Path(__file__).parent / ".server_runtime_config.json"
with open(config_file) as f:
    runtime_config = json.load(f)

# Import server class dynamically
import importlib
import inspect
module = importlib.import_module("{module_name}")

# Get server class (assume it's the only class in module ending with "Server")
server_classes = [obj for name, obj in inspect.getmembers(module)
                  if inspect.isclass(obj) and name.endswith("Server") and hasattr(obj, 'get_server_name')]

if not server_classes:
    print(f"No server class found in {module_name}")
    sys.exit(1)

ServerClass = server_classes[0]

# Create and start server
async def main():
    server = ServerClass(runtime_config["config"], runtime_config["port"])
    await server.start()

    # Keep running
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        await server.stop()

asyncio.run(main())
"""

        script_file = level_path.absolute() / ".start_server.py"
        with open(script_file, 'w') as f:
            f.write(startup_script)

        try:
            # Start backend server (use absolute paths, no cwd needed)
            process = subprocess.Popen(
                [sys.executable, str(script_file.absolute())],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                start_new_session=True
            )

            # Wait for startup
            time.sleep(2)

            # Check if process started
            if process.poll() is not None:
                _, stderr = process.communicate()
                return False, f"Backend failed to start: {stderr.decode()[:500]}"

            # Save backend state
            state = self._load_state() or {}
            if "backends" not in state:
                state["backends"] = {}

            state["backends"][challenge_id] = {
                "pid": process.pid,
                "port": port,
                "challenge_path": str(level_path),
                "module": module_name,
                "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            }
            self._save_state_dict(state)

            return True, f"Backend server started (PID {process.pid}, port {port})"

        except Exception as e:
            return False, f"Failed to start backend: {str(e)}"

    def _stop_backend_server(self, challenge_id: str) -> bool:
        """
        Stop a backend server.

        Args:
            challenge_id: Challenge identifier

        Returns:
            bool: True if stopped, False if not running
        """
        state = self._load_state()
        if not state or "backends" not in state:
            return False

        backend_info = state["backends"].get(challenge_id)
        if not backend_info:
            return False

        pid = backend_info.get("pid")
        if pid and self._is_process_running(pid):
            try:
                import os
                import signal

                # Try graceful shutdown first (SIGTERM)
                try:
                    os.kill(pid, signal.SIGTERM)
                except AttributeError:
                    # Windows doesn't have SIGTERM, use CTRL_C_EVENT
                    os.kill(pid, signal.CTRL_C_EVENT if hasattr(signal, 'CTRL_C_EVENT') else 0)

                time.sleep(1)

                # Force kill if still running (SIGKILL on Unix, forceful terminate on Windows)
                if self._is_process_running(pid):
                    try:
                        os.kill(pid, signal.SIGKILL)
                    except AttributeError:
                        # Windows: use taskkill or just try to kill
                        try:
                            import subprocess
                            subprocess.run(["taskkill", "/F", "/PID", str(pid)], check=False, capture_output=True)
                        except Exception:
                            os.kill(pid, 1)  # Fallback

                logger.info(f"Stopped backend server (PID {pid})")
            except Exception as e:
                logger.error(f"Error stopping backend: {e}")

        # Remove from state
        del state["backends"][challenge_id]
        self._save_state_dict(state)

        return True

    def _wait_for_backend(self, backend_url: str, timeout: int = 10) -> bool:
        """
        Wait for backend server to become healthy.

        Args:
            backend_url: Backend URL
            timeout: Timeout in seconds

        Returns:
            bool: True if healthy, False if timeout
        """
        import requests
        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                response = requests.get(f"{backend_url}/health", timeout=2)
                if response.status_code == 200:
                    return True
            except requests.RequestException:
                pass

            time.sleep(0.5)

        return False

    def _update_gateway_routing(self, challenge_id: str, backend_url: str) -> Tuple[bool, str]:
        """
        Update gateway routing configuration via admin API.

        Args:
            challenge_id: Challenge identifier
            backend_url: Backend server URL

        Returns:
            tuple[bool, str]: (success, message)
        """
        try:
            import requests

            # Call gateway admin endpoint to register backend
            response = requests.post(
                f"http://localhost:{self.GATEWAY_PORT}/admin/register",
                json={
                    "challenge_id": challenge_id,
                    "backend_url": backend_url
                },
                timeout=5
            )

            if response.status_code == 200:
                return True, f"Routing configured: {challenge_id} -> {backend_url}"
            else:
                error_msg = response.json().get("error", "Unknown error")
                return False, f"Failed to register backend: {error_msg}"

        except requests.RequestException as e:
            logger.warning(f"Could not update gateway routing: {e}")
            return False, f"Gateway routing update failed: {str(e)}"

    # State management

    def _load_state(self) -> Optional[Dict[str, Any]]:
        """Load state from JSON file."""
        if not self.state_file.exists():
            return None

        try:
            with open(self.state_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading state: {e}")
            return None

    def _save_state(self):
        """Save current state to JSON file."""
        # State is managed by individual methods
        pass

    def _save_state_dict(self, state: Dict[str, Any]):
        """Save state dictionary to file."""
        try:
            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving state: {e}")

    # Helper methods

    def _is_process_running(self, pid: int) -> bool:
        """Check if process is running (cross-platform)."""
        try:
            import os
            import signal
            # Send signal 0 to check if process exists (works on Unix and Windows)
            os.kill(pid, 0)
            return True
        except (OSError, ProcessLookupError):
            return False

    def _is_port_in_use(self, port: int) -> bool:
        """Check if port is in use (cross-platform)."""
        import socket
        try:
            # Try to bind to the port - if it fails, port is in use
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return False  # Successfully bound, port is free
        except OSError:
            return True  # Failed to bind, port is in use

    def _get_setup_message(self, challenge_id: str) -> str:
        """
        Get concise setup message for AI client configuration.

        Args:
            challenge_id: Challenge identifier

        Returns:
            str: Formatted setup instructions for display in retro UI
        """
        return f"""🔌 MCP Gateway Ready

Gateway URL: http://localhost:{self.GATEWAY_PORT}/mcp

How to Connect:

Option 1 - Test with curl (Recommended):
  curl http://localhost:{self.GATEWAY_PORT}/health

Option 2 - Use MCP Inspector (Visual UI):
  npx @modelcontextprotocol/inspector http://localhost:{self.GATEWAY_PORT}/mcp

Option 3 - Custom MCP Client:
  Connect to http://localhost:{self.GATEWAY_PORT}/mcp via HTTP/SSE transport

📖 Full Configuration Guide: domains/mcp/CLIENT_SETUP.md

All challenges route through this gateway - no reconfiguration needed!
"""
