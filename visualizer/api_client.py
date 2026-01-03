#!/usr/bin/env python3
"""
API Client for DevSecOps Arena Engine
Handles communication with the containerized engine API
"""

import requests
import logging
from pathlib import Path
from typing import Tuple, Optional, Dict, Any

logger = logging.getLogger(__name__)


class ArenaAPIClient:
    """Client for communicating with DevSecOps Arena API"""

    def __init__(self, api_url: str = "http://localhost:5000"):
        """
        Initialize API client

        Args:
            api_url: Base URL of the Arena API server
        """
        self.api_url = api_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json'
        })

    def health_check(self) -> bool:
        """Check if API server is healthy"""
        try:
            response = self.session.get(f"{self.api_url}/health", timeout=5)
            return response.status_code == 200
        except requests.RequestException as e:
            logger.error(f"Health check failed: {e}")
            return False

    def get_game_state(self) -> Dict[str, Any]:
        """Get current game state"""
        try:
            response = self.session.get(f"{self.api_url}/api/game-state", timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to get game state: {e}")
            return {}

    def get_current_level_path(self) -> Optional[Path]:
        """Get current level path"""
        try:
            response = self.session.get(f"{self.api_url}/api/current-level", timeout=10)
            response.raise_for_status()
            data = response.json()
            level_path_str = data.get('level_path')
            if level_path_str:
                return Path(level_path_str)
            return None
        except requests.RequestException as e:
            logger.error(f"Failed to get current level: {e}")
            return None

    def validate_flag(self, level_path: Path, flag: str) -> Tuple[bool, str]:
        """
        Validate a flag submission

        Args:
            level_path: Path to the level
            flag: Flag to validate

        Returns:
            Tuple of (success, message)
        """
        try:
            payload = {
                'flag': flag,
                'level_path': str(level_path)
            }
            response = self.session.post(
                f"{self.api_url}/api/validate-flag",
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            return data.get('success', False), data.get('message', 'Unknown error')
        except requests.RequestException as e:
            logger.error(f"Failed to validate flag: {e}")
            return False, f"API error: {str(e)}"

    def unlock_hint(self, level_path: Path, hint_number: int) -> Tuple[bool, str, Optional[str]]:
        """
        Unlock a hint

        Args:
            level_path: Path to the level
            hint_number: Hint number to unlock

        Returns:
            Tuple of (success, message, hint_content)
        """
        try:
            payload = {
                'hint_number': hint_number,
                'level_path': str(level_path)
            }
            response = self.session.post(
                f"{self.api_url}/api/unlock-hint",
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            return (
                data.get('success', False),
                data.get('message', 'Unknown error'),
                data.get('hint_content')
            )
        except requests.RequestException as e:
            logger.error(f"Failed to unlock hint: {e}")
            return False, f"API error: {str(e)}", None

    def get_progress(self) -> Dict[str, Any]:
        """Get current progress"""
        try:
            response = self.session.get(f"{self.api_url}/api/progress", timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to get progress: {e}")
            return {}
