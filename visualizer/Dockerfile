FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy visualizer files
COPY visualizer/ /app/visualizer/

# Copy domains for visualization metadata
COPY domains/ /app/domains/

# Expose visualizer port
EXPOSE 8080

# Set environment variables
ENV VISUALIZER_PORT=8080
ENV ENGINE_API_URL=http://engine:5000

# Set working directory to visualizer
WORKDIR /app/visualizer

# Make standalone entrypoint executable
RUN chmod +x run_standalone.py

# Health check
HEALTHCHECK --interval=10s --timeout=5s --retries=3 \
  CMD curl -f http://localhost:8080/ || exit 1

# Run the standalone visualizer
CMD ["python3", "run_standalone.py"]
