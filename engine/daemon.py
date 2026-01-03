#!/usr/bin/env python3
"""
DevSecOps Arena Engine Daemon
Runs the engine as a background service with API server for containerized deployment
"""

import sys
import signal
from pathlib import Path

# Ensure engine module is importable
sys.path.insert(0, str(Path(__file__).parent))

from engine import Arena
from api_server import start_api_server
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EngineDaemon:
    """Engine daemon for containerized deployment"""

    def __init__(self, port=5000, domain=None):
        self.port = port
        self.domain = domain
        self.arena = None
        self.running = False

    def start(self):
        """Start the engine daemon"""
        logger.info("🚀 Starting DevSecOps Arena Engine Daemon")

        # Initialize Arena instance
        logger.info(f"   Initializing Arena (domain={self.domain or 'all'})...")
        self.arena = Arena(
            enable_visualizer=False,  # Visualizer runs separately
            domain=self.domain
        )

        logger.info(f"   Arena initialized successfully")
        logger.info(f"   Current domain: {self.arena.current_domain.config.name if self.arena.current_domain else 'None'}")

        # Start API server (blocking)
        logger.info(f"\n📡 Starting API server on port {self.port}...")
        logger.info(f"   Health check: http://0.0.0.0:{self.port}/health")
        logger.info(f"   Game state: http://0.0.0.0:{self.port}/api/game-state")

        self.running = True

        # Start API server (this will block)
        try:
            start_api_server(
                arena=self.arena,
                host='0.0.0.0',
                port=self.port,
                debug=False
            )
        except KeyboardInterrupt:
            logger.info("\n\n👋 Shutting down engine daemon...")
            self.stop()

    def stop(self):
        """Stop the engine daemon"""
        self.running = False
        logger.info("Engine daemon stopped")


def signal_handler(sig, frame):
    """Handle shutdown signals"""
    logger.info(f"\n\nReceived signal {sig}, shutting down...")
    sys.exit(0)


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='DevSecOps Arena Engine Daemon')
    parser.add_argument('--port', type=int, default=5000, help='API server port (default: 5000)')
    parser.add_argument('--domain', type=str, help='Specific domain to load (optional)')

    args = parser.parse_args()

    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Start daemon
    daemon = EngineDaemon(port=args.port, domain=args.domain)
    daemon.start()


if __name__ == '__main__':
    main()
