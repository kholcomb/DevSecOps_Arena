# MCP Services Dockerfile
# Runs both gateway and backend challenge servers

FROM python:3.12-slim

WORKDIR /app

# Install curl for healthchecks
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better layer caching
COPY domains/mcp/requirements.txt /tmp/mcp-requirements.txt
RUN pip install --no-cache-dir -r /tmp/mcp-requirements.txt

# Copy MCP domain files
COPY domains/mcp /app/domains/mcp

# Expose ports
# 8900 - Gateway (only gateway is exposed to host)
# Backend servers are only accessible within Docker network
EXPOSE 8900

# Default command (will be overridden by docker-compose or CLI)
CMD ["python3", "domains/mcp/gateway/gateway_server.py"]
