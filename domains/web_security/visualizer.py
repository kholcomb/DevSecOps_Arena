#!/usr/bin/env python3
"""
Web Security Visualizer

Provides visualization data for Docker Compose-based web security challenges.
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
import subprocess
import json
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from domains._base.visualizer import DomainVisualizer


class WebSecurityVisualizer(DomainVisualizer):
    """
    Visualizer for web security challenges.

    Provides real-time information about:
    - Running Docker containers
    - Port mappings and access URLs
    - Container health status
    - Network architecture
    """

    def __init__(self, domain_config: Dict[str, Any]):
        """
        Initialize web security visualizer.

        Args:
            domain_config: Configuration from domain_config.yaml
        """
        super().__init__(domain_config)
        self.project_prefix = "arena_web"

    def get_visualization_data(self, level_path: Optional[Path] = None) -> Dict[str, Any]:
        """
        Get current state data for Docker Compose visualization.

        Args:
            level_path: Optional path to current level

        Returns:
            Dictionary with container and network information
        """
        if not level_path:
            return {
                'domain': 'web_security',
                'containers': [],
                'message': 'No level deployed'
            }

        compose_file = level_path / "docker-compose.yml"
        if not compose_file.exists():
            return {
                'domain': 'web_security',
                'containers': [],
                'message': 'No docker-compose.yml found'
            }

        try:
            project_name = self._get_project_name(level_path)

            # Get container information
            result = subprocess.run(
                ["docker", "compose", "-f", str(compose_file), "-p", project_name, "ps", "--format", "json"],
                capture_output=True,
                text=True,
                timeout=10
            )

            containers = []
            if result.returncode == 0 and result.stdout.strip():
                for line in result.stdout.strip().split('\n'):
                    try:
                        container_info = json.loads(line)

                        # Extract port mappings
                        ports = []
                        urls = []
                        publishers = container_info.get('Publishers', [])
                        if publishers:
                            for pub in publishers:
                                if isinstance(pub, dict):
                                    target_port = pub.get('TargetPort', '')
                                    published_port = pub.get('PublishedPort', '')
                                    if published_port:
                                        ports.append(f"{published_port}:{target_port}")
                                        # Generate URL for common web ports
                                        if target_port in [80, 3000, 5000, 8000, 8080]:
                                            urls.append(f"http://localhost:{published_port}")

                        containers.append({
                            'name': container_info.get('Name', 'unknown'),
                            'service': container_info.get('Service', 'unknown'),
                            'status': container_info.get('State', 'unknown'),
                            'health': container_info.get('Health', 'none'),
                            'ports': ports,
                            'urls': urls
                        })
                    except json.JSONDecodeError:
                        continue

            # Determine overall status
            all_running = all(c['status'] == 'running' for c in containers) if containers else False

            return {
                'domain': 'web_security',
                'level': str(level_path.name),
                'project_name': project_name,
                'containers': containers,
                'ready': all_running,
                'message': 'All containers running' if all_running else 'Some containers not ready'
            }

        except subprocess.TimeoutExpired:
            return {
                'domain': 'web_security',
                'containers': [],
                'message': 'Timeout getting container status'
            }
        except Exception as e:
            return {
                'domain': 'web_security',
                'containers': [],
                'message': f'Error: {str(e)}'
            }

    def get_diagram_template(self, world: str, level: str) -> Optional[Dict[str, Any]]:
        """
        Get architecture diagram template for a web security level.

        Args:
            world: World identifier
            level: Level identifier

        Returns:
            Diagram configuration or None
        """
        # Simple architecture for web security challenges
        return {
            'type': 'web_application',
            'layers': ['client', 'application', 'database'],
            'description': 'Web application with intentional security vulnerabilities'
        }

    def get_quick_info(self, level_path: Optional[Path] = None) -> str:
        """
        Get quick summary of current challenge state.

        Args:
            level_path: Optional path to current level

        Returns:
            Human-readable summary string
        """
        data = self.get_visualization_data(level_path)

        if not data.get('containers'):
            return "No containers running"

        containers = data['containers']
        running_count = sum(1 for c in containers if c['status'] == 'running')

        lines = [f"Running {running_count}/{len(containers)} containers"]

        # Show access URLs
        for container in containers:
            if container.get('urls'):
                for url in container['urls']:
                    lines.append(f"  • {container['service']}: {url}")

        return "\n".join(lines)

    def _get_project_name(self, level_path: Path) -> str:
        """
        Generate Docker Compose project name from level path.

        Args:
            level_path: Path to the level directory

        Returns:
            Project name string
        """
        parts = level_path.parts
        world = parts[-2] if len(parts) >= 2 else "unknown"
        level = parts[-1] if len(parts) >= 1 else "unknown"

        # Clean up names
        world = ''.join(c if c.isalnum() or c in '-_' else '_' for c in world)
        level = ''.join(c if c.isalnum() or c in '-_' else '_' for c in level)

        return f"{self.project_prefix}_{world}_{level}".lower()


class NoOpVisualizer(DomainVisualizer):
    """
    No-op visualizer that returns minimal data.

    Use this for domains that don't need visualization.
    """

    def get_visualization_data(self, level_path: Optional[Path] = None) -> Dict[str, Any]:
        """Returns minimal data"""
        return {
            'domain': 'unknown',
            'message': 'Visualization not available'
        }

    def get_quick_info(self, level_path: Optional[Path] = None) -> str:
        """Returns minimal info"""
        return "Visualization not available for this domain"
