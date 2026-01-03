# MCP Docker Deployment

## Overview

The MCP domain now uses Docker containers for easier deployment and lifecycle management. This provides:

- ✅ **Isolated environment** - No conflicts with system Python
- ✅ **Easy cleanup** - Stop containers when done, no orphan processes
- ✅ **Consistent deployment** - Same environment across all machines
- ✅ **Automatic restart** - Gateway persists across challenges

## Architecture

```
┌─────────────────────────────────────────┐
│  AI Client (Claude Desktop/Code/etc)   │
└─────────────┬───────────────────────────┘
              │ HTTP/SSE
              │
┌─────────────▼───────────────────────────┐
│  Gateway Container (port 8900)          │
│  - Persistent across challenges         │
│  - Routes requests to backends          │
│  - Session management                   │
│  - Image: devsecops-arena-mcp:1.0.0     │
└─────────────┬───────────────────────────┘
              │ HTTP
              │
┌─────────────▼───────────────────────────┐
│  Backend Container (port 9001)          │
│  - Challenge-specific vulnerable server │
│  - FastMCP SDK-based                    │
│  - Starts/stops with challenge          │
│  - Image: devsecops-arena-mcp:1.0.0     │
└─────────────────────────────────────────┘
```

## Semantic Versioning

The MCP Docker images use semantic versioning (MAJOR.MINOR.PATCH):
- **Version file**: `domains/mcp/VERSION`
- **Current version**: 1.0.0
- **Image tag**: `devsecops-arena-mcp:1.0.0`

The deployer automatically reads the version from the VERSION file and uses it for all Docker operations.

## Usage

### Default Behavior

Docker deployment is **enabled by default**. Just run:

```bash
./play.sh --domain mcp
```

The game engine will automatically:
1. Build the Docker image (first time only)
2. Start the gateway container (persistent)
3. Start the backend container for your challenge
4. Register the backend with the gateway
5. Display connection instructions

### Manual Docker Commands

If you need to manage containers manually:

```bash
# Build the image (uses version from VERSION file)
cd domains/mcp
IMAGE_TAG=$(cat VERSION) docker-compose build

# Or build with a specific version
IMAGE_TAG=1.0.0 docker-compose build

# Start gateway only
IMAGE_TAG=$(cat VERSION) docker-compose up -d mcp-gateway

# Start both gateway and backend
IMAGE_TAG=$(cat VERSION) docker-compose --profile challenge up -d

# View logs
docker-compose logs -f mcp-gateway
docker-compose logs -f mcp-backend

# Stop backend (keep gateway)
docker-compose stop mcp-backend

# Stop everything
docker-compose down

# Clean up everything including volumes
docker-compose down -v
```

### Using Non-Docker Deployment

If you prefer subprocess-based deployment (legacy):

```bash
export MCP_USE_DOCKER=false
./play.sh --domain mcp
```

## Container Management

### Gateway Container

- **Name:** `devsecops-arena-mcp-gateway`
- **Port:** 8900
- **Lifecycle:** Persistent (stays running across challenges)
- **Auto-restart:** Yes (`restart: unless-stopped`)

### Backend Container

- **Name:** `devsecops-arena-mcp-backend`
- **Port:** 9001-9010 (challenge-specific)
- **Lifecycle:** Starts/stops with challenge
- **Profile:** `challenge` (only runs when explicitly started)

### Network

- **Name:** `devsecops-arena-mcp`
- **Type:** Bridge
- **Purpose:** Allows gateway and backend to communicate

## Troubleshooting

### Docker not found

```bash
# Install Docker Desktop
# https://www.docker.com/products/docker-desktop
```

### Containers not starting

```bash
# Check Docker is running
docker info

# View container logs
docker logs devsecops-arena-mcp-gateway
docker logs devsecops-arena-mcp-backend

# Force rebuild
docker-compose build --no-cache
```

### Port conflicts

```bash
# Check what's using port 8900
lsof -i :8900

# Stop conflicting containers
docker stop $(docker ps -q --filter "publish=8900")
```

### Clean slate

```bash
# Stop all MCP containers
docker-compose down

# Remove images (check VERSION file for current version)
docker rmi devsecops-arena-mcp:$(cat domains/mcp/VERSION)

# Rebuild and start fresh
IMAGE_TAG=$(cat domains/mcp/VERSION) docker-compose -f domains/mcp/docker-compose.yml build
./play.sh --domain mcp
```

## Development

### Updating the Image

After modifying server code:

```bash
# Bump version in VERSION file if needed (MAJOR.MINOR.PATCH)
echo "1.0.1" > domains/mcp/VERSION

# Rebuild image with new version
IMAGE_TAG=$(cat domains/mcp/VERSION) docker-compose -f domains/mcp/docker-compose.yml build

# Restart containers
docker-compose down
IMAGE_TAG=$(cat domains/mcp/VERSION) docker-compose -f domains/mcp/docker-compose.yml up -d mcp-gateway
```

**Version Bumping Guidelines:**
- **MAJOR**: Breaking changes to MCP protocol or API
- **MINOR**: New features, new challenges, non-breaking changes
- **PATCH**: Bug fixes, documentation updates

### Inspecting Running Containers

```bash
# Shell into gateway
docker exec -it devsecops-arena-mcp-gateway /bin/bash

# Shell into backend
docker exec -it devsecops-arena-mcp-backend /bin/bash

# View real-time logs
docker logs -f devsecops-arena-mcp-gateway
```

## Benefits Over Subprocess Deployment

| Feature | Docker | Subprocess |
|---------|--------|------------|
| Isolation | ✅ Complete | ❌ System Python |
| Cleanup | ✅ `docker rm` | ⚠️ Manual pkill |
| Portability | ✅ Works anywhere | ⚠️ Needs Python setup |
| Orphan processes | ✅ Prevented | ❌ Can happen |
| Dependency conflicts | ✅ Isolated | ⚠️ Can conflict |
| Restart on crash | ✅ Auto-restart | ❌ Manual restart |

## Files

- `Dockerfile` - Image definition
- `docker-compose.yml` - Orchestration config
- `deployer_docker.py` - Docker-based deployer
- `requirements.txt` - Python dependencies
- `.dockerignore` - Files to exclude from image
