#!/usr/bin/env python3
"""
MCP Session Manager

Manages session state for MCP connections, including session creation,
tracking, and cleanup.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, Optional
import uuid


@dataclass
class SessionState:
    """
    State for a single MCP session.

    Attributes:
        session_id: Unique session identifier (UUID)
        challenge_id: Currently active challenge for this session
        created_at: Session creation timestamp
        last_active: Last activity timestamp
        message_count: Number of messages exchanged
        metadata: Additional session metadata
    """
    session_id: str
    challenge_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    last_active: datetime = field(default_factory=datetime.now)
    message_count: int = 0
    metadata: Dict[str, any] = field(default_factory=dict)

    def touch(self):
        """Update last_active timestamp"""
        self.last_active = datetime.now()

    def increment_message_count(self):
        """Increment message counter"""
        self.message_count += 1
        self.touch()


class SessionManager:
    """
    Manages MCP sessions.

    Responsibilities:
    - Create new sessions with UUID identifiers
    - Track active sessions
    - Clean up stale sessions
    - Map sessions to active challenges
    """

    def __init__(self, session_timeout_seconds: int = 3600):
        """
        Initialize session manager.

        Args:
            session_timeout_seconds: Seconds before inactive session is cleaned up (default 1 hour)
        """
        self.sessions: Dict[str, SessionState] = {}
        self.session_timeout = timedelta(seconds=session_timeout_seconds)

    def create_session(self, challenge_id: Optional[str] = None) -> str:
        """
        Create a new session.

        Args:
            challenge_id: Optional challenge ID to associate with session

        Returns:
            str: New session ID (UUID)
        """
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = SessionState(
            session_id=session_id,
            challenge_id=challenge_id
        )
        return session_id

    def get_session(self, session_id: str) -> Optional[SessionState]:
        """
        Get session by ID.

        Args:
            session_id: Session identifier

        Returns:
            SessionState if found, None otherwise
        """
        return self.sessions.get(session_id)

    def update_session_challenge(self, session_id: str, challenge_id: str) -> bool:
        """
        Update the challenge associated with a session.

        Args:
            session_id: Session identifier
            challenge_id: New challenge identifier

        Returns:
            bool: True if updated, False if session not found
        """
        session = self.get_session(session_id)
        if session:
            session.challenge_id = challenge_id
            session.touch()
            return True
        return False

    def touch_session(self, session_id: str) -> bool:
        """
        Mark session as active (update last_active timestamp).

        Args:
            session_id: Session identifier

        Returns:
            bool: True if session exists, False otherwise
        """
        session = self.get_session(session_id)
        if session:
            session.touch()
            return True
        return False

    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session.

        Args:
            session_id: Session identifier

        Returns:
            bool: True if deleted, False if not found
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False

    def cleanup_stale_sessions(self) -> int:
        """
        Remove sessions that haven't been active within timeout period.

        Returns:
            int: Number of sessions cleaned up
        """
        now = datetime.now()
        stale_sessions = [
            session_id
            for session_id, session in self.sessions.items()
            if now - session.last_active > self.session_timeout
        ]

        for session_id in stale_sessions:
            self.delete_session(session_id)

        return len(stale_sessions)

    def get_active_session_count(self) -> int:
        """
        Get count of active sessions.

        Returns:
            int: Number of active sessions
        """
        return len(self.sessions)

    def get_sessions_by_challenge(self, challenge_id: str) -> list[SessionState]:
        """
        Get all sessions associated with a challenge.

        Args:
            challenge_id: Challenge identifier

        Returns:
            list[SessionState]: Sessions for this challenge
        """
        return [
            session
            for session in self.sessions.values()
            if session.challenge_id == challenge_id
        ]

    def get_all_sessions(self) -> Dict[str, SessionState]:
        """
        Get all active sessions.

        Returns:
            Dict mapping session_id -> SessionState
        """
        return self.sessions.copy()
