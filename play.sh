#!/bin/bash
# Quick launcher for K8sQuest

cd "$(dirname "$0")"

if [ ! -d "venv" ]; then
  echo "❌ Virtual environment not found. Please run ./install.sh first"
  exit 1
fi

source venv/bin/activate
python3 engine/engine.py
