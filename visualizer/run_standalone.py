#!/usr/bin/env python3
"""
Standalone Visualizer Entry Point
Runs the visualizer with API client mode (for containerized deployment)
"""

import os
import sys
from pathlib import Path

# Import API client and server
from api_client import ArenaAPIClient
from server import VisualizationServer

def main():
    """Run visualizer in standalone mode with API client"""
    # Get configuration from environment variables
    port = int(os.getenv('VISUALIZER_PORT', '8080'))
    api_url = os.getenv('ENGINE_API_URL', 'http://localhost:5000')

    print(f"🎨 Starting DevSecOps Arena Visualizer")
    print(f"   Port: {port}")
    print(f"   Engine API: {api_url}")

    # Create API client
    api_client = ArenaAPIClient(api_url=api_url)

    # Test API connection
    print(f"\n🔍 Testing connection to engine API...")
    if api_client.health_check():
        print(f"   ✅ Connected to engine API at {api_url}")
    else:
        print(f"   ⚠️  Warning: Engine API not responding at {api_url}")
        print(f"   Visualizer will start but may not function until engine is available.")

    # Start visualization server with API client
    visualizer = VisualizationServer(
        port=port,
        api_client=api_client,
        verbose=True
    )

    url = visualizer.start()
    print(f"\n✨ Visualizer running at {url}")
    print(f"   Press Ctrl+C to stop\n")

    # Keep the main thread alive
    try:
        while True:
            import time
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down visualizer...")
        visualizer.stop()

if __name__ == '__main__':
    main()
