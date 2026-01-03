#!/usr/bin/env python3
"""
MCP Docker Deployer

Manages deployment of MCP security challenges using Docker containers.
Replaces subprocess-based deployment with containerized services.
"""

import sys
import subprocess
import json
import logging
import time
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
import shutil

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from domains._base.deployer import ChallengeDeployer

logger = logging.getLogger(__name__)


class MCPDockerDeployer(ChallengeDeployer):
    """
    Docker-based deployer for MCP security challenges.

    Manages:
    - Docker image building
    - Gateway container (persistent)
    - Backend containers (per-challenge)
    - Container health checking
    """

    GATEWAY_PORT = 8900
    BACKEND_PORT_START = 9001
    DOCKER_COMPOSE_FILE = Path(__file__).parent / "docker-compose.yml"
    MCP_NETWORK = "devsecops-arena-mcp"

    # Container names
    GATEWAY_CONTAINER = "devsecops-arena-mcp-gateway"
    BACKEND_CONTAINER = "devsecops-arena-mcp-backend"

    def __init__(self, domain_config: Dict[str, Any]):
        """
        Initialize MCP Docker deployer.

        Args:
            domain_config: Domain configuration dictionary
        """
        super().__init__(domain_config)
        self.mcp_dir = Path(__file__).parent
        self.arena_root = self.mcp_dir.parent.parent

    def health_check(self) -> Tuple[bool, str]:
        """
        Check if Docker is available and running.

        Returns:
            tuple[bool, str]: (is_healthy, status_message)
        """
        # Check if docker command exists
        if not shutil.which("docker"):
            return False, "Docker not found. Please install Docker Desktop"

        # Check if Docker daemon is running
        try:
            result = subprocess.run(
                ["docker", "info"],
                capture_output=True,
                timeout=5
            )
            if result.returncode != 0:
                return False, "Docker daemon not running. Please start Docker Desktop"
        except subprocess.TimeoutExpired:
            return False, "Docker not responding. Please check Docker Desktop"
        except Exception as e:
            return False, f"Docker check failed: {e}"

        return True, "Docker available and running"

    def deploy_challenge(self, level_path: Path) -> Tuple[bool, str]:
        """
        Deploy an MCP security challenge using Docker.

        Args:
            level_path: Path to level directory

        Returns:
            tuple[bool, str]: (success, message)
        """
        try:
            challenge_id = level_path.name

            # Step 1: Build Docker image if needed
            logger.info("Building Docker image...")
            build_success, build_msg = self._build_image()
            if not build_success:
                return False, f"Failed to build image: {build_msg}"

            # Step 2: Ensure gateway container is running
            logger.info("Ensuring gateway container is running...")
            gateway_success, gateway_msg = self._ensure_gateway_running()
            if not gateway_success:
                return False, f"Failed to start gateway: {gateway_msg}"

            # Step 3: Load server configuration
            server_config_file = level_path / "server_config.yaml"
            if not server_config_file.exists():
                return False, f"server_config.yaml not found in {level_path}"

            import yaml
            with open(server_config_file, 'r') as f:
                server_config = yaml.safe_load(f)

            server_info = server_config.get("server", {})
            module_name = server_info.get("module")
            port = server_info.get("port", self.BACKEND_PORT_START)
            config = server_info.get("config", {})

            # Step 4: Start backend container
            logger.info(f"Starting backend container for {challenge_id}...")
            backend_success, backend_msg = self._start_backend_container(
                challenge_id, level_path, module_name, port, config
            )
            if not backend_success:
                return False, f"Failed to start backend: {backend_msg}"

            # Step 5: Wait for backend health check
            # Use container name for internal Docker network communication
            backend_url_internal = f"http://{self.BACKEND_CONTAINER}:{port}"

            # Wait for backend to be healthy (we'll check from gateway container)
            time.sleep(5)  # Give backend time to start

            # Step 6: Register backend with gateway
            logger.info("Registering backend with gateway...")
            routing_success, routing_msg = self._update_gateway_routing(challenge_id, backend_url_internal)
            if not routing_success:
                logger.warning(f"Gateway routing update failed: {routing_msg}")

            # Success message
            setup_msg = self._get_setup_message(challenge_id)
            return True, f"MCP challenge deployed successfully!\n\n{setup_msg}"

        except Exception as e:
            logger.error(f"Error deploying challenge: {e}", exc_info=True)
            return False, f"Deployment error: {str(e)}"

    def cleanup_challenge(self, level_path: Path) -> Tuple[bool, str]:
        """
        Clean up an MCP challenge (stop backend container).

        Args:
            level_path: Path to level directory

        Returns:
            tuple[bool, str]: (success, message)
        """
        try:
            challenge_id = level_path.name

            # Stop backend container
            logger.info(f"Stopping backend container...")
            self._stop_backend_container()

            return True, f"Challenge {challenge_id} cleaned up (gateway still running)"

        except Exception as e:
            logger.error(f"Error cleaning up challenge: {e}", exc_info=True)
            return False, f"Cleanup error: {str(e)}"

    def get_status(self, level_path: Path) -> Dict[str, Any]:
        """
        Get status of MCP challenge deployment.

        Args:
            level_path: Path to level directory

        Returns:
            dict: Status information
        """
        challenge_id = level_path.name

        # Check container statuses
        gateway_running = self._is_container_running(self.GATEWAY_CONTAINER)
        backend_running = self._is_container_running(self.BACKEND_CONTAINER)

        return {
            "ready": gateway_running and backend_running,
            "message": self._get_status_message(gateway_running, backend_running),
            "gateway": {
                "running": gateway_running,
                "container": self.GATEWAY_CONTAINER,
                "port": self.GATEWAY_PORT,
                "url": f"http://localhost:{self.GATEWAY_PORT}/mcp"
            },
            "backend": {
                "running": backend_running,
                "container": self.BACKEND_CONTAINER,
                "challenge_id": challenge_id if backend_running else None
            }
        }

    # Docker management methods

    def _build_image(self) -> Tuple[bool, str]:
        """Build MCP Docker image."""
        try:
            # Check if image exists
            result = subprocess.run(
                ["docker", "images", "-q", "devsecops-arena-mcp"],
                capture_output=True,
                text=True
            )

            if result.stdout.strip():
                logger.info("Docker image already exists")
                return True, "Image ready"

            # Build image using docker-compose
            logger.info("Building Docker image (this may take a minute)...")
            result = subprocess.run(
                ["docker-compose", "-f", str(self.DOCKER_COMPOSE_FILE), "build"],
                cwd=str(self.arena_root),
                capture_output=True,
                text=True,
                timeout=300
            )

            if result.returncode == 0:
                return True, "Image built successfully"
            else:
                return False, f"Build failed: {result.stderr[:500]}"

        except Exception as e:
            return False, f"Build error: {e}"

    def _ensure_gateway_running(self) -> Tuple[bool, str]:
        """Ensure gateway container is running."""
        if self._is_container_running(self.GATEWAY_CONTAINER):
            return True, "Gateway already running"

        # Start gateway using docker-compose
        try:
            subprocess.run(
                ["docker-compose", "-f", str(self.DOCKER_COMPOSE_FILE), "up", "-d", "mcp-gateway"],
                cwd=str(self.arena_root),
                check=True,
                capture_output=True
            )

            # Wait for gateway to be ready
            time.sleep(3)

            if self._is_container_running(self.GATEWAY_CONTAINER):
                return True, "Gateway started"
            else:
                return False, "Gateway failed to start"

        except subprocess.CalledProcessError as e:
            return False, f"Failed to start gateway: {e.stderr.decode()[:500]}"

    def _start_backend_container(self, challenge_id: str, level_path: Path,
                                 module_name: str, port: int,
                                 config: Dict[str, Any]) -> Tuple[bool, str]:
        """Start backend container for challenge."""
        try:
            # Stop existing backend if running
            self._stop_backend_container()

            # Write runtime config
            config_file = level_path / ".server_runtime_config.json"
            with open(config_file, 'w') as f:
                json.dump({"config": config, "port": port}, f)

            # Start backend container
            # Note: No port mapping (-p) because backend is only accessible via gateway within Docker network
            result = subprocess.run(
                [
                    "docker", "run", "-d",
                    "--name", self.BACKEND_CONTAINER,
                    "--network", self.MCP_NETWORK,
                    # No -p flag - backend not exposed to host
                    "-v", f"{self.mcp_dir}/servers:/app/domains/mcp/servers:ro",
                    "-v", f"{level_path}:/app/challenge:ro",
                    "-w", "/app",
                    "-e", f"PYTHONPATH=/app",
                    "devsecops-arena-mcp:latest",
                    "python3", f"challenge/.start_server.py"
                ],
                capture_output=True,
                text=True,
                check=True
            )

            container_id = result.stdout.strip()
            logger.info(f"Backend container started: {container_id[:12]}")
            return True, f"Backend started (port {port})"

        except subprocess.CalledProcessError as e:
            return False, f"Failed to start backend: {e.stderr[:500]}"
        except Exception as e:
            return False, f"Backend start error: {e}"

    def _stop_backend_container(self):
        """Stop and remove backend container."""
        try:
            subprocess.run(
                ["docker", "rm", "-f", self.BACKEND_CONTAINER],
                capture_output=True,
                timeout=10
            )
        except Exception as e:
            logger.warning(f"Error stopping backend container: {e}")

    def _is_container_running(self, container_name: str) -> bool:
        """Check if container is running."""
        try:
            result = subprocess.run(
                ["docker", "ps", "--filter", f"name={container_name}", "--format", "{{.Names}}"],
                capture_output=True,
                text=True
            )
            return container_name in result.stdout
        except Exception:
            return False

    def _wait_for_backend_via_gateway(self, challenge_id: str, timeout: int = 30) -> bool:
        """
        Wait for backend to be healthy by checking via gateway.

        Since backend is not exposed to host, we verify registration worked
        by checking gateway status.
        """
        import requests
        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                response = requests.get(f"http://localhost:{self.GATEWAY_PORT}/status", timeout=2)
                if response.status_code == 200:
                    data = response.json()
                    active_backend = data.get("routing", {}).get("active_backend")
                    if active_backend and self.BACKEND_CONTAINER in active_backend:
                        return True
            except requests.RequestException:
                pass
            time.sleep(1)

        return False

    def _update_gateway_routing(self, challenge_id: str, backend_url: str) -> Tuple[bool, str]:
        """
        Register backend with gateway via admin API.

        Note: backend_url should use the Docker container name as hostname
        since backend is not exposed to host.
        """
        try:
            import requests

            # Use container name as hostname within Docker network
            backend_url_internal = f"http://{self.BACKEND_CONTAINER}:{backend_url.split(':')[-1]}"

            response = requests.post(
                f"http://localhost:{self.GATEWAY_PORT}/admin/register",
                json={
                    "challenge_id": challenge_id,
                    "backend_url": backend_url_internal
                },
                timeout=5
            )

            if response.status_code == 200:
                return True, f"Routing configured: {challenge_id} -> {backend_url}"
            else:
                error_msg = response.json().get("error", "Unknown error")
                return False, f"Failed to register backend: {error_msg}"

        except Exception as e:
            return False, f"Gateway routing update failed: {str(e)}"

    def _get_status_message(self, gateway_running: bool, backend_running: bool) -> str:
        """Generate status message."""
        if gateway_running and backend_running:
            return "MCP challenge ready - both containers running"
        elif gateway_running:
            return "Gateway running but no backend deployed"
        elif backend_running:
            return "Backend running but gateway is down"
        else:
            return "MCP services not running"

    def _get_setup_message(self, challenge_id: str) -> str:
        """Get setup message for client configuration."""
        return f"""🔌 MCP Gateway Ready

Gateway URL: http://localhost:{self.GATEWAY_PORT}/mcp

How to Connect:

Option 1 - Test with curl:
  curl http://localhost:{self.GATEWAY_PORT}/health

Option 2 - Use MCP Inspector:
  npx @modelcontextprotocol/inspector http://localhost:{self.GATEWAY_PORT}/mcp

Option 3 - Connect your AI client:
  URL: http://localhost:{self.GATEWAY_PORT}/mcp

📖 Full Configuration Guide: domains/mcp/CLIENT_SETUP.md

🐳 Containerized deployment - gateway and backend running in Docker
"""
