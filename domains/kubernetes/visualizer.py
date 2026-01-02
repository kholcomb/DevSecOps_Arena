#!/usr/bin/env python3
"""
Kubernetes Cluster Visualizer

Provides real-time K8s cluster state visualization.
Extracted from the original visualizer/server.py implementation.
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
import subprocess
import json
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from domains._base import DomainVisualizer


class K8sVisualizer(DomainVisualizer):
    """
    Visualizer for Kubernetes challenges.

    Provides real-time information about:
    - Pods (status, readiness, restarts, issues)
    - Services (endpoints, selectors)
    - Deployments (replicas, rollout status)
    - ConfigMaps and Secrets
    - NetworkPolicies
    - PVCs and StatefulSets
    """

    def __init__(self, domain_config: Dict[str, Any]):
        """Initialize K8s visualizer"""
        super().__init__(domain_config)
        self.namespace = domain_config.get('namespace', 'k8squest')

    def get_visualization_data(self, level_path: Optional[Path] = None) -> Dict[str, Any]:
        """
        Get current Kubernetes cluster state.

        Args:
            level_path: Optional path to current level

        Returns:
            Dictionary with cluster state data
        """
        return {
            'domain': 'kubernetes',
            'namespace': self.namespace,
            'resources': self._get_cluster_state(),
            'issues': self.detect_issues(),
            'resource_graph': self.get_resource_graph()
        }

    def _get_cluster_state(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Query Kubernetes cluster for current state.

        Returns:
            Dictionary of resource lists
        """
        state = {
            'pods': self._get_pods(),
            'services': self._get_services(),
            'deployments': self._get_deployments(),
            'configmaps': self._get_configmaps(),
            'secrets': self._get_secrets(),
            'networkpolicies': self._get_networkpolicies(),
            'pvcs': self._get_pvcs(),
            'statefulsets': self._get_statefulsets()
        }

        return state

    def _get_pods(self) -> List[Dict[str, Any]]:
        """Get pods in k8squest namespace"""
        try:
            result = subprocess.run(
                ['kubectl', 'get', 'pods', '-n', self.namespace, '-o', 'json'],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                return []

            data = json.loads(result.stdout)
            pods = []

            for pod in data.get('items', []):
                pod_info = {
                    'name': pod['metadata']['name'],
                    'status': pod['status'].get('phase', 'Unknown'),
                    'ready': self._is_pod_ready(pod),
                    'restarts': sum(
                        cs.get('restartCount', 0)
                        for cs in pod['status'].get('containerStatuses', [])
                    ),
                    'conditions': [
                        c['type']
                        for c in pod['status'].get('conditions', [])
                        if c.get('status') == 'True'
                    ],
                    'labels': pod['metadata'].get('labels', {}),
                    'issues': self._detect_pod_issues(pod)
                }

                pods.append(pod_info)

            return pods

        except Exception:
            return []

    def _get_services(self) -> List[Dict[str, Any]]:
        """Get services in k8squest namespace"""
        try:
            result = subprocess.run(
                ['kubectl', 'get', 'services', '-n', self.namespace, '-o', 'json'],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                return []

            data = json.loads(result.stdout)
            services = []

            for svc in data.get('items', []):
                svc_info = {
                    'name': svc['metadata']['name'],
                    'type': svc['spec'].get('type', 'ClusterIP'),
                    'clusterIP': svc['spec'].get('clusterIP'),
                    'ports': svc['spec'].get('ports', []),
                    'selector': svc['spec'].get('selector', {}),
                    'issues': []
                }

                services.append(svc_info)

            return services

        except Exception:
            return []

    def _get_deployments(self) -> List[Dict[str, Any]]:
        """Get deployments in k8squest namespace"""
        try:
            result = subprocess.run(
                ['kubectl', 'get', 'deployments', '-n', self.namespace, '-o', 'json'],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                return []

            data = json.loads(result.stdout)
            deployments = []

            for deploy in data.get('items', []):
                deploy_info = {
                    'name': deploy['metadata']['name'],
                    'replicas': deploy['spec'].get('replicas', 0),
                    'ready_replicas': deploy['status'].get('readyReplicas', 0),
                    'available_replicas': deploy['status'].get('availableReplicas', 0),
                    'updated_replicas': deploy['status'].get('updatedReplicas', 0)
                }

                deployments.append(deploy_info)

            return deployments

        except Exception:
            return []

    def _get_configmaps(self) -> List[Dict[str, Any]]:
        """Get configmaps in k8squest namespace"""
        try:
            result = subprocess.run(
                ['kubectl', 'get', 'configmaps', '-n', self.namespace, '-o', 'json'],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                return []

            data = json.loads(result.stdout)
            return [
                {'name': cm['metadata']['name']}
                for cm in data.get('items', [])
            ]

        except Exception:
            return []

    def _get_secrets(self) -> List[Dict[str, Any]]:
        """Get secrets in k8squest namespace"""
        try:
            result = subprocess.run(
                ['kubectl', 'get', 'secrets', '-n', self.namespace, '-o', 'json'],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                return []

            data = json.loads(result.stdout)
            return [
                {'name': secret['metadata']['name']}
                for secret in data.get('items', [])
            ]

        except Exception:
            return []

    def _get_networkpolicies(self) -> List[Dict[str, Any]]:
        """Get network policies in k8squest namespace"""
        try:
            result = subprocess.run(
                ['kubectl', 'get', 'networkpolicies', '-n', self.namespace, '-o', 'json'],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                return []

            data = json.loads(result.stdout)
            return [
                {'name': np['metadata']['name']}
                for np in data.get('items', [])
            ]

        except Exception:
            return []

    def _get_pvcs(self) -> List[Dict[str, Any]]:
        """Get PVCs in k8squest namespace"""
        try:
            result = subprocess.run(
                ['kubectl', 'get', 'pvc', '-n', self.namespace, '-o', 'json'],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                return []

            data = json.loads(result.stdout)
            return [
                {
                    'name': pvc['metadata']['name'],
                    'status': pvc['status'].get('phase', 'Unknown'),
                    'capacity': pvc['status'].get('capacity', {}).get('storage', 'Unknown')
                }
                for pvc in data.get('items', [])
            ]

        except Exception:
            return []

    def _get_statefulsets(self) -> List[Dict[str, Any]]:
        """Get StatefulSets in k8squest namespace"""
        try:
            result = subprocess.run(
                ['kubectl', 'get', 'statefulsets', '-n', self.namespace, '-o', 'json'],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                return []

            data = json.loads(result.stdout)
            return [
                {
                    'name': sts['metadata']['name'],
                    'replicas': sts['spec'].get('replicas', 0),
                    'ready_replicas': sts['status'].get('readyReplicas', 0)
                }
                for sts in data.get('items', [])
            ]

        except Exception:
            return []

    def _is_pod_ready(self, pod: Dict) -> bool:
        """Check if pod is ready"""
        container_statuses = pod['status'].get('containerStatuses', [])
        if not container_statuses:
            return False

        return all(cs.get('ready', False) for cs in container_statuses)

    def _detect_pod_issues(self, pod: Dict) -> List[str]:
        """Detect issues with a pod"""
        issues = []
        phase = pod['status'].get('phase', '')

        # Check phase
        if phase == 'Failed':
            issues.append('Pod has failed')
        elif phase == 'Pending':
            issues.append('Pod is pending')

        # Check container statuses
        for cs in pod['status'].get('containerStatuses', []):
            state = cs.get('state', {})

            if 'waiting' in state:
                reason = state['waiting'].get('reason', 'Unknown')
                if reason == 'CrashLoopBackOff':
                    issues.append(f'Container is in CrashLoopBackOff')
                elif reason == 'ImagePullBackOff' or reason == 'ErrImagePull':
                    issues.append(f'Cannot pull container image')
                else:
                    issues.append(f'Container waiting: {reason}')

            if 'terminated' in state:
                reason = state['terminated'].get('reason', 'Unknown')
                issues.append(f'Container terminated: {reason}')

            # Check restarts
            restarts = cs.get('restartCount', 0)
            if restarts > 5:
                issues.append(f'High restart count: {restarts}')

        return issues

    def detect_issues(self) -> List[Dict[str, Any]]:
        """
        Detect issues in the cluster.

        Returns:
            List of issue dictionaries
        """
        issues = []
        pods = self._get_pods()

        for pod in pods:
            for issue in pod.get('issues', []):
                issues.append({
                    'severity': 'error' if 'failed' in issue.lower() or 'crash' in issue.lower() else 'warning',
                    'resource': f"Pod/{pod['name']}",
                    'message': issue,
                    'hint': 'Check pod logs with: kubectl logs ' + pod['name'] + ' -n k8squest'
                })

        return issues

    def get_resource_graph(self) -> Dict[str, Any]:
        """
        Get resource relationship graph.

        Returns:
            Graph with nodes and edges
        """
        nodes = []
        edges = []

        # Add pods as nodes
        pods = self._get_pods()
        for pod in pods:
            nodes.append({
                'id': f"pod-{pod['name']}",
                'type': 'pod',
                'label': pod['name'],
                'status': pod['status'],
                'ready': pod['ready']
            })

        # Add services as nodes
        services = self._get_services()
        for svc in services:
            nodes.append({
                'id': f"svc-{svc['name']}",
                'type': 'service',
                'label': svc['name']
            })

            # Create edges from service to pods (based on selector)
            # This is simplified - full implementation would match labels
            if svc.get('selector'):
                for pod in pods:
                    edges.append({
                        'from': f"svc-{svc['name']}",
                        'to': f"pod-{pod['name']}",
                        'label': 'selects'
                    })

        # Add deployments as nodes
        deployments = self._get_deployments()
        for deploy in deployments:
            nodes.append({
                'id': f"deploy-{deploy['name']}",
                'type': 'deployment',
                'label': deploy['name']
            })

        return {
            'nodes': nodes,
            'edges': edges
        }
