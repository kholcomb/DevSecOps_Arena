#!/bin/bash
# Quick launcher for DevSecOps Arena
# Usage: ./play.sh [OPTIONS]
#
# Options:
#   --domain DOMAIN    Select domain (kubernetes, web_security, etc.)
#   --no-viz           Disable visualization server
#   --viz-port PORT    Set visualization server port (default: 8080)
#
# Examples:
#   ./play.sh                           # Interactive domain selection
#   ./play.sh --domain kubernetes       # Pre-select kubernetes domain
#   ./play.sh --domain web_security     # Pre-select web_security domain
#   ./play.sh --no-viz                  # Disable visualization

cd "$(dirname "$0")"

if [ ! -d "venv" ]; then
  echo "❌ Virtual environment not found. Please run ./install.sh first"
  exit 1
fi

# Show help if requested
if [[ "$1" == "-h" ]] || [[ "$1" == "--help" ]]; then
  echo "DevSecOps Arena - Multi-Domain Security Training Platform"
  echo ""
  echo "Usage: ./play.sh [OPTIONS]"
  echo ""
  echo "Options:"
  echo "  --domain DOMAIN    Select domain (kubernetes, web_security, etc.)"
  echo "  --no-viz           Disable visualization server"
  echo "  --viz-port PORT    Set visualization server port (default: 8080)"
  echo "  -h, --help         Show this help message"
  echo ""
  echo "Examples:"
  echo "  ./play.sh                           # Interactive domain selection"
  echo "  ./play.sh --domain kubernetes       # Pre-select kubernetes domain"
  echo "  ./play.sh --domain web_security     # Pre-select web_security domain"
  echo "  ./play.sh --no-viz                  # Disable visualization"
  exit 0
fi

source venv/bin/activate
# Pass all command line arguments to engine.py
python3 engine/engine.py "$@"
