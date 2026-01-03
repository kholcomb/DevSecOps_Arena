#!/usr/bin/env python3
"""
Docker Compose Visualizer

Provides visualization data for Docker Compose-based security challenges.
Shared across all domains that use Docker Compose (Web Security, API Security, etc.).
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
import subprocess
import json
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from domains._base.visualizer import DomainVisualizer


class DockerComposeVisualizer(DomainVisualizer):
    """
    Visualizer for Docker Compose-based security challenges.

    Provides real-time information about:
    - Running Docker containers
    - Port mappings and access URLs
    - Container health status
    - Network architecture

    Used by: Web Security, API Security, and other Docker Compose-based domains.
    """

    def __init__(self, domain_config: Dict[str, Any]):
        """
        Initialize Docker Compose visualizer.

        Args:
            domain_config: Configuration from domain_config.yaml (must include 'id' and optionally 'domain_path')
        """
        super().__init__(domain_config)
        # Use domain id for dynamic prefix, default to 'web' for backwards compatibility
        domain_id = domain_config.get('id', 'web_security')
        self.domain_id = domain_id
        self.project_prefix = f"arena_{domain_id.replace('_security', '')}"

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
                'domain': self.domain_id,
                'containers': [],
                'message': 'No level deployed'
            }

        compose_file = level_path / "docker-compose.yml"
        if not compose_file.exists():
            return {
                'domain': self.domain_id,
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
                'domain': self.domain_id,
                'level': str(level_path.name),
                'project_name': project_name,
                'containers': containers,
                'ready': all_running,
                'message': 'All containers running' if all_running else 'Some containers not ready'
            }

        except subprocess.TimeoutExpired:
            return {
                'domain': self.domain_id,
                'containers': [],
                'message': 'Timeout getting container status'
            }
        except Exception as e:
            return {
                'domain': self.domain_id,
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
            Diagram configuration with nodes and connections
        """
        # Build diagram from actual running containers
        level_path = self._infer_level_path(world, level)
        viz_data = self.get_visualization_data(level_path)

        containers = viz_data.get('containers', [])

        if not containers:
            # Return a generic diagram when no containers are running
            # Format domain name for title (capitalize and remove underscores)
            domain_title = self.domain_id.replace('_', ' ').title()

            return {
                'title': f'{domain_title} Challenge',
                'nodes': [
                    {'id': 'client', 'type': 'pod', 'label': 'Browser', 'x': 150, 'y': 200},
                    {'id': 'webapp', 'type': 'service', 'label': 'Vulnerable Application', 'x': 350, 'y': 200},
                    {'id': 'database', 'type': 'pvc', 'label': 'Database', 'x': 550, 'y': 200}
                ],
                'connections': [
                    {'from': 'client', 'to': 'webapp', 'label': 'HTTP Request'},
                    {'from': 'webapp', 'to': 'database', 'label': 'Query'}
                ]
            }

        # Build diagram from actual containers
        nodes = []
        connections = []

        # Add browser/client node
        nodes.append({
            'id': 'client',
            'type': 'pod',
            'label': '🌐 Your Browser',
            'x': 100,
            'y': 200
        })

        # Add container nodes
        x_offset = 300
        for i, container in enumerate(containers):
            node_id = f"container_{i}"

            # Determine node type based on service name
            service_name = container.get('service', 'unknown').lower()
            node_type = 'service'  # Default
            if 'db' in service_name or 'database' in service_name:
                node_type = 'pvc'
            elif 'web' in service_name or 'app' in service_name:
                node_type = 'service'

            # Get URL or port info
            label = container.get('service', 'Container')
            if container.get('urls'):
                # Show first URL in label
                url = container['urls'][0]
                label = f"{label}\n{url}"

            nodes.append({
                'id': node_id,
                'type': node_type,
                'label': label,
                'resource_name': container.get('name'),
                'x': x_offset,
                'y': 200 if i == 0 else 200 + (i % 2) * 150 - 75
            })

            # Connect client to web services
            if container.get('urls') and i == 0:
                connections.append({
                    'from': 'client',
                    'to': node_id,
                    'label': 'Attack Vector'
                })

            x_offset += 200

        # Connect containers to each other if there are multiple
        if len(containers) > 1:
            for i in range(len(containers) - 1):
                connections.append({
                    'from': f"container_{i}",
                    'to': f"container_{i+1}",
                    'label': 'Internal'
                })

        # Format domain name for title (capitalize and remove underscores)
        domain_title = self.domain_id.replace('_', ' ').title()

        return {
            'title': f'{domain_title}: {level or "Challenge"}',
            'nodes': nodes,
            'connections': connections
        }

    def _infer_level_path(self, world: str, level: str) -> Optional[Path]:
        """
        Try to infer the level path from world and level identifiers.

        Args:
            world: World identifier
            level: Level identifier

        Returns:
            Path to level directory or None
        """
        if not world or not level:
            return None

        # Try to construct path
        try:
            from pathlib import Path
            # Use domain_path from config if available (for cross-domain compatibility)
            # Otherwise fall back to __file__ path (for backwards compatibility)
            base_path = self.config.get('domain_path', Path(__file__).parent)
            level_path = base_path / "worlds" / world / level

            if level_path.exists():
                return level_path
        except:
            pass

        return None

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
