#!/usr/bin/env python3
"""
Docker Compose Challenge Deployer

Handles deployment of web security challenges using Docker Compose.
"""

from pathlib import Path
from typing import Dict, Any
import subprocess
import sys
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from domains._base import ChallengeDeployer


class DockerComposeDeployer(ChallengeDeployer):
    """
    Deployer for web security challenges using Docker Compose.

    Manages:
    - Docker Compose project lifecycle
    - Container deployment and cleanup
    - Status checking
    - Network isolation
    """

    def __init__(self, domain_config: Dict[str, Any]):
        """
        Initialize docker-compose deployer.

        Args:
            domain_config: Configuration from domain_config.yaml
        """
        super().__init__(domain_config)
        self.project_prefix = "arena_web"

    def health_check(self) -> tuple[bool, str]:
        """
        Check if Docker and Docker Compose are installed and running.

        Returns:
            tuple[bool, str]: (is_healthy, status_message)
        """
        try:
            # Check if docker is installed
            result = subprocess.run(
                ["docker", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode != 0:
                return False, "Docker is not installed or not in PATH"

            # Check if Docker daemon is running
            result = subprocess.run(
                ["docker", "info"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                return False, "Docker daemon is not running. Please start Docker."

            # Check if docker-compose is available
            result = subprocess.run(
                ["docker", "compose", "version"],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode != 0:
                # Try old docker-compose command
                result = subprocess.run(
                    ["docker-compose", "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode != 0:
                    return False, "Docker Compose is not installed"

            return True, "Docker and Docker Compose are available"

        except subprocess.TimeoutExpired:
            return False, "Timeout checking Docker/Docker Compose"
        except FileNotFoundError:
            return False, "Docker command not found"
        except Exception as e:
            return False, f"Health check error: {str(e)}"

    def deploy_challenge(self, level_path: Path) -> tuple[bool, str]:
        """
        Deploy a web security challenge using Docker Compose.

        Steps:
        1. Find docker-compose.yml in level directory
        2. Stop any existing containers
        3. Start containers in detached mode
        4. Wait for containers to be healthy

        Args:
            level_path: Path to level directory containing docker-compose.yml

        Returns:
            tuple[bool, str]: (success, message)
        """
        compose_file = level_path / "docker-compose.yml"

        if not compose_file.exists():
            return False, f"docker-compose.yml not found in {level_path}"

        try:
            # Get project name from level path
            project_name = self._get_project_name(level_path)

            # Stop existing containers (if any)
            subprocess.run(
                ["docker", "compose", "-f", str(compose_file), "-p", project_name, "down", "-v"],
                capture_output=True,
                timeout=30
            )

            # Start containers
            result = subprocess.run(
                ["docker", "compose", "-f", str(compose_file), "-p", project_name, "up", "-d"],
                capture_output=True,
                text=True,
                timeout=120
            )

            if result.returncode != 0:
                return False, f"Failed to start containers: {result.stderr}"

            # Give containers a moment to initialize
            import time
            time.sleep(2)

            # Check if containers are running
            status = self.get_status(level_path)
            if not status.get('ready', False):
                return False, f"Containers started but not healthy: {status.get('message', 'Unknown error')}"

            return True, f"Challenge deployed successfully (project: {project_name})"

        except subprocess.TimeoutExpired:
            return False, "Timeout deploying challenge"
        except Exception as e:
            return False, f"Deployment error: {str(e)}"

    def cleanup_challenge(self, level_path: Path) -> tuple[bool, str]:
        """
        Clean up Docker Compose challenge environment.

        Args:
            level_path: Path to the level directory

        Returns:
            tuple[bool, str]: (success, message)
        """
        compose_file = level_path / "docker-compose.yml"

        if not compose_file.exists():
            return True, "No docker-compose.yml to clean up"

        try:
            project_name = self._get_project_name(level_path)

            # Stop and remove containers, networks, and volumes
            result = subprocess.run(
                ["docker", "compose", "-f", str(compose_file), "-p", project_name, "down", "-v"],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                return False, f"Cleanup failed: {result.stderr}"

            return True, f"Challenge cleaned up (project: {project_name})"

        except subprocess.TimeoutExpired:
            return False, "Timeout during cleanup"
        except Exception as e:
            return False, f"Cleanup error: {str(e)}"

    def get_status(self, level_path: Path) -> Dict[str, Any]:
        """
        Get current status of Docker Compose challenge containers.

        Args:
            level_path: Path to the level directory

        Returns:
            Dict with container status information
        """
        compose_file = level_path / "docker-compose.yml"

        if not compose_file.exists():
            return {
                'ready': False,
                'message': 'No docker-compose.yml found',
                'containers': []
            }

        try:
            project_name = self._get_project_name(level_path)

            # Get container status
            result = subprocess.run(
                ["docker", "compose", "-f", str(compose_file), "-p", project_name, "ps", "--format", "json"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                return {
                    'ready': False,
                    'message': 'Failed to get container status',
                    'containers': []
                }

            # Parse container info
            containers = []
            if result.stdout.strip():
                for line in result.stdout.strip().split('\n'):
                    try:
                        container_info = json.loads(line)
                        containers.append({
                            'name': container_info.get('Name', 'unknown'),
                            'status': container_info.get('State', 'unknown'),
                            'health': container_info.get('Health', 'none')
                        })
                    except json.JSONDecodeError:
                        continue

            # Check if all containers are running
            all_running = all(c['status'] == 'running' for c in containers) if containers else False

            return {
                'ready': all_running,
                'message': 'All containers running' if all_running else 'Some containers not running',
                'containers': containers
            }

        except subprocess.TimeoutExpired:
            return {
                'ready': False,
                'message': 'Timeout checking status',
                'containers': []
            }
        except Exception as e:
            return {
                'ready': False,
                'message': f'Status check error: {str(e)}',
                'containers': []
            }

    def get_deployment_files(self, level_path: Path) -> list[Path]:
        """
        Get list of Docker Compose deployment files.

        Args:
            level_path: Path to the level directory

        Returns:
            List of Path objects for deployment files
        """
        files = []
        compose_file = level_path / "docker-compose.yml"
        if compose_file.exists():
            files.append(compose_file)
        return files

    def _get_project_name(self, level_path: Path) -> str:
        """
        Generate Docker Compose project name from level path.

        Args:
            level_path: Path to the level directory

        Returns:
            Project name string
        """
        # Use world and level names for project name
        # e.g., "arena_web_world1_level01"
        parts = level_path.parts
        world = parts[-2] if len(parts) >= 2 else "unknown"
        level = parts[-1] if len(parts) >= 1 else "unknown"

        # Clean up names (remove non-alphanumeric except dash/underscore)
        world = ''.join(c if c.isalnum() or c in '-_' else '_' for c in world)
        level = ''.join(c if c.isalnum() or c in '-_' else '_' for c in level)

        return f"{self.project_prefix}_{world}_{level}".lower()
