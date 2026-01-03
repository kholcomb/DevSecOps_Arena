# DevSecOps Arena - Containerized Deployment

This guide explains how to run DevSecOps Arena in a fully containerized environment, making it OS-agnostic and easier to deploy.

## Architecture

The containerized setup consists of three main components:

```
┌─────────────────────────────────────────────────────────┐
│                    Docker Network                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Engine     │  │  Visualizer  │  │ MCP/Challenges│  │
│  │   API        │◄─┤   (Web UI)   │  │  (Backends)   │  │
│  │  (Port 5000) │  │  (Port 8080) │  │  (Dynamic)    │  │
│  └──────┬───────┘  └──────────────┘  └──────────────┘  │
└─────────┼──────────────────────────────────────────────┘
          │
     REST API
          │
    ┌─────▼──────┐
    │   Host     │
    │  (Browser) │
    └────────────┘
```

### Components

1. **Engine Container** (`devsecops-arena-engine`)
   - Runs the core game engine as a daemon
   - Exposes REST API on port 5000
   - Manages game state and progress
   - Coordinates challenge deployments

2. **Visualizer Container** (`devsecops-arena-visualizer`)
   - Provides web-based UI
   - Communicates with engine via REST API
   - Accessible at http://localhost:8080
   - Shows real-time game state and challenge status

3. **Challenge Backends** (Domain-specific)
   - MCP servers, web apps, API servers, etc.
   - Deployed dynamically by the engine
   - Isolated in separate containers

## Quick Start

### Prerequisites

- Docker Desktop or Docker Engine
- Docker Compose (v2.0+)

### Starting the Arena

```bash
# Clone the repository (if not already done)
git clone <repository-url>
cd DevSecOps_Arena

# Start containerized services
./start_containerized.sh
```

This script will:
1. Build all container images
2. Start the engine and visualizer services
3. Display service status and URLs

### Accessing the Arena

Once started, access the arena via:

- **Visualizer UI**: http://localhost:8080
- **Engine API**: http://localhost:5001
- **Health Check**: http://localhost:5001/health

## Manual Docker Compose Commands

```bash
# Build containers
docker-compose build

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f engine
docker-compose logs -f visualizer

# Stop all services
docker-compose down

# Restart a service
docker-compose restart engine

# Rebuild and restart
docker-compose up -d --build
```

## API Endpoints

The Engine API exposes the following endpoints:

### Health & Status
- `GET /health` - Health check
- `GET /api/game-state` - Current game state
- `GET /api/current-level` - Current level information
- `GET /api/progress` - Player progress

### Game Actions
- `POST /api/validate-flag` - Validate a flag submission
  ```json
  {
    "flag": "FLAG{...}",
    "level_path": "/path/to/level"  // optional
  }
  ```

- `POST /api/unlock-hint` - Unlock a hint
  ```json
  {
    "hint_number": 1,
    "level_path": "/path/to/level"  // optional
  }
  ```

## Development Workflow

### Making Changes

1. **Modify source code** on your host machine
2. **Rebuild containers**:
   ```bash
   docker-compose build
   docker-compose up -d
   ```

### Debugging

```bash
# Access engine container shell
docker exec -it devsecops-arena-engine /bin/bash

# Access visualizer container shell
docker exec -it devsecops-arena-visualizer /bin/bash

# View real-time logs
docker-compose logs -f engine

# Check container status
docker-compose ps

# Inspect container
docker inspect devsecops-arena-engine
```

## Volumes and Persistence

The setup mounts the following volumes:

- `./progress.json` → Engine container (Read/Write)
  - Player progress persists across restarts

- `./domains/` → Engine and Visualizer containers (Read-Only)
  - Challenge metadata and configurations

- `/var/run/docker.sock` → Engine container (Read-Only)
  - Allows engine to deploy challenge containers

## Troubleshooting

### Services Won't Start

```bash
# Check Docker is running
docker info

# Check for port conflicts
lsof -i :5000
lsof -i :8080

# View detailed logs
docker-compose logs engine
docker-compose logs visualizer
```

### Can't Connect to Engine API

```bash
# Test engine health
curl http://localhost:5001/health

# Check if engine is running
docker ps | grep engine

# Restart engine
docker-compose restart engine
```

### Visualizer Shows "Engine Not Available"

This means the visualizer can't connect to the engine API:

```bash
# Check engine is healthy
docker-compose ps engine

# Check network connectivity
docker exec devsecops-arena-visualizer curl http://engine:5000/health

# Restart both services
docker-compose restart
```

### Progress Not Persisting

```bash
# Check progress file exists and has correct permissions
ls -la progress.json

# Ensure progress file is mounted correctly
docker inspect devsecops-arena-engine | grep progress.json
```

## Migrating from Local Setup

If you were running the non-containerized version:

1. Your `progress.json` file will be automatically used
2. Stop any locally running instances
3. Start the containerized version
4. Your progress will be preserved

## OS Compatibility

This containerized setup works on:
- ✅ macOS (Intel & Apple Silicon)
- ✅ Linux (any distribution with Docker)
- ✅ Windows (with Docker Desktop + WSL2)

## Architecture Benefits

### Isolation
- Each component runs in its own container
- No dependency conflicts
- Clean environment management

### Portability
- Works on any OS with Docker
- Consistent behavior across platforms
- Easy to share and distribute

### Scalability
- Can run multiple instances
- Easy to add new services
- Better resource management

### Development
- Fast iteration cycles
- Easy debugging
- Separate concerns

## Next Steps

1. **Add more challenge domains** - Each domain can have its own containerized backend
2. **Implement CLI client** - Optional CLI tool that connects to the REST API
3. **Add authentication** - Secure the API with token-based auth
4. **Deploy to cloud** - Run on Kubernetes or cloud container services

## Support

For issues or questions about containerized deployment:
1. Check the logs: `docker-compose logs -f`
2. Review this documentation
3. Open an issue on GitHub
