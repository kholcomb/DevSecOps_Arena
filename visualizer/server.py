#!/usr/bin/env python3
"""
K8sQuest Visualization Server
Provides real-time cluster state visualization with architecture diagrams
"""

import json
import subprocess
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import parse_qs, urlparse
import os


class K8sQuestVisualizerHandler(SimpleHTTPRequestHandler):
    """HTTP handler for K8sQuest visualization server"""

    def __init__(self, *args, game_state_callback=None, **kwargs):
        self.game_state_callback = game_state_callback
        super().__init__(*args, **kwargs)

    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)

        # API endpoints
        if parsed_path.path == '/api/state':
            self.serve_cluster_state()
        elif parsed_path.path == '/api/level-diagram':
            self.serve_level_diagram()
        else:
            # Serve static files
            super().do_GET()

    def serve_cluster_state(self):
        """Serve current cluster state and game progress"""
        try:
            # Get game state from callback
            game_state = {}
            if self.game_state_callback:
                game_state = self.game_state_callback()

            # Get Kubernetes cluster state
            k8s_state = self.get_k8s_cluster_state()

            response = {
                'game': game_state,
                'cluster': k8s_state,
                'timestamp': subprocess.check_output(['date', '+%s']).decode().strip()
            }

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())

        except Exception as e:
            self.send_error(500, f"Error getting cluster state: {str(e)}")

    def serve_level_diagram(self):
        """Serve diagram configuration for current level"""
        try:
            game_state = {}
            if self.game_state_callback:
                game_state = self.game_state_callback()

            current_level = game_state.get('current_level', 1)
            current_world = game_state.get('current_world', 1)

            # Get diagram template for this level
            diagram_data = self.get_level_diagram_template(current_world, current_level)

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(diagram_data).encode())

        except Exception as e:
            self.send_error(500, f"Error getting diagram: {str(e)}")

    def get_k8s_cluster_state(self):
        """Query Kubernetes cluster for current state in k8squest namespace"""
        state = {
            'pods': [],
            'services': [],
            'deployments': [],
            'configmaps': [],
            'secrets': [],
            'ingresses': [],
            'networkpolicies': [],
            'pvcs': [],
            'statefulsets': []
        }

        namespace = 'k8squest'

        try:
            # Get pods with detailed status
            pods_json = subprocess.check_output(
                ['kubectl', 'get', 'pods', '-n', namespace, '-o', 'json'],
                stderr=subprocess.DEVNULL
            ).decode()
            pods_data = json.loads(pods_json)

            for pod in pods_data.get('items', []):
                pod_info = {
                    'name': pod['metadata']['name'],
                    'status': pod['status'].get('phase', 'Unknown'),
                    'ready': self.is_pod_ready(pod),
                    'restarts': sum(cs.get('restartCount', 0) for cs in pod['status'].get('containerStatuses', [])),
                    'conditions': [c['type'] for c in pod['status'].get('conditions', []) if c.get('status') == 'True'],
                    'labels': pod['metadata'].get('labels', {})
                }

                # Check for issues
                pod_info['issues'] = self.detect_pod_issues(pod)
                state['pods'].append(pod_info)

            # Get services
            svc_json = subprocess.check_output(
                ['kubectl', 'get', 'services', '-n', namespace, '-o', 'json'],
                stderr=subprocess.DEVNULL
            ).decode()
            svc_data = json.loads(svc_json)

            for svc in svc_data.get('items', []):
                svc_info = {
                    'name': svc['metadata']['name'],
                    'type': svc['spec'].get('type', 'ClusterIP'),
                    'clusterIP': svc['spec'].get('clusterIP'),
                    'ports': svc['spec'].get('ports', []),
                    'selector': svc['spec'].get('selector', {}),
                    'endpoints': self.get_service_endpoints(svc['metadata']['name'], namespace)
                }
                svc_info['issues'] = self.detect_service_issues(svc_info)
                state['services'].append(svc_info)

            # Get deployments
            deploy_json = subprocess.check_output(
                ['kubectl', 'get', 'deployments', '-n', namespace, '-o', 'json'],
                stderr=subprocess.DEVNULL
            ).decode()
            deploy_data = json.loads(deploy_json)

            for deploy in deploy_data.get('items', []):
                deploy_info = {
                    'name': deploy['metadata']['name'],
                    'replicas': deploy['spec'].get('replicas', 0),
                    'ready_replicas': deploy['status'].get('readyReplicas', 0),
                    'available_replicas': deploy['status'].get('availableReplicas', 0),
                    'labels': deploy['metadata'].get('labels', {})
                }
                deploy_info['issues'] = self.detect_deployment_issues(deploy_info)
                state['deployments'].append(deploy_info)

            # Get other resources (simplified)
            for resource_type in ['configmaps', 'secrets', 'ingresses', 'networkpolicies', 'persistentvolumeclaims', 'statefulsets']:
                try:
                    output = subprocess.check_output(
                        ['kubectl', 'get', resource_type, '-n', namespace, '-o', 'json'],
                        stderr=subprocess.DEVNULL
                    ).decode()
                    data = json.loads(output)

                    key = 'pvcs' if resource_type == 'persistentvolumeclaims' else resource_type
                    state[key] = [{'name': item['metadata']['name']} for item in data.get('items', [])]
                except:
                    pass

        except Exception as e:
            state['error'] = str(e)

        return state

    def is_pod_ready(self, pod):
        """Check if pod is ready"""
        conditions = pod['status'].get('conditions', [])
        for condition in conditions:
            if condition.get('type') == 'Ready':
                return condition.get('status') == 'True'
        return False

    def detect_pod_issues(self, pod):
        """Detect issues with a pod"""
        issues = []
        status = pod['status']

        # Check phase
        if status.get('phase') in ['Failed', 'Unknown']:
            issues.append(f"Pod in {status.get('phase')} state")

        # Check container statuses
        for cs in status.get('containerStatuses', []):
            if cs.get('state', {}).get('waiting'):
                reason = cs['state']['waiting'].get('reason', 'Unknown')
                issues.append(f"Container waiting: {reason}")

            if cs.get('restartCount', 0) > 0:
                issues.append(f"Container restarted {cs['restartCount']} times")

        # Check if pod is ready
        if not self.is_pod_ready(pod):
            issues.append("Pod not ready")

        return issues

    def detect_service_issues(self, svc_info):
        """Detect issues with a service"""
        issues = []

        if svc_info['endpoints'] == 0:
            issues.append("No endpoints - selector might not match any pods")

        if not svc_info.get('selector'):
            issues.append("No selector defined")

        return issues

    def detect_deployment_issues(self, deploy_info):
        """Detect issues with a deployment"""
        issues = []

        if deploy_info['ready_replicas'] < deploy_info['replicas']:
            issues.append(f"Only {deploy_info['ready_replicas']}/{deploy_info['replicas']} replicas ready")

        if deploy_info['replicas'] == 0:
            issues.append("Deployment scaled to 0 replicas")

        return issues

    def get_service_endpoints(self, service_name, namespace):
        """Get number of endpoints for a service"""
        try:
            output = subprocess.check_output(
                ['kubectl', 'get', 'endpoints', service_name, '-n', namespace, '-o', 'json'],
                stderr=subprocess.DEVNULL
            ).decode()
            data = json.loads(output)

            count = 0
            for subset in data.get('subsets', []):
                count += len(subset.get('addresses', []))
            return count
        except:
            return 0

    def get_level_diagram_template(self, world, level):
        """Get diagram template for specific level"""
        # Import diagram templates
        from templates.diagrams import get_diagram_for_level

        return get_diagram_for_level(world, level)

    def log_message(self, format, *args):
        """Suppress log messages unless error"""
        if self.server.verbose:
            super().log_message(format, *args)


