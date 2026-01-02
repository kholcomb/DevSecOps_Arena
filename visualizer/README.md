# K8sQuest Cluster Visualizer

A real-time web-based visualization tool for the K8sQuest Kubernetes learning game. This component provides an interactive architecture diagram that shows the current state of your Kubernetes cluster and highlights issues you need to fix.

## Features

- **Real-time Cluster State**: Auto-refreshes every 3 seconds to show current pod, service, and deployment status
- **Dynamic Architecture Diagrams**: Level-specific diagrams that show the expected Kubernetes resources
- **Issue Detection**: Automatically highlights problems like crashed pods, missing endpoints, and misconfigured resources
- **Interactive Visualization**: D3.js-powered SVG diagrams with zoom and pan capabilities
- **Zero External Dependencies**: Uses Python's built-in HTTP server

## How It Works

The visualizer consists of three main components:

### 1. Backend Server (`server.py`)
- Built with Python's standard `http.server` module (zero dependencies)
- Runs in a background thread alongside the game
- Provides REST API endpoints:
  - `/api/state` - Returns current cluster state and game progress
  - `/api/level-diagram` - Returns diagram template for current level
- Queries Kubernetes cluster via `kubectl` commands
- Detects issues automatically (pod failures, service endpoint problems, etc.)

### 2. Diagram Templates (`templates/diagrams.py`)
- Defines architecture diagrams for each world and level
- Specifies nodes (pods, services, deployments, etc.) and their connections
- Customized for each learning objective:
  - **World 1**: Simple pod diagrams
  - **World 2**: Deployment and scaling diagrams
  - **World 3**: Networking and service mesh diagrams
  - **World 4**: StatefulSets and storage diagrams
  - **World 5**: Security and RBAC diagrams

### 3. Frontend (`static/`)
- **index.html**: Main visualization page
- **app.js**: D3.js-based interactive diagram rendering
- **style.css**: Retro gaming-themed styling

## Usage

### Enable Visualizer (Default)
```bash
./play.sh
```

The visualizer starts automatically and opens in your browser at `http://localhost:8080`.

### Disable Visualizer
For a more realistic, terminal-only experience:
```bash
./play.sh --no-viz
```

### Custom Port
```bash
./play.sh --viz-port 9000
```

## Architecture

```
┌─────────────────┐
│   K8sQuest      │
│   Engine        │ ← Main game loop
│   (engine.py)   │
└────────┬────────┘
         │
         ├─── game_state_callback() ──┐
         │                             │
         ▼                             ▼
┌─────────────────┐          ┌──────────────────┐
│  Visualization  │◄─────────┤  Browser Client  │
│  Server         │  HTTP    │                  │
│  (server.py)    │  ───────►│  D3.js Diagrams  │
└────────┬────────┘          └──────────────────┘
         │
         ├── kubectl commands
         │
         ▼
┌─────────────────┐
│   Kubernetes    │
│   Cluster       │
│   (kind)        │
└─────────────────┘
```

## API Endpoints

### GET /api/state
Returns current game state and cluster resources:

```json
{
  "game": {
    "total_xp": 300,
    "current_world": 1,
    "current_level": 3,
    "player_name": "K8s Explorer"
  },
  "cluster": {
    "pods": [
      {
        "name": "nginx-broken",
        "status": "CrashLoopBackOff",
        "ready": false,
        "issues": ["Container waiting: CrashLoopBackOff"]
      }
    ],
    "services": [...],
    "deployments": [...]
  }
}
```

### GET /api/level-diagram
Returns diagram configuration for the current level:

```json
{
  "title": "World 1 - Level 3: Pod Basics",
  "nodes": [
    {
      "id": "pod",
      "type": "pod",
      "label": "Pod",
      "x": 300,
      "y": 200
    }
  ],
  "connections": [],
  "expected_resources": ["pods"]
}
```

## Diagram Node Types

The visualizer supports various Kubernetes resource types with custom icons and shapes:

| Type | Icon | Shape | Description |
|------|------|-------|-------------|
| pod | 📦 | Circle | Individual pod |
| deployment | 🚀 | Rectangle | Deployment controller |
| service | ⚖️ | Rectangle | Service load balancer |
| ingress | 🌐 | Circle | Ingress controller |
| statefulset | 💾 | Cylinder | StatefulSet |
| pvc | 💿 | Cylinder | PersistentVolumeClaim |
| configmap | ⚙️ | Rectangle | ConfigMap |
| secret | 🔐 | Rectangle | Secret |
| networkpolicy | 🔒 | Circle | NetworkPolicy |

## Status Colors

- **Green** (🟢): Healthy - resource is running correctly
- **Orange** (🟡): Warning - degraded state (e.g., fewer replicas than desired)
- **Red** (🔴): Error - critical failure (e.g., CrashLoopBackOff, no endpoints)
- **Gray** (⚪): Unknown - resource not found or state unclear

## Issue Detection

The visualizer automatically detects common Kubernetes problems:

### Pod Issues
- CrashLoopBackOff / ImagePullBackOff
- Container restarts
- Not ready
- Failed or Unknown phase

### Service Issues
- No endpoints (selector mismatch)
- Missing selector

### Deployment Issues
- Replicas not ready
- Zero replicas

## Development

### Adding New Diagram Templates

Edit `visualizer/templates/diagrams.py`:

```python
def get_world_X_diagram(level):
    return {
        'title': f'World X - Level {level}: Description',
        'nodes': [
            {
                'id': 'my-node',
                'type': 'pod',
                'label': 'My Pod',
                'x': 300,
                'y': 200
            }
        ],
        'connections': [
            {'from': 'node1', 'to': 'node2', 'label': 'connects'}
        ],
        'expected_resources': ['pods', 'services']
    }
```

### Running Server Standalone

For testing:

```bash
cd visualizer
python3 server.py
```

Then open `http://localhost:8080` in your browser.

## Troubleshooting

### Server won't start
- Check if port 8080 is already in use
- Use `--viz-port` to specify a different port
- Check firewall settings

### Diagram not updating
- Verify kubectl is working: `kubectl get pods -n k8squest`
- Check browser console for JavaScript errors
- Refresh the page manually

### Blank diagram
- Ensure resources exist in k8squest namespace
- Check that the current level has a diagram template
- Verify API endpoints are responding: `curl http://localhost:8080/api/state`

## Browser Compatibility

- ✅ Chrome/Chromium (recommended)
- ✅ Firefox
- ✅ Safari
- ✅ Edge

## Performance

- Lightweight polling (3-second intervals)
- Minimal CPU usage (< 1%)
- No external API calls
- All data served from local Kubernetes cluster

## Security

- Server only listens on localhost
- No authentication required (local only)
- Read-only kubectl access
- No write operations to cluster
- No external network access

## Future Enhancements

Potential improvements:
- [ ] WebSocket support for real-time updates
- [ ] Export diagrams as SVG/PNG
- [ ] Historical state tracking
- [ ] Custom diagram editor
- [ ] Multi-cluster support
- [ ] Dark/light theme toggle
