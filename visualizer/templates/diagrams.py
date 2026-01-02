"""
Diagram templates for each K8sQuest level
Defines the architecture components and connections for visualization
"""


def get_diagram_for_level(world, level):
    """Get diagram configuration for a specific level"""

    # World 1: Core Kubernetes Basics (Levels 1-10)
    if world == 1:
        return get_world_1_diagram(level)
    # World 2: Deployments & Scaling (Levels 11-20)
    elif world == 2:
        return get_world_2_diagram(level)
    # World 3: Networking & Services (Levels 21-30)
    elif world == 3:
        return get_world_3_diagram(level)
    # World 4: Storage & Stateful Apps (Levels 31-40)
    elif world == 4:
        return get_world_4_diagram(level)
    # World 5: Security & Production Ops (Levels 41-50)
    elif world == 5:
        return get_world_5_diagram(level)
    else:
        return get_default_diagram()


def get_world_1_diagram(level):
    """World 1: Core Kubernetes Basics - Pod-focused diagrams"""

    if level <= 5:
        # Simple pod diagrams
        return {
            'title': f'World 1 - Level {level}: Pod Basics',
            'nodes': [
                {
                    'id': 'pod',
                    'type': 'pod',
                    'label': 'Pod',
                    'resource_name': None,  # Will be populated from cluster state
                    'x': 300,
                    'y': 200
                },
                {
                    'id': 'container',
                    'type': 'container',
                    'label': 'Container',
                    'parent': 'pod',
                    'x': 300,
                    'y': 250
                }
            ],
            'connections': [],
            'expected_resources': ['pods'],
            'check_patterns': [
                {'type': 'pod', 'name_pattern': '.*', 'expected_status': 'Running'}
            ]
        }
    elif level <= 8:
        # Deployment diagrams
        return {
            'title': f'World 1 - Level {level}: Deployments & Replicas',
            'nodes': [
                {
                    'id': 'deployment',
                    'type': 'deployment',
                    'label': 'Deployment',
                    'resource_name': None,
                    'x': 300,
                    'y': 100
                },
                {
                    'id': 'replicaset',
                    'type': 'replicaset',
                    'label': 'ReplicaSet',
                    'parent': 'deployment',
                    'x': 300,
                    'y': 180
                },
                {
                    'id': 'pod1',
                    'type': 'pod',
                    'label': 'Pod 1',
                    'parent': 'replicaset',
                    'x': 200,
                    'y': 280
                },
                {
                    'id': 'pod2',
                    'type': 'pod',
                    'label': 'Pod 2',
                    'parent': 'replicaset',
                    'x': 300,
                    'y': 280
                },
                {
                    'id': 'pod3',
                    'type': 'pod',
                    'label': 'Pod 3',
                    'parent': 'replicaset',
                    'x': 400,
                    'y': 280
                }
            ],
            'connections': [
                {'from': 'deployment', 'to': 'replicaset', 'label': 'manages'},
                {'from': 'replicaset', 'to': 'pod1', 'label': 'creates'},
                {'from': 'replicaset', 'to': 'pod2', 'label': 'creates'},
                {'from': 'replicaset', 'to': 'pod3', 'label': 'creates'}
            ],
            'expected_resources': ['deployments', 'pods'],
            'check_patterns': [
                {'type': 'deployment', 'name_pattern': '.*', 'expected_replicas': 3}
            ]
        }
    else:
        # Service + pods
        return {
            'title': f'World 1 - Level {level}: Services & Labels',
            'nodes': [
                {
                    'id': 'service',
                    'type': 'service',
                    'label': 'Service',
                    'resource_name': None,
                    'x': 100,
                    'y': 200
                },
                {
                    'id': 'pod1',
                    'type': 'pod',
                    'label': 'Pod 1',
                    'x': 300,
                    'y': 150
                },
                {
                    'id': 'pod2',
                    'type': 'pod',
                    'label': 'Pod 2',
                    'x': 300,
                    'y': 250
                }
            ],
            'connections': [
                {'from': 'service', 'to': 'pod1', 'label': 'routes to'},
                {'from': 'service', 'to': 'pod2', 'label': 'routes to'}
            ],
            'expected_resources': ['services', 'pods'],
            'check_patterns': [
                {'type': 'service', 'name_pattern': '.*', 'expected_endpoints': 2}
            ]
        }


def get_world_2_diagram(level):
    """World 2: Deployments & Scaling - Deployment-focused diagrams"""
    return {
        'title': f'World 2 - Level {level}: Deployments & Scaling',
        'nodes': [
            {
                'id': 'deployment',
                'type': 'deployment',
                'label': 'Deployment',
                'resource_name': None,
                'x': 300,
                'y': 100
            },
            {
                'id': 'hpa',
                'type': 'hpa',
                'label': 'HPA',
                'x': 500,
                'y': 100
            },
            {
                'id': 'replicaset-old',
                'type': 'replicaset',
                'label': 'Old ReplicaSet',
                'x': 200,
                'y': 200
            },
            {
                'id': 'replicaset-new',
                'type': 'replicaset',
                'label': 'New ReplicaSet',
                'x': 400,
                'y': 200
            },
            {
                'id': 'pods',
                'type': 'pod-group',
                'label': 'Pods',
                'count': 3,
                'x': 300,
                'y': 320
            }
        ],
        'connections': [
            {'from': 'deployment', 'to': 'replicaset-new', 'label': 'active'},
            {'from': 'deployment', 'to': 'replicaset-old', 'label': 'old revision'},
            {'from': 'hpa', 'to': 'deployment', 'label': 'scales'},
            {'from': 'replicaset-new', 'to': 'pods', 'label': 'manages'}
        ],
        'expected_resources': ['deployments', 'pods'],
        'check_patterns': [
            {'type': 'deployment', 'name_pattern': '.*', 'check_rolling_update': True}
        ]
    }


