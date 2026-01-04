#!/bin/bash
#
# Start DevSecOps Arena in Containerized Mode
# This script starts the engine and visualizer as Docker containers
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 DevSecOps Arena - Containerized Mode${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Error: Docker is not running${NC}"
    echo -e "${YELLOW}Please start Docker and try again${NC}"
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null 2>&1; then
    echo -e "${RED}❌ Error: docker-compose not found${NC}"
    echo -e "${YELLOW}Please install docker-compose and try again${NC}"
    exit 1
fi

# Determine docker compose command
if docker compose version &> /dev/null 2>&1; then
    COMPOSE_CMD="docker compose"
else
    COMPOSE_CMD="docker-compose"
fi

echo -e "${GREEN}✓${NC} Docker is running"
echo -e "${GREEN}✓${NC} Using: $COMPOSE_CMD\n"

# Create progress.json if it doesn't exist
if [ ! -f "progress.json" ]; then
    echo -e "${YELLOW}📝 Creating progress.json...${NC}"
    echo '{"player_name": "Player", "domains": {}}' > progress.json
    echo -e "${GREEN}✓${NC} Progress file created\n"
fi

# Build and start containers
echo -e "${BLUE}🏗️  Building containers...${NC}"
$COMPOSE_CMD build

echo -e "\n${BLUE}🎮 Starting DevSecOps Arena services...${NC}"
$COMPOSE_CMD up -d

# Wait for services to be healthy
echo -e "\n${YELLOW}⏳ Waiting for services to be ready...${NC}"
sleep 5

# Check service health
echo -e "\n${BLUE}📊 Service Status:${NC}"

if docker ps | grep -q "devsecops-arena-engine.*Up"; then
    echo -e "${GREEN}✓${NC} Engine API:     http://localhost:5001"
else
    echo -e "${RED}✗${NC} Engine API:     Not running"
fi

if docker ps | grep -q "devsecops-arena-visualizer.*Up"; then
    echo -e "${GREEN}✓${NC} Visualizer:     http://localhost:8080"
else
    echo -e "${RED}✗${NC} Visualizer:     Not running"
fi

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}🎉 DevSecOps Arena is ready!${NC}"
echo -e "${GREEN}========================================${NC}\n"

echo -e "${BLUE}📖 Quick Start:${NC}"
echo -e "  1. Open visualizer: ${YELLOW}http://localhost:8080${NC}"
echo -e "  2. View logs:       ${YELLOW}$COMPOSE_CMD logs -f${NC}"
echo -e "  3. Stop services:   ${YELLOW}$COMPOSE_CMD down${NC}"
echo -e "  4. Restart:         ${YELLOW}$COMPOSE_CMD restart${NC}\n"

echo -e "${BLUE}🔍 Troubleshooting:${NC}"
echo -e "  View engine logs:      ${YELLOW}$COMPOSE_CMD logs engine${NC}"
echo -e "  View visualizer logs:  ${YELLOW}$COMPOSE_CMD logs visualizer${NC}"
echo -e "  Check API health:      ${YELLOW}curl http://localhost:5001/health${NC}\n"

# Ask if user wants to follow logs
read -p "$(echo -e ${YELLOW}Follow logs now? [y/N]:${NC} )" -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    $COMPOSE_CMD logs -f
fi
