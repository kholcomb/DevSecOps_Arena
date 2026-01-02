#!/usr/bin/env python3
"""
Domain Visualizer Abstract Base Class

Defines the interface for domain-specific visualization.
Each domain provides state data that can be rendered in the web UI.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pathlib import Path


class DomainVisualizer(ABC):
    """
    Abstract base class for domain visualization.

    Each domain implements methods to provide real-time state information
    that can be displayed in the web visualization interface.
    """

    def __init__(self, domain_config: Dict[str, Any]):
        """
        Initialize the visualizer with domain-specific configuration.

        Args:
            domain_config: Configuration dictionary from domain_config.yaml
        """
        self.config = domain_config

    @abstractmethod
    def get_visualization_data(self, level_path: Optional[Path] = None) -> Dict[str, Any]:
        """
        Get current state data for visualization.

        This should return domain-specific information about deployed resources,
        their status, relationships, and any issues detected.

        Args:
            level_path: Optional path to current level (for level-specific data)

        Returns:
            Dictionary with visualization data. Structure is domain-specific.

        Example (Kubernetes):
            >>> visualizer.get_visualization_data(level_path)
            {
                'domain': 'kubernetes',
                'resources': {
                    'pods': [
                        {
                            'name': 'nginx-broken',
                            'status': 'CrashLoopBackOff',
                            'ready': False,
                            'restarts': 5,
                            'issues': ['Container has invalid command']
                        }
                    ],
                    'services': [...],
                    'deployments': [...]
                },
                'issues': [
                    {
                        'severity': 'error',
                        'resource': 'Pod/nginx-broken',
                        'message': 'Container failing to start'
                    }
                ]
            }

        Example (Docker Compose):
            >>> visualizer.get_visualization_data(level_path)
            {
                'domain': 'web_security',
                'containers': [
                    {
                        'name': 'vulnerable-web-app',
                        'status': 'running',
                        'ports': ['3000:3000'],
                        'url': 'http://localhost:3000'
                    }
                ],
                'architecture': {
                    'layers': ['frontend', 'backend', 'database'],
                    'connections': [
                        {'from': 'frontend', 'to': 'backend', 'port': 5000}
                    ]
                }
            }
        """
        raise NotImplementedError("Subclass must implement get_visualization_data()")

    def get_diagram_template(self, world: str, level: str) -> Optional[Dict[str, Any]]:
        """
        Get architecture diagram template for a specific level.

        Override this to provide custom diagram configurations.

        Args:
            world: World identifier (e.g., "world-1-basics")
            level: Level identifier (e.g., "level-1-pods")

        Returns:
            Dictionary with diagram configuration, or None if no custom diagram

        Example:
            >>> visualizer.get_diagram_template("world-1", "level-1")
            {
                'type': 'network',
                'nodes': [
                    {'id': 'pod', 'label': 'Broken Pod', 'type': 'pod'},
                    {'id': 'node', 'label': 'Worker Node', 'type': 'node'}
                ],
                'edges': [
                    {'from': 'node', 'to': 'pod', 'label': 'schedules'}
                ]
            }
        """
        return None

    def detect_issues(self) -> List[Dict[str, Any]]:
        """
        Detect issues in the current domain state.

        Override this to implement domain-specific issue detection
        (e.g., pods not ready, containers not running, security misconfigurations).

        Returns:
            List of issue dictionaries with keys:
            - severity: 'error' | 'warning' | 'info'
            - resource: Resource identifier
            - message: Human-readable issue description

        Example:
            >>> visualizer.detect_issues()
            [
                {
                    'severity': 'error',
                    'resource': 'Pod/nginx-broken',
                    'message': 'Container is in CrashLoopBackOff state',
                    'hint': 'Check container logs with kubectl logs'
                }
            ]
        """
        return []

    def get_resource_graph(self) -> Dict[str, Any]:
        """
        Get resource relationship graph for visualization.

        Override this to provide domain-specific resource relationships.

        Returns:
            Graph structure with nodes and edges

        Example:
            >>> visualizer.get_resource_graph()
            {
                'nodes': [
                    {'id': 'deployment-1', 'type': 'deployment', 'label': 'web'},
                    {'id': 'pod-1', 'type': 'pod', 'label': 'web-abc123'}
                ],
                'edges': [
                    {'from': 'deployment-1', 'to': 'pod-1', 'label': 'manages'}
                ]
            }
        """
        return {'nodes': [], 'edges': []}


class NoOpVisualizer(DomainVisualizer):
    """
    No-op visualizer for domains without visualization support.
    """

    def get_visualization_data(self, level_path: Optional[Path] = None) -> Dict[str, Any]:
        """Return minimal visualization data"""
        return {
            'domain': self.config.get('id', 'unknown'),
            'message': 'Visualization not available for this domain',
            'resources': {}
        }
