#!/usr/bin/env python3
"""
DevSecOps Arena API Server
Provides REST API for engine-visualizer communication
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import logging
from pathlib import Path
import threading
import sys

# Ensure engine module is importable
sys.path.insert(0, str(Path(__file__).parent))

app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests from visualizer

# Global reference to Arena instance
arena_instance = None
arena_lock = threading.Lock()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def set_arena_instance(arena):
    """Set the global Arena instance for API endpoints to use"""
    global arena_instance
    with arena_lock:
        arena_instance = arena


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'devsecops-arena-api'
    })


@app.route('/api/game-state', methods=['GET'])
def get_game_state():
    """Get current game state"""
    with arena_lock:
        if not arena_instance:
            return jsonify({'error': 'Arena not initialized'}), 503

        try:
            state = arena_instance.get_game_state()
            return jsonify(state)
        except Exception as e:
            logger.error(f"Error getting game state: {e}")
            return jsonify({'error': str(e)}), 500


@app.route('/api/current-level', methods=['GET'])
def get_current_level():
    """Get current level path and metadata"""
    with arena_lock:
        if not arena_instance:
            return jsonify({'error': 'Arena not initialized'}), 503

        try:
            level_path = arena_instance.get_current_level_path()
            if level_path:
                return jsonify({
                    'level_path': str(level_path),
                    'level_name': level_path.name if level_path else None
                })
            else:
                return jsonify({'level_path': None, 'level_name': None})
        except Exception as e:
            logger.error(f"Error getting current level: {e}")
            return jsonify({'error': str(e)}), 500


@app.route('/api/validate-flag', methods=['POST'])
def validate_flag():
    """Validate a flag submission"""
    with arena_lock:
        if not arena_instance:
            return jsonify({'error': 'Arena not initialized'}), 503

        try:
            data = request.get_json()
            if not data or 'flag' not in data:
                return jsonify({'error': 'Missing flag in request'}), 400

            flag = data['flag']
            level_path_str = data.get('level_path')

            # Get current level path or use provided one
            if level_path_str:
                level_path = Path(level_path_str)
            else:
                level_path = arena_instance.get_current_level_path()

            if not level_path:
                return jsonify({'error': 'No active level'}), 400

            success, message = arena_instance.validate_flag(level_path, flag)

            return jsonify({
                'success': success,
                'message': message
            })
        except Exception as e:
            logger.error(f"Error validating flag: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500


@app.route('/api/unlock-hint', methods=['POST'])
def unlock_hint():
    """Unlock a hint for the current level"""
    with arena_lock:
        if not arena_instance:
            return jsonify({'error': 'Arena not initialized'}), 503

        try:
            data = request.get_json()
            if not data or 'hint_number' not in data:
                return jsonify({'error': 'Missing hint_number in request'}), 400

            hint_number = data['hint_number']
            level_path_str = data.get('level_path')

            # Get current level path or use provided one
            if level_path_str:
                level_path = Path(level_path_str)
            else:
                level_path = arena_instance.get_current_level_path()

            if not level_path:
                return jsonify({'error': 'No active level'}), 400

            success, message, hint_content = arena_instance.unlock_hint(level_path, hint_number)

            return jsonify({
                'success': success,
                'message': message,
                'hint_content': hint_content
            })
        except Exception as e:
            logger.error(f"Error unlocking hint: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500


@app.route('/api/progress', methods=['GET'])
def get_progress():
    """Get current progress"""
    with arena_lock:
        if not arena_instance:
            return jsonify({'error': 'Arena not initialized'}), 503

        try:
            progress = arena_instance.progress
            return jsonify(progress)
        except Exception as e:
            logger.error(f"Error getting progress: {e}")
            return jsonify({'error': str(e)}), 500


def start_api_server(arena, host='0.0.0.0', port=5000, debug=False):
    """
    Start the API server

    Args:
        arena: Arena instance to expose via API
        host: Host to bind to (default: 0.0.0.0 for container access)
        port: Port to bind to (default: 5000)
        debug: Enable Flask debug mode
    """
    set_arena_instance(arena)
    logger.info(f"Starting API server on {host}:{port}")
    app.run(host=host, port=port, debug=debug, threaded=True)


if __name__ == '__main__':
    # For standalone testing
    print("API Server starting in standalone mode...")
    print("Note: Arena instance must be set via set_arena_instance()")
    app.run(host='0.0.0.0', port=5000, debug=True)