def get_world_3_diagram(level):
    """World 3: Networking & Services - Network-focused diagrams"""
    return {
        'title': f'World 3 - Level {level}: Networking & Services',
        'nodes': [
            {
                'id': 'ingress',
                'type': 'ingress',
                'label': 'Ingress',
                'x': 300,
                'y': 50
            },
            {
                'id': 'service-frontend',
                'type': 'service',
                'label': 'Frontend Service',
                'resource_name': None,
                'x': 200,
                'y': 150
            },
            {
                'id': 'service-backend',
                'type': 'service',
                'label': 'Backend Service',
                'resource_name': None,
                'x': 400,
                'y': 150
            },
            {
                'id': 'pods-frontend',
                'type': 'pod-group',
                'label': 'Frontend Pods',
                'count': 2,
                'x': 200,
                'y': 280
            },
            {
                'id': 'pods-backend',
                'type': 'pod-group',
                'label': 'Backend Pods',
                'count': 2,
                'x': 400,
                'y': 280
            },
            {
                'id': 'networkpolicy',
                'type': 'networkpolicy',
                'label': 'NetworkPolicy',
                'x': 300,
                'y': 380
            }
        ],
        'connections': [
            {'from': 'ingress', 'to': 'service-frontend', 'label': 'routes'},
            {'from': 'service-frontend', 'to': 'pods-frontend', 'label': 'load balances'},
            {'from': 'service-backend', 'to': 'pods-backend', 'label': 'load balances'},
            {'from': 'pods-frontend', 'to': 'service-backend', 'label': 'calls'},
            {'from': 'networkpolicy', 'to': 'pods-backend', 'label': 'restricts'}
        ],
        'expected_resources': ['services', 'pods', 'ingresses', 'networkpolicies'],
        'check_patterns': [
            {'type': 'service', 'name_pattern': '.*', 'expected_endpoints': '>0'},
            {'type': 'ingress', 'name_pattern': '.*', 'check_rules': True}
        ]
    }


def get_world_4_diagram(level):
    """World 4: Storage & Stateful Apps - Storage-focused diagrams"""
    return {
        'title': f'World 4 - Level {level}: Storage & StatefulSets',
        'nodes': [
            {
                'id': 'statefulset',
                'type': 'statefulset',
                'label': 'StatefulSet',
                'resource_name': None,
                'x': 300,
                'y': 100
            },
            {
                'id': 'service-headless',
                'type': 'service',
                'label': 'Headless Service',
                'resource_name': None,
                'x': 150,
                'y': 100
            },
            {
                'id': 'pod-0',
                'type': 'pod',
                'label': 'Pod-0',
                'x': 200,
                'y': 250
            },
            {
                'id': 'pod-1',
                'type': 'pod',
                'label': 'Pod-1',
                'x': 300,
                'y': 250
            },
            {
                'id': 'pod-2',
                'type': 'pod',
                'label': 'Pod-2',
                'x': 400,
                'y': 250
            },
            {
                'id': 'pvc-0',
                'type': 'pvc',
                'label': 'PVC-0',
                'x': 200,
                'y': 380
            },
            {
                'id': 'pvc-1',
                'type': 'pvc',
                'label': 'PVC-1',
                'x': 300,
                'y': 380
            },
            {
                'id': 'pvc-2',
                'type': 'pvc',
                'label': 'PVC-2',
                'x': 400,
                'y': 380
            },
            {
                'id': 'storageclass',
                'type': 'storageclass',
                'label': 'StorageClass',
                'x': 500,
                'y': 380
            }
        ],
        'connections': [
            {'from': 'statefulset', 'to': 'pod-0', 'label': 'manages'},
            {'from': 'statefulset', 'to': 'pod-1', 'label': 'manages'},
            {'from': 'statefulset', 'to': 'pod-2', 'label': 'manages'},
            {'from': 'service-headless', 'to': 'pod-0', 'label': 'DNS'},
            {'from': 'service-headless', 'to': 'pod-1', 'label': 'DNS'},
            {'from': 'service-headless', 'to': 'pod-2', 'label': 'DNS'},
            {'from': 'pod-0', 'to': 'pvc-0', 'label': 'mounts'},
            {'from': 'pod-1', 'to': 'pvc-1', 'label': 'mounts'},
            {'from': 'pod-2', 'to': 'pvc-2', 'label': 'mounts'},
            {'from': 'pvc-0', 'to': 'storageclass', 'label': 'uses'},
            {'from': 'pvc-1', 'to': 'storageclass', 'label': 'uses'},
            {'from': 'pvc-2', 'to': 'storageclass', 'label': 'uses'}
        ],
        'expected_resources': ['statefulsets', 'pods', 'pvcs', 'services'],
        'check_patterns': [
            {'type': 'statefulset', 'name_pattern': '.*', 'expected_replicas': 3},
            {'type': 'pvc', 'count': 3, 'expected_status': 'Bound'}
        ]
    }


