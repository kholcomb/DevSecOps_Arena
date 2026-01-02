#!/bin/bash
# Quick launcher for K8sQuest
# Usage: ./play.sh [--no-viz] [--viz-port PORT]

cd "$(dirname "$0")"

if [ ! -d "venv" ]; then
  echo "❌ Virtual environment not found. Please run ./install.sh first"
  exit 1
fi

source venv/bin/activate
# Pass all command line arguments to engine.py
python3 engine/engine.py "$@"