class VisualizationServer:
    """K8sQuest visualization server manager"""

    def __init__(self, port=8080, game_state_callback=None, verbose=False):
        self.port = port
        self.game_state_callback = game_state_callback
        self.verbose = verbose
        self.server = None
        self.thread = None
        self.running = False

    def start(self):
        """Start the visualization server in a background thread"""
        if self.running:
            return

        # Change to visualizer/static directory to serve files
        os.chdir(Path(__file__).parent / 'static')

        # Create handler with game state callback
        def handler(*args, **kwargs):
            return K8sQuestVisualizerHandler(
                *args,
                game_state_callback=self.game_state_callback,
                **kwargs
            )

        self.server = HTTPServer(('localhost', self.port), handler)
        self.server.verbose = self.verbose

        # Start server in background thread
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.running = True

        return f"http://localhost:{self.port}"

    def stop(self):
        """Stop the visualization server"""
        if self.server:
            self.server.shutdown()
            self.running = False


def main():
    """Standalone server for testing"""
    server = VisualizationServer(port=8080, verbose=True)
    url = server.start()
    print(f"K8sQuest Visualization Server running at {url}")
    print("Press Ctrl+C to stop")

    try:
        while True:
            import time
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping server...")
        server.stop()


if __name__ == '__main__':
    main()
