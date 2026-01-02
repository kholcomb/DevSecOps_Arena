#!/usr/bin/env python3
"""
DevSecOps Arena Visualization Server
Provides real-time cluster state visualization with architecture diagrams
"""

import json
import subprocess
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import parse_qs, urlparse
import os


class DevSecOpsArenaVisualizerHandler(SimpleHTTPRequestHandler):
    """HTTP handler for DevSecOps Arena visualization server"""

    def __init__(self, *args, game_state_callback=None, domain_visualizer=None, current_level_path=None, **kwargs):
        self.game_state_callback = game_state_callback
        self.domain_visualizer = domain_visualizer
        self.current_level_path = current_level_path
        super().__init__(*args, **kwargs)

    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)

        # API endpoints
        if parsed_path.path == '/api/state':
            self.serve_cluster_state()
        elif parsed_path.path == '/api/level-diagram':
            self.serve_level_diagram()
        elif parsed_path.path == '/api/hints':
            self.serve_hints()
        elif parsed_path.path == '/api/solution':
            self.serve_solution()
        elif parsed_path.path == '/api/debrief':
            self.serve_debrief()
        else:
            # Serve static files
            super().do_GET()

    def serve_cluster_state(self):
        """Serve current environment state and game progress"""
        try:
            # Get game state from callback
            game_state = {}
            if self.game_state_callback:
                game_state = self.game_state_callback()

            # Get domain-specific environment state
            env_state = {}
            if self.domain_visualizer:
                # Use domain visualizer to get state
                level_path = self.current_level_path() if self.current_level_path and callable(self.current_level_path) else None
                viz_data = self.domain_visualizer.get_visualization_data(level_path)
                # Extract resources for backward compatibility with frontend
                env_state = viz_data.get('resources', {})

                # For Kubernetes, resources are nested; for other domains, adapt structure
                if 'domain' in viz_data and viz_data['domain'] != 'kubernetes':
                    # Adapt non-K8s data to a structure the frontend can display
                    env_state = self._adapt_domain_state(viz_data)
            else:
                # Fallback to K8s state if no domain visualizer (backward compatibility)
                env_state = self.get_k8s_cluster_state()

            response = {
                'game': game_state,
                'cluster': env_state,  # Keep 'cluster' key for backward compatibility
                'timestamp': subprocess.check_output(['date', '+%s']).decode().strip()
            }

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())

        except Exception as e:
            self.send_error(500, f"Error getting environment state: {str(e)}")

    def _adapt_domain_state(self, viz_data):
        """
        Adapt domain-specific visualization data to frontend structure.

        For non-Kubernetes domains (like web_security with Docker Compose),
        convert their data to a structure similar to Kubernetes for display.
        """
        adapted = {
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

        # Handle web_security domain (Docker Compose)
        if viz_data.get('domain') == 'web_security':
            containers = viz_data.get('containers', [])

            # Map containers to pods for display
            for container in containers:
                pod_info = {
                    'name': container.get('service', container.get('name', 'unknown')),
                    'status': 'Running' if container.get('status') == 'running' else 'Not Ready',
                    'ready': container.get('status') == 'running',
                    'restarts': 0,
                    'conditions': [],
                    'labels': {'domain': 'web_security'},
                    'issues': [] if container.get('status') == 'running' else [f"Container status: {container.get('status', 'unknown')}"]
                }

                # Add URL info as metadata
                if container.get('urls'):
                    pod_info['labels']['access_url'] = ', '.join(container['urls'])

                adapted['pods'].append(pod_info)

            # Add a service entry for each container with URLs
            for container in containers:
                if container.get('urls'):
                    svc_info = {
                        'name': container.get('service', container.get('name', 'unknown')),
                        'type': 'External',
                        'endpoints': len(container.get('urls', [])),
                        'ports': container.get('ports', []),
                        'issues': []
                    }
                    adapted['services'].append(svc_info)

        return adapted

    def serve_level_diagram(self):
        """Serve diagram configuration for current level"""
        try:
            game_state = {}
            if self.game_state_callback:
                game_state = self.game_state_callback()

            current_level = game_state.get('current_level', '')
            current_world = game_state.get('current_world', '')
            current_domain = game_state.get('current_domain', 'unknown')

            # Try to get diagram from domain visualizer first
            diagram_data = None
            if self.domain_visualizer:
                diagram_data = self.domain_visualizer.get_diagram_template(current_world, current_level)

            # Fallback to hardcoded templates if domain doesn't provide one
            if not diagram_data:
                # For backward compatibility, try old template system
                try:
                    # Convert world/level names to numbers for legacy system
                    world_num = self._extract_world_number(current_world)
                    level_num = self._extract_level_number(current_level)
                    diagram_data = self.get_level_diagram_template(world_num, level_num)
                except:
                    diagram_data = self._get_generic_diagram(current_domain)

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(diagram_data).encode())

        except Exception as e:
            self.send_error(500, f"Error getting diagram: {str(e)}")

    def get_k8s_cluster_state(self):
        """Query Kubernetes cluster for current state in arena namespace"""
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

        namespace = 'arena'

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

    def serve_hints(self):
        """Serve hints for current level"""
        try:
            level_path = None
            if self.current_level_path and callable(self.current_level_path):
                level_path = self.current_level_path()

            # Debug logging
            import sys
            print(f"[DEBUG] serve_hints - level_path: {level_path}", file=sys.stderr)

            if not level_path:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'hints': [], 'message': 'No level loaded'}).encode())
                return

            # Read hint files
            hints = []
            for i in range(1, 4):
                hint_file = level_path / f"hint-{i}.txt"
                if hint_file.exists():
                    with open(hint_file, 'r') as f:
                        hints.append({
                            'number': i,
                            'content': f.read().strip()
                        })

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'hints': hints}).encode())

        except Exception as e:
            self.send_error(500, f"Error getting hints: {str(e)}")

    def serve_solution(self):
        """Serve solution for current level"""
        try:
            level_path = None
            if self.current_level_path and callable(self.current_level_path):
                level_path = self.current_level_path()

            if not level_path:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'solution': '', 'message': 'No level loaded'}).encode())
                return

            # Try to read solution file (could be .yaml, .md, .txt in root or solution/ dir)
            solution_content = ''
            solution_type = 'text'

            # First check root directory
            for ext in ['yaml', 'yml', 'md', 'txt']:
                solution_file = level_path / f"solution.{ext}"
                if solution_file.exists():
                    with open(solution_file, 'r') as f:
                        solution_content = f.read()
                    solution_type = 'markdown' if ext == 'md' else 'yaml' if ext in ['yaml', 'yml'] else 'text'
                    break

            # If not found, check solution/ subdirectory
            if not solution_content:
                solution_dir = level_path / "solution"
                if solution_dir.exists() and solution_dir.is_dir():
                    for ext in ['yaml', 'yml', 'md', 'txt']:
                        solution_file = solution_dir / f"payload.{ext}"
                        if solution_file.exists():
                            with open(solution_file, 'r') as f:
                                solution_content = f.read()
                            solution_type = 'markdown' if ext == 'md' else 'yaml' if ext in ['yaml', 'yml'] else 'text'
                            break

                    # Also try just listing first file in solution dir
                    if not solution_content:
                        try:
                            solution_files = list(solution_dir.glob('*'))
                            if solution_files and solution_files[0].is_file():
                                with open(solution_files[0], 'r') as f:
                                    solution_content = f.read()
                                solution_type = 'text'
                        except:
                            pass

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({
                'solution': solution_content,
                'type': solution_type
            }).encode())

        except Exception as e:
            self.send_error(500, f"Error getting solution: {str(e)}")

    def serve_debrief(self):
        """Serve debrief/learning content for current level"""
        try:
            level_path = None
            if self.current_level_path and callable(self.current_level_path):
                level_path = self.current_level_path()

            if not level_path:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'debrief': '', 'message': 'No level loaded'}).encode())
                return

            # Read debrief file
            debrief_file = level_path / "debrief.md"
            debrief_content = ''

            if debrief_file.exists():
                with open(debrief_file, 'r') as f:
                    debrief_content = f.read()

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({
                'debrief': debrief_content,
                'type': 'markdown'
            }).encode())

        except Exception as e:
            self.send_error(500, f"Error getting debrief: {str(e)}")

    def _extract_world_number(self, world_str):
        """Extract world number from world name like 'world-1-basics' -> 1"""
        import re
        match = re.search(r'world-(\d+)', str(world_str))
        return int(match.group(1)) if match else 1

    def _extract_level_number(self, level_str):
        """Extract level number from level name like 'level-01-pods' -> 1"""
        import re
        match = re.search(r'level-(\d+)', str(level_str))
        return int(match.group(1)) if match else 1

    def _get_generic_diagram(self, domain):
        """Get a generic diagram for a domain"""
        if domain == 'web_security':
            return {
                'title': 'Web Application Architecture',
                'nodes': [
                    {'id': 'client', 'type': 'client', 'label': 'Browser', 'x': 150, 'y': 100},
                    {'id': 'webapp', 'type': 'webapp', 'label': 'Web App', 'x': 300, 'y': 200},
                    {'id': 'database', 'type': 'database', 'label': 'Database', 'x': 450, 'y': 200}
                ],
                'connections': [
                    {'from': 'client', 'to': 'webapp', 'label': 'HTTP'},
                    {'from': 'webapp', 'to': 'database', 'label': 'SQL'}
                ]
            }
        else:
            return {
                'title': 'Challenge Environment',
                'nodes': [
                    {'id': 'challenge', 'type': 'service', 'label': 'Challenge Environment', 'x': 300, 'y': 200}
                ],
                'connections': []
            }

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
    """DevSecOps Arena visualization server manager"""

    def __init__(self, port=8080, game_state_callback=None, domain_visualizer=None, current_level_path_callback=None, verbose=False):
        self.port = port
        self.game_state_callback = game_state_callback
        self.domain_visualizer = domain_visualizer
        self.current_level_path_callback = current_level_path_callback
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

        # Create handler with game state callback and domain visualizer
        def handler(*args, **kwargs):
            return DevSecOpsArenaVisualizerHandler(
                *args,
                game_state_callback=self.game_state_callback,
                domain_visualizer=self.domain_visualizer,
                current_level_path=self.current_level_path_callback,
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
    print(f"DevSecOps Arena Visualization Server running at {url}")
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