def get_world_5_diagram(level):
    """World 5: Security & Production Ops - Complex production diagrams"""

    if level == 50:
        # The Chaos Finale - Show everything
        return {
            'title': f'World 5 - Level {level}: The Chaos Finale',
            'nodes': [
                {'id': 'ingress', 'type': 'ingress', 'label': 'Ingress', 'x': 300, 'y': 50},
                {'id': 'svc-web', 'type': 'service', 'label': 'Web Service', 'x': 200, 'y': 150},
                {'id': 'svc-api', 'type': 'service', 'label': 'API Service', 'x': 400, 'y': 150},
                {'id': 'deploy-web', 'type': 'deployment', 'label': 'Web', 'x': 200, 'y': 250},
                {'id': 'deploy-api', 'type': 'deployment', 'label': 'API', 'x': 400, 'y': 250},
                {'id': 'statefulset-db', 'type': 'statefulset', 'label': 'Database', 'x': 300, 'y': 350},
                {'id': 'configmap', 'type': 'configmap', 'label': 'ConfigMap', 'x': 100, 'y': 250},
                {'id': 'secret', 'type': 'secret', 'label': 'Secret', 'x': 100, 'y': 350},
                {'id': 'networkpolicy', 'type': 'networkpolicy', 'label': 'NetworkPolicy', 'x': 500, 'y': 350},
                {'id': 'resourcequota', 'type': 'resourcequota', 'label': 'ResourceQuota', 'x': 500, 'y': 250}
            ],
            'connections': [
                {'from': 'ingress', 'to': 'svc-web', 'label': 'routes'},
                {'from': 'svc-web', 'to': 'deploy-web', 'label': 'lb'},
                {'from': 'svc-api', 'to': 'deploy-api', 'label': 'lb'},
                {'from': 'deploy-api', 'to': 'statefulset-db', 'label': 'connects'},
                {'from': 'configmap', 'to': 'deploy-web', 'label': 'config'},
                {'from': 'secret', 'to': 'deploy-api', 'label': 'credentials'},
                {'from': 'networkpolicy', 'to': 'statefulset-db', 'label': 'protects'}
            ],
            'expected_resources': ['deployments', 'statefulsets', 'services', 'ingresses', 'networkpolicies', 'configmaps', 'secrets'],
            'check_patterns': [
                {'type': 'all', 'check_health': True}
            ]
        }
    else:
        # RBAC and security focused
        return {
            'title': f'World 5 - Level {level}: Security & RBAC',
            'nodes': [
                {'id': 'serviceaccount', 'type': 'serviceaccount', 'label': 'ServiceAccount', 'x': 150, 'y': 100},
                {'id': 'role', 'type': 'role', 'label': 'Role', 'x': 300, 'y': 100},
                {'id': 'rolebinding', 'type': 'rolebinding', 'label': 'RoleBinding', 'x': 450, 'y': 100},
                {'id': 'deployment', 'type': 'deployment', 'label': 'Deployment', 'x': 300, 'y': 220},
                {'id': 'pod', 'type': 'pod', 'label': 'Pod', 'x': 300, 'y': 320},
                {'id': 'securitycontext', 'type': 'security', 'label': 'SecurityContext', 'x': 450, 'y': 320}
            ],
            'connections': [
                {'from': 'rolebinding', 'to': 'role', 'label': 'binds'},
                {'from': 'rolebinding', 'to': 'serviceaccount', 'label': 'grants to'},
                {'from': 'deployment', 'to': 'pod', 'label': 'creates'},
                {'from': 'pod', 'to': 'serviceaccount', 'label': 'uses'},
                {'from': 'securitycontext', 'to': 'pod', 'label': 'restricts'}
            ],
            'expected_resources': ['deployments', 'pods'],
            'check_patterns': [
                {'type': 'pod', 'check_security': True}
            ]
        }


def get_default_diagram():
    """Default generic Kubernetes diagram"""
    return {
        'title': 'K8sQuest Cluster',
        'nodes': [
            {'id': 'deployment', 'type': 'deployment', 'label': 'Deployment', 'x': 300, 'y': 100},
            {'id': 'service', 'type': 'service', 'label': 'Service', 'x': 150, 'y': 200},
            {'id': 'pods', 'type': 'pod-group', 'label': 'Pods', 'count': 3, 'x': 300, 'y': 250}
        ],
        'connections': [
            {'from': 'deployment', 'to': 'pods', 'label': 'manages'},
            {'from': 'service', 'to': 'pods', 'label': 'routes to'}
        ],
        'expected_resources': ['deployments', 'services', 'pods'],
        'check_patterns': []
    }
