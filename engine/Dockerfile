FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    git \
    kubectl \
    docker.io \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy engine files
COPY engine/ /app/engine/

# Copy domains for challenge metadata and deployment
COPY domains/ /app/domains/

# Copy RBAC if exists
COPY rbac/ /app/rbac/ 2>/dev/null || true

# Create progress directory
RUN mkdir -p /app/data

# Expose API port
EXPOSE 5000

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV ENGINE_API_PORT=5000

# Set working directory
WORKDIR /app/engine

# Make daemon executable
RUN chmod +x daemon.py

# Health check
HEALTHCHECK --interval=10s --timeout=5s --retries=3 \
  CMD curl -f http://localhost:5000/health || exit 1

# Run the engine daemon
CMD ["python3", "daemon.py", "--port", "5000"]
